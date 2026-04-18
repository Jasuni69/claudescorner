"""
vectordb.py — sqlite-vec + FTS5 hybrid store for all .md documents.

Architecture:
  docs          : one row per file (metadata, full body, content hash)
  doc_chunks    : N rows per doc — chunk text, section heading, token span
  vec_docs      : vec0 — chunk_id -> embedding (dense)
  fts_chunks    : FTS5 — chunk_id -> chunk text (lexical)

Retrieval is hybrid: dense (cosine) + sparse (BM25 via FTS5), fused with
reciprocal-rank fusion. Returns chunk text so callers see the actual passage
that matched, not just doc metadata.
"""
import hashlib
import json
import math
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sqlite_vec

BASE = Path(__file__).parent.parent.parent.parent  # → E:\2026\ClaudesCorner
DB_PATH = str(BASE / "core" / "vectorstore.db")
DIM = 384
CHUNK_TARGET_TOKENS = 256
CHUNK_OVERLAP_TOKENS = 64
CHUNK_MIN_TOKENS = 40
SEMANTIC_TYPES = {"memory", "core", "skill", "agent", "digested", "project", "root", "cert"}
EPISODIC_TYPES = {"daily_log", "inbox", "research", "journal"}
RECENCY_HALF_LIFE_DAYS = 45.0  # episodic score halves every 45d; tune as needed
DEPRECATED_WEIGHT = 0.35       # soft down-weight instead of hard filter
RRF_K = 60                     # standard RRF constant
SOUL_BIAS_ALPHA = 0.12         # max bias weight; scaled down for long queries
SOUL_BIAS_MAX_TOKENS = 8       # above this, bias decays to ~0
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # ~80MB, lazy-loaded
RERANK_POOL = 20               # chunks fed to cross-encoder per search

_reranker = None


def _get_reranker():
    """Lazy-load the cross-encoder. Returns None if unavailable; caller falls back."""
    global _reranker
    if _reranker is False:
        return None
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder(RERANK_MODEL, max_length=256)
        except Exception:
            _reranker = False
            return None
    return _reranker


# ── Connection singleton ─────────────────────────────────────────────────────

_conn_local = threading.local()


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    cached = getattr(_conn_local, "conn", None)
    cached_path = getattr(_conn_local, "path", None)
    if cached is not None and cached_path == db_path:
        return cached

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS docs (
            id          TEXT PRIMARY KEY,
            path        TEXT NOT NULL,
            rel_path    TEXT NOT NULL,
            doc_type    TEXT NOT NULL,
            name        TEXT NOT NULL,
            title       TEXT NOT NULL,
            description TEXT NOT NULL,
            body        TEXT NOT NULL,
            tags        TEXT NOT NULL DEFAULT '[]',
            status      TEXT NOT NULL DEFAULT 'active',
            author      TEXT NOT NULL DEFAULT '',
            mtime       REAL NOT NULL,
            content_sha TEXT NOT NULL DEFAULT '',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_docs_type   ON docs(doc_type);
        CREATE INDEX IF NOT EXISTS idx_docs_status ON docs(status);

        CREATE TABLE IF NOT EXISTS doc_chunks (
            id          TEXT PRIMARY KEY,
            doc_id      TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            section     TEXT NOT NULL DEFAULT '',
            text        TEXT NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES docs(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_chunks_doc ON doc_chunks(doc_id);

        CREATE VIRTUAL TABLE IF NOT EXISTS vec_docs USING vec0(
            id        TEXT PRIMARY KEY,
            embedding FLOAT[384]
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
            id UNINDEXED,
            text,
            tokenize = 'porter unicode61'
        );
    """)
    # Schema migration: ensure content_sha exists on pre-existing DBs
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(docs)")}
    if "content_sha" not in cols:
        conn.execute("ALTER TABLE docs ADD COLUMN content_sha TEXT NOT NULL DEFAULT ''")
    conn.commit()
    _conn_local.conn = conn
    _conn_local.path = db_path
    return conn


def close_connection() -> None:
    conn = getattr(_conn_local, "conn", None)
    if conn is not None:
        conn.close()
        _conn_local.conn = None
        _conn_local.path = None


# ── Identity helpers ─────────────────────────────────────────────────────────

def _doc_id(path: str) -> str:
    return hashlib.sha1(path.encode()).hexdigest()[:16]


def _chunk_id(doc_id: str, chunk_index: int) -> str:
    return f"{doc_id}:{chunk_index}"


def _content_sha(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8", errors="ignore")).hexdigest()[:16]


# ── Markdown-aware chunking ──────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
_CODE_FENCE_RE = re.compile(r"^```")

# Lazy tokenizer; falls back to whitespace count if unavailable.
_tokenizer = None

def _token_len(text: str) -> int:
    global _tokenizer
    if _tokenizer is None:
        try:
            from transformers import AutoTokenizer
            _tokenizer = AutoTokenizer.from_pretrained(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception:
            _tokenizer = False  # sentinel: unavailable
    if _tokenizer and _tokenizer is not False:
        return len(_tokenizer.encode(text, add_special_tokens=False))
    return len(text.split())


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Split markdown by headings. Returns [(section_heading, section_text), ...].
    Respects code fences (headings inside ``` are not treated as section breaks).
    """
    lines = body.splitlines()
    sections: list[tuple[str, list[str]]] = [("", [])]
    in_fence = False
    for line in lines:
        if _CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            sections[-1][1].append(line)
            continue
        if not in_fence:
            m = _HEADING_RE.match(line)
            if m:
                sections.append((m.group(2).strip(), []))
                continue
        sections[-1][1].append(line)
    return [(h, "\n".join(body_lines).strip()) for h, body_lines in sections if body_lines]


def _pack_paragraphs(section_text: str, target: int, overlap: int,
                     min_tokens: int) -> list[str]:
    """Greedy-pack paragraphs into <= target-token chunks with token overlap."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", section_text) if p.strip()]
    if not paragraphs:
        return []
    chunks: list[str] = []
    buf: list[str] = []
    buf_tokens = 0
    for para in paragraphs:
        pt = _token_len(para)
        if pt > target:
            # Flush current buffer
            if buf:
                chunks.append("\n\n".join(buf))
                buf, buf_tokens = [], 0
            # Oversized paragraph — split on sentences, then fall back to words
            sentences = re.split(r"(?<=[.!?])\s+", para)
            sbuf: list[str] = []
            sbuf_tokens = 0
            for s in sentences:
                st = _token_len(s)
                if sbuf_tokens + st > target and sbuf:
                    chunks.append(" ".join(sbuf))
                    # Carry overlap
                    carry, ct = [], 0
                    for x in reversed(sbuf):
                        xt = _token_len(x)
                        if ct + xt > overlap:
                            break
                        carry.insert(0, x)
                        ct += xt
                    sbuf, sbuf_tokens = carry[:], ct
                sbuf.append(s)
                sbuf_tokens += st
            if sbuf:
                chunks.append(" ".join(sbuf))
            continue
        if buf_tokens + pt > target and buf:
            chunks.append("\n\n".join(buf))
            # Overlap: keep trailing paragraphs up to overlap tokens
            carry, ct = [], 0
            for x in reversed(buf):
                xt = _token_len(x)
                if ct + xt > overlap:
                    break
                carry.insert(0, x)
                ct += xt
            buf, buf_tokens = carry[:], ct
        buf.append(para)
        buf_tokens += pt
    if buf:
        tail = "\n\n".join(buf)
        if chunks and _token_len(tail) < min_tokens:
            chunks[-1] = chunks[-1] + "\n\n" + tail
        else:
            chunks.append(tail)
    return chunks


def _split_chunks(body: str, target: int = CHUNK_TARGET_TOKENS,
                  overlap: int = CHUNK_OVERLAP_TOKENS,
                  min_tokens: int = CHUNK_MIN_TOKENS) -> list[tuple[str, str]]:
    """Return [(section_heading, chunk_text), ...]. Empty body → one empty chunk."""
    body = body.strip()
    if not body:
        return [("", "")]
    out: list[tuple[str, str]] = []
    for heading, section_text in _split_sections(body):
        section_with_h = (f"# {heading}\n\n{section_text}" if heading else section_text)
        for chunk in _pack_paragraphs(section_with_h, target, overlap, min_tokens):
            out.append((heading, chunk))
    return out or [("", body)]


# ── Upsert / delete / deprecate ──────────────────────────────────────────────

def _purge_chunks(conn: sqlite3.Connection, doc_id: str) -> None:
    conn.execute("DELETE FROM doc_chunks WHERE doc_id=?", (doc_id,))
    rows = conn.execute(
        "SELECT id FROM vec_docs WHERE id LIKE ?", (f"{doc_id}:%",)
    ).fetchall()
    for r in rows:
        conn.execute("DELETE FROM vec_docs WHERE id=?", (r["id"],))
    conn.execute("DELETE FROM vec_docs WHERE id=?", (doc_id,))  # legacy
    conn.execute("DELETE FROM fts_chunks WHERE id LIKE ?", (f"{doc_id}:%",))
    conn.execute("DELETE FROM fts_chunks WHERE id=?", (doc_id,))


def upsert(db_path: str = DB_PATH, *, path: str, rel_path: str, doc_type: str,
           name: str, title: str, description: str, body: str,
           tags: list[str], mtime: float, embedding: list[float] | None = None,
           status: str = "active", author: str = "") -> None:
    """Single-doc upsert; embeds chunks internally. Heavier than upsert_with_chunks."""
    doc_id = _doc_id(path)
    now = datetime.now(timezone.utc).isoformat()
    sha = _content_sha(body)
    conn = get_connection(db_path)

    conn.execute("""
        INSERT INTO docs (id, path, rel_path, doc_type, name, title, description,
                          body, tags, status, author, mtime, content_sha,
                          created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            rel_path=excluded.rel_path, doc_type=excluded.doc_type,
            name=excluded.name, title=excluded.title,
            description=excluded.description, body=excluded.body,
            tags=excluded.tags, status=excluded.status,
            author=excluded.author, mtime=excluded.mtime,
            content_sha=excluded.content_sha,
            updated_at=excluded.updated_at
    """, (doc_id, path, rel_path, doc_type, name, title, description,
          body, json.dumps(tags), status, author, mtime, sha, now, now))
    _purge_chunks(conn, doc_id)
    conn.commit()

    # Embed chunks (sentence-transformers is heavy; import lazily)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    chunk_pairs = _split_chunks(body)
    texts = [c[1] for c in chunk_pairs]
    vecs = model.encode(texts, show_progress_bar=False)

    _write_chunks(conn, doc_id, chunk_pairs, [v.tolist() for v in vecs])
    conn.commit()


def upsert_with_chunks(db_path: str = DB_PATH, *, path: str, rel_path: str, doc_type: str,
                       name: str, title: str, description: str, body: str,
                       tags: list[str], mtime: float,
                       chunk_embeddings: list[list[float]],
                       chunk_pairs: list[tuple[str, str]] | None = None,
                       status: str = "active", author: str = "") -> None:
    """Batch-friendly variant: caller pre-computes chunks + embeddings.

    If chunk_pairs is None (legacy callers), recompute chunks from body.
    Must match len(chunk_embeddings).
    """
    doc_id = _doc_id(path)
    now = datetime.now(timezone.utc).isoformat()
    sha = _content_sha(body)
    conn = get_connection(db_path)

    conn.execute("""
        INSERT INTO docs (id, path, rel_path, doc_type, name, title, description,
                          body, tags, status, author, mtime, content_sha,
                          created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            rel_path=excluded.rel_path, doc_type=excluded.doc_type,
            name=excluded.name, title=excluded.title,
            description=excluded.description, body=excluded.body,
            tags=excluded.tags, status=excluded.status,
            author=excluded.author, mtime=excluded.mtime,
            content_sha=excluded.content_sha,
            updated_at=excluded.updated_at
    """, (doc_id, path, rel_path, doc_type, name, title, description,
          body, json.dumps(tags), status, author, mtime, sha, now, now))
    _purge_chunks(conn, doc_id)

    if chunk_pairs is None:
        chunk_pairs = _split_chunks(body)
    if len(chunk_pairs) != len(chunk_embeddings):
        raise ValueError(
            f"chunk_pairs/embeddings length mismatch: "
            f"{len(chunk_pairs)} vs {len(chunk_embeddings)}"
        )

    _write_chunks(conn, doc_id, chunk_pairs, chunk_embeddings)
    conn.commit()


def _write_chunks(conn: sqlite3.Connection, doc_id: str,
                  chunk_pairs: list[tuple[str, str]],
                  embeddings: list[list[float]]) -> None:
    for i, ((section, text), vec) in enumerate(zip(chunk_pairs, embeddings)):
        cid = _chunk_id(doc_id, i)
        conn.execute(
            "INSERT INTO doc_chunks (id, doc_id, chunk_index, section, text) "
            "VALUES (?,?,?,?,?)",
            (cid, doc_id, i, section, text),
        )
        conn.execute(
            "INSERT INTO vec_docs (id, embedding) VALUES (?,?)",
            (cid, sqlite_vec.serialize_float32(vec)),
        )
        conn.execute(
            "INSERT INTO fts_chunks (id, text) VALUES (?,?)", (cid, text)
        )


def delete(db_path: str = DB_PATH, *, path: str) -> None:
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    _purge_chunks(conn, doc_id)
    conn.execute("DELETE FROM docs WHERE id=?", (doc_id,))
    conn.commit()


def deprecate(db_path: str = DB_PATH, *, path: str, reason: str = "") -> None:
    doc_id = _doc_id(path)
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(db_path)
    conn.execute(
        "UPDATE docs SET status='deprecated', updated_at=? WHERE id=?",
        (now, doc_id),
    )
    conn.commit()


# ── Retrieval: hybrid dense + FTS5 with RRF fusion ───────────────────────────

def _soul_bias_weight(query: str) -> float:
    """Scale soul bias down as query gets longer/more specific."""
    toks = len(query.split())
    if toks <= 1:
        return SOUL_BIAS_ALPHA
    if toks >= SOUL_BIAS_MAX_TOKENS:
        return 0.0
    # Linear decay: 1 token → full alpha; SOUL_BIAS_MAX_TOKENS → 0.
    frac = max(0.0, 1.0 - (toks - 1) / (SOUL_BIAS_MAX_TOKENS - 1))
    return SOUL_BIAS_ALPHA * frac


def _fts_sanitize(query: str) -> str:
    """Turn free text into FTS5 MATCH-safe disjunction of terms."""
    toks = re.findall(r"[A-Za-z0-9_]{2,}", query)
    if not toks:
        return ""
    # Quote each term to avoid operator collisions; OR-join for recall.
    return " OR ".join(f'"{t}"' for t in toks)


def _dense_search(conn: sqlite3.Connection, q_vec, top_k: int) -> list[tuple[str, float]]:
    import numpy as np
    vec_bytes = sqlite_vec.serialize_float32(q_vec.tolist())
    rows = conn.execute("""
        SELECT id, embedding,
               vec_distance_cosine(embedding, ?) AS dist
        FROM vec_docs
        ORDER BY dist
        LIMIT ?
    """, (vec_bytes, top_k)).fetchall()
    results: list[tuple[str, float]] = []
    for r in rows:
        doc_vec = np.frombuffer(r["embedding"], dtype="float32")
        norm = doc_vec / (np.linalg.norm(doc_vec) + 1e-9)
        score = float(np.dot(q_vec, norm))
        results.append((r["id"], score))
    return results


def _sparse_search(conn: sqlite3.Connection, query: str, top_k: int) -> list[tuple[str, float]]:
    fts_query = _fts_sanitize(query)
    if not fts_query:
        return []
    try:
        rows = conn.execute("""
            SELECT id, bm25(fts_chunks) AS score
            FROM fts_chunks
            WHERE fts_chunks MATCH ?
            ORDER BY score
            LIMIT ?
        """, (fts_query, top_k)).fetchall()
    except sqlite3.OperationalError:
        return []
    # bm25 is "lower = better" in FTS5; flip sign so higher is better.
    return [(r["id"], -float(r["score"])) for r in rows]


def _rrf_fuse(dense: list[tuple[str, float]],
              sparse: list[tuple[str, float]], k: int = RRF_K) -> dict[str, float]:
    """Reciprocal rank fusion: score = sum(1/(k+rank_i)) over source lists."""
    rrf: dict[str, float] = {}
    for rank, (cid, _) in enumerate(dense, 1):
        rrf[cid] = rrf.get(cid, 0.0) + 1.0 / (k + rank)
    for rank, (cid, _) in enumerate(sparse, 1):
        rrf[cid] = rrf.get(cid, 0.0) + 1.0 / (k + rank)
    return rrf


def search(db_path: str = DB_PATH, *, query_embedding: list[float],
           query: str = "", top_k: int = 8, doc_type: str | None = None,
           status: str | None = "active",
           soul_bias: list[float] | None = None,
           include_deprecated: bool = False,
           rerank: bool = True) -> list[dict[str, Any]]:
    """Hybrid retrieval. Returns one result per doc — best chunk wins —
    with the matching chunk text included.

    Backward-compatible: existing callers passing only `query_embedding` still
    work (sparse pass becomes a no-op when `query` is empty).
    """
    import numpy as np

    q = np.array(query_embedding, dtype="float32")
    if soul_bias is not None and query:
        w = _soul_bias_weight(query)
        if w > 0:
            s = np.array(soul_bias, dtype="float32")
            q = (1.0 - w) * q + w * s
    q = q / (np.linalg.norm(q) + 1e-9)

    conn = get_connection(db_path)

    # Pull a wide candidate pool — fusion + doc-dedup shrinks it.
    pool = max(top_k * 20, 60)
    dense = _dense_search(conn, q, pool)
    sparse = _sparse_search(conn, query, pool) if query else []

    if not dense and not sparse:
        return []

    fused = _rrf_fuse(dense, sparse)
    dense_scores = {cid: sc for cid, sc in dense}

    # Optional cross-encoder rerank on top-N fused chunks.
    # Replaces rrf score with a normalized rerank score for those chunks only.
    if rerank and query:
        ranker = _get_reranker()
        if ranker is not None:
            top_ids = [cid for cid, _ in sorted(
                fused.items(), key=lambda kv: -kv[1])[:RERANK_POOL]]
            if top_ids:
                ph = ",".join("?" * len(top_ids))
                rows = conn.execute(
                    f"SELECT id, text FROM doc_chunks WHERE id IN ({ph})", top_ids,
                ).fetchall()
                id_text = {r["id"]: r["text"] for r in rows}
                pairs = [(query, id_text[cid]) for cid in top_ids if cid in id_text]
                if pairs:
                    import numpy as np
                    scores = ranker.predict(pairs, show_progress_bar=False)
                    # Min-max normalize into roughly same range as rrf
                    s = np.array(scores, dtype="float32")
                    lo, hi = float(s.min()), float(s.max())
                    span = (hi - lo) or 1.0
                    rrf_vals = [fused[cid] for cid in top_ids if cid in id_text]
                    rrf_hi = max(rrf_vals) if rrf_vals else 1.0
                    for cid, raw in zip([c for c in top_ids if c in id_text], s):
                        fused[cid] = float((raw - lo) / span) * rrf_hi

    # Group chunk_id → (doc_id, best_rrf, best_cosine, chunk_idx)
    doc_best: dict[str, dict] = {}
    for cid, rrf_score in fused.items():
        doc_id = cid.split(":", 1)[0]
        entry = doc_best.get(doc_id)
        if entry is None or rrf_score > entry["rrf"]:
            doc_best[doc_id] = {
                "chunk_id": cid,
                "rrf": rrf_score,
                "cosine": dense_scores.get(cid, 0.0),
            }

    if not doc_best:
        return []

    ids = list(doc_best.keys())
    placeholders = ",".join("?" * len(ids))
    status_clause = ""
    params: list = list(ids)
    if doc_type:
        status_clause += " AND doc_type=?"
        params.append(doc_type)
    if status and not include_deprecated:
        status_clause += " AND status=?"
        params.append(status)

    docs = conn.execute(
        f"SELECT id, path, rel_path, doc_type, name, title, description, "
        f"       tags, mtime, status "
        f"FROM docs WHERE id IN ({placeholders}){status_clause}",
        params,
    ).fetchall()

    # Fetch chunk text + section for each winning chunk in one query
    chunk_ids = [doc_best[d["id"]]["chunk_id"] for d in docs]
    chunk_text_map: dict[str, tuple[str, str]] = {}
    if chunk_ids:
        ph = ",".join("?" * len(chunk_ids))
        for row in conn.execute(
            f"SELECT id, section, text FROM doc_chunks WHERE id IN ({ph})",
            chunk_ids,
        ):
            chunk_text_map[row["id"]] = (row["section"], row["text"])

    now_ts = datetime.now(timezone.utc).timestamp()
    results = []
    for d in docs:
        info = doc_best[d["id"]]
        base = info["rrf"]

        # Episodic recency via exponential half-life (additive-style bonus,
        # implemented as multiplicative factor on rrf score).
        if d["doc_type"] in EPISODIC_TYPES:
            days_old = max(0.0, (now_ts - d["mtime"]) / 86400)
            decay = 0.5 ** (days_old / RECENCY_HALF_LIFE_DAYS)
            # Keep a floor so ancient-but-relevant episodic still surfaces.
            recency = 0.35 + 0.65 * decay
            base *= recency

        if d["status"] == "deprecated":
            base *= DEPRECATED_WEIGHT

        section, chunk_text = chunk_text_map.get(info["chunk_id"], ("", ""))
        results.append({
            "id": d["id"],
            "path": d["path"],
            "rel_path": d["rel_path"],
            "doc_type": d["doc_type"],
            "name": d["name"],
            "title": d["title"],
            "description": d["description"],
            "tags": json.loads(d["tags"]),
            "status": d["status"],
            "section": section,
            "chunk": chunk_text,
            "score": round(base, 6),
            "cosine": round(info["cosine"], 4),
        })

    return sorted(results, key=lambda x: -x["score"])[:top_k]


# ── Utility reads ────────────────────────────────────────────────────────────

def fetch_body(db_path: str = DB_PATH, *, path: str) -> str | None:
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    row = conn.execute("SELECT body FROM docs WHERE id=?", (doc_id,)).fetchone()
    return row["body"] if row else None


def fetch_chunks(db_path: str = DB_PATH, *, path: str) -> list[dict]:
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT chunk_index, section, text FROM doc_chunks "
        "WHERE doc_id=? ORDER BY chunk_index", (doc_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def count(db_path: str = DB_PATH, doc_type: str | None = None,
          status: str | None = None) -> int:
    conn = get_connection(db_path)
    q = "SELECT COUNT(*) FROM docs WHERE 1=1"
    params: list = []
    if doc_type:
        q += " AND doc_type=?"
        params.append(doc_type)
    if status:
        q += " AND status=?"
        params.append(status)
    return conn.execute(q, params).fetchone()[0]


def list_docs(db_path: str = DB_PATH, doc_type: str | None = None,
              status: str = "active", limit: int = 100) -> list[dict]:
    conn = get_connection(db_path)
    q = ("SELECT id, rel_path, doc_type, name, title, description, tags, status, "
         "       updated_at FROM docs WHERE status=?")
    params: list = [status]
    if doc_type:
        q += " AND doc_type=?"
        params.append(doc_type)
    q += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]


def content_sha(db_path: str = DB_PATH, *, path: str) -> str | None:
    """Return stored content hash for a doc, or None if absent."""
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    row = conn.execute("SELECT content_sha FROM docs WHERE id=?", (doc_id,)).fetchone()
    return row["content_sha"] if row else None
