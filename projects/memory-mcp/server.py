#!/usr/bin/env python3
"""
memory-mcp/server.py — MCP server exposing SOUL.md, MEMORY.md, HEARTBEAT.md as tools.
Transport: stdio (works with Claude Desktop's MCP config).
Search: sentence-transformers semantic embeddings (falls back to TF-IDF if unavailable).
"""
import json
import math
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, date as Date
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

BASE = Path(__file__).parent.parent.parent  # → E:\2026\ClaudesCorner
SOUL = BASE / "core" / "SOUL.md"
HEARTBEAT = BASE / "core" / "HEARTBEAT.md"
MEMORY = BASE / "MEMORY.md"
MEMORY_DIR = BASE / "memory"
INDEX_FILE = MEMORY_DIR / ".index.json"
EMBED_INDEX_FILE = MEMORY_DIR / ".embed_index.json"
ACCESS_LOG_FILE = MEMORY_DIR / ".access_log.json"
CONTEXT_PACK = BASE / "scripts" / "context-pack.py"
MD_ROOTS = [MEMORY_DIR, BASE, BASE / "core"]
TOP_K = 10
EMBED_MODEL = "all-MiniLM-L6-v2"

# --- Embedding support (optional) ---

_embedder = None
_embed_available = False

def _load_embedder():
    global _embedder, _embed_available
    if _embed_available:
        return True
    try:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(EMBED_MODEL)
        _embed_available = True
        return True
    except Exception:
        return False


def _embed(texts: list[str]):
    """Return numpy array of embeddings, shape (N, D)."""
    return _embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def _cosine_scores(query_vec, doc_vecs):
    """Cosine similarity between query_vec (D,) and doc_vecs (N, D)."""
    import numpy as np
    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    norms = np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-9
    normed = doc_vecs / norms
    return normed @ q  # shape (N,)


# --- Shared doc loader ---

def _collect_docs() -> dict[str, str]:
    docs: dict[str, str] = {}
    for root in MD_ROOTS:
        if not root.exists():
            continue
        pattern = "*.md" if root == BASE else "**/*.md"
        for p in sorted(root.glob(pattern)):
            if p.name.startswith("."):
                continue
            rel = str(p.relative_to(BASE))
            try:
                docs[rel] = p.read_text(encoding="utf-8")
            except Exception:
                pass
    return docs


def _any_md_newer_than(mtime: float) -> bool:
    for root in MD_ROOTS:
        if not root.exists():
            continue
        pattern = "*.md" if root == BASE else "**/*.md"
        for p in root.glob(pattern):
            if not p.name.startswith(".") and p.stat().st_mtime > mtime:
                return True
    return False


# --- Semantic search ---

def _build_embed_index(docs: dict[str, str]) -> dict:
    import numpy as np
    doc_ids = list(docs.keys())
    texts = [docs[d] for d in doc_ids]
    vecs = _embed(texts)
    return {
        "doc_ids": doc_ids,
        "embeddings": vecs.tolist(),
    }


def _is_embed_stale(docs: dict[str, str]) -> bool:
    if not EMBED_INDEX_FILE.exists():
        return True
    mtime = EMBED_INDEX_FILE.stat().st_mtime
    if _any_md_newer_than(mtime):
        return True
    # Also stale if doc count changed
    try:
        idx = json.loads(EMBED_INDEX_FILE.read_text(encoding="utf-8"))
        return len(idx.get("doc_ids", [])) != len(docs)
    except Exception:
        return True


def _load_embed_index() -> dict | None:
    if EMBED_INDEX_FILE.exists():
        try:
            return json.loads(EMBED_INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _save_embed_index(index: dict) -> None:
    EMBED_INDEX_FILE.parent.mkdir(exist_ok=True)
    EMBED_INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")


def _load_access_log() -> dict:
    if ACCESS_LOG_FILE.exists():
        try:
            return json.loads(ACCESS_LOG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _record_hits(doc_ids: list[str]) -> None:
    """Increment hit counter for each returned doc."""
    log = _load_access_log()
    ts = datetime.now().isoformat()
    for doc_id in doc_ids:
        entry = log.get(doc_id, {"hits": 0, "first_seen": ts, "last_hit": None})
        entry["hits"] += 1
        entry["last_hit"] = ts
        log[doc_id] = entry
    # Register all known docs with 0 hits if not yet seen
    ACCESS_LOG_FILE.parent.mkdir(exist_ok=True)
    ACCESS_LOG_FILE.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_stale_docs(min_days_old: int = 30, max_hits: int = 0) -> list[dict]:
    """Return docs older than min_days_old with <= max_hits search hits."""
    log = _load_access_log()
    now = datetime.now()
    stale = []
    for doc_id, entry in log.items():
        if entry["hits"] > max_hits:
            continue
        path = Path(doc_id)
        if not path.exists():
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        age_days = (now - mtime).days
        if age_days >= min_days_old:
            stale.append({
                "doc_id": doc_id,
                "age_days": age_days,
                "hits": entry["hits"],
                "last_hit": entry["last_hit"],
            })
    return sorted(stale, key=lambda x: x["hits"])


def _search_semantic(query: str, docs: dict[str, str],
                     from_date: str | None, to_date: str | None) -> str:
    import numpy as np
    index = None if _is_embed_stale(docs) else _load_embed_index()
    if index is None:
        index = _build_embed_index(docs)
        _save_embed_index(index)

    doc_ids = index["doc_ids"]
    doc_vecs = np.array(index["embeddings"], dtype=np.float32)
    query_vec = _embed([query])[0]
    scores = _cosine_scores(query_vec, doc_vecs)

    fd = Date.fromisoformat(from_date) if from_date else None
    td = Date.fromisoformat(to_date) if to_date else None
    terms = re.findall(r"[a-zA-Z0-9_\-]{2,}", query.lower())

    ranked = sorted(zip(doc_ids, scores.tolist()), key=lambda x: x[1], reverse=True)
    lines = [f"Results for: {query!r} (semantic)\n"]
    count = 0
    returned_ids = []
    for doc_id, score in ranked:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", Path(doc_id).stem)
        if m:
            d = Date.fromisoformat(m.group(1))
            if fd and d < fd:
                continue
            if td and d > td:
                continue
        snippet = _snippet(docs.get(doc_id, ""), terms)
        lines.append(f"  {count+1}. [{score:.3f}] {doc_id}")
        if snippet:
            lines.append(f"     > {snippet}")
        returned_ids.append(doc_id)
        count += 1
        if count >= TOP_K:
            break

    if count == 0:
        return f"No results for: {query!r}"
    _record_hits(returned_ids)
    return "\n".join(lines)


# --- TF-IDF fallback ---

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_\-]{2,}", text.lower())


def _build_tfidf_index(docs: dict[str, str]) -> dict:
    tf: dict[str, dict[str, float]] = {}
    df: dict[str, int] = defaultdict(int)
    for doc_id, text in docs.items():
        tokens = _tokenize(text)
        if not tokens:
            continue
        freq: dict[str, int] = defaultdict(int)
        for t in tokens:
            freq[t] += 1
        total = len(tokens)
        tf[doc_id] = {t: c / total for t, c in freq.items()}
        for t in freq:
            df[t] += 1
    N = len(docs)
    idf = {t: math.log((N + 1) / (c + 1)) + 1 for t, c in df.items()}
    inverted: dict[str, list] = defaultdict(list)
    for doc_id, term_tf in tf.items():
        for term, score in term_tf.items():
            inverted[term].append((doc_id, score * idf.get(term, 1.0)))
    return {"inverted": dict(inverted), "idf": idf, "docs": list(docs.keys())}


def _is_tfidf_stale(docs: dict[str, str]) -> bool:
    if not INDEX_FILE.exists():
        return True
    mtime = INDEX_FILE.stat().st_mtime
    return _any_md_newer_than(mtime)


def _load_tfidf_index() -> dict | None:
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _save_tfidf_index(index: dict) -> None:
    INDEX_FILE.parent.mkdir(exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")


def _search_tfidf(query: str, docs: dict[str, str],
                  from_date: str | None, to_date: str | None) -> str:
    index = None if _is_tfidf_stale(docs) else _load_tfidf_index()
    if index is None:
        index = _build_tfidf_index(docs)
        _save_tfidf_index(index)
    terms = _tokenize(query)
    scores: dict[str, float] = defaultdict(float)
    for term in terms:
        for doc_id, score in index["inverted"].get(term, []):
            scores[doc_id] += score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    fd = Date.fromisoformat(from_date) if from_date else None
    td = Date.fromisoformat(to_date) if to_date else None
    lines = [f"Results for: {query!r} (TF-IDF fallback)\n"]
    count = 0
    for doc_id, score in ranked:
        m = re.search(r"(\d{4}-\d{2}-\d{2})", Path(doc_id).stem)
        if m:
            d = Date.fromisoformat(m.group(1))
            if fd and d < fd:
                continue
            if td and d > td:
                continue
        snippet = _snippet(docs.get(doc_id, ""), terms)
        lines.append(f"  {count+1}. [{score:.3f}] {doc_id}")
        if snippet:
            lines.append(f"     > {snippet}")
        count += 1
        if count >= TOP_K:
            break
    if count == 0:
        return f"No results for: {query!r}"
    return "\n".join(lines)


# --- Shared snippet ---

def _snippet(text: str, terms: list[str]) -> str:
    lines = text.splitlines()
    section = ""
    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            section = line.strip()
        if any(t in line.lower() for t in terms):
            ctx = " ".join(l.strip() for l in lines[i:i+3] if l.strip())
            return ((section + " > " if section else "") + ctx)[:200]
    return ""


# --- Unified search entry point ---

def _search_memory(query: str, from_date: str | None = None, to_date: str | None = None) -> str:
    docs = _collect_docs()
    if _load_embedder():
        return _search_semantic(query, docs, from_date, to_date)
    return _search_tfidf(query, docs, from_date, to_date)


# --- MCP server ---

server = Server("memory-mcp")


def _read(p: Path) -> str:
    if p.exists():
        return p.read_text(encoding="utf-8")
    return f"[{p.name} not found]"


def _run_script(script: Path, args: list[str] = []) -> str:
    try:
        python = sys.executable if sys.executable else r"C:\Python314\python.exe"
        result = subprocess.run(
            [python, str(script)] + args,
            capture_output=True, text=True, timeout=30,
            cwd=str(BASE),
        )
        out = result.stdout + result.stderr
        return out.strip() or "[no output]"
    except subprocess.TimeoutExpired:
        return "[script timed out after 30s]"
    except Exception as e:
        return f"[error running script: {e}]"


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_soul",
            description="Read SOUL.md — Jason's identity, purpose, personality context.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="read_heartbeat",
            description="Read HEARTBEAT.md — current session state, OpenClaw parity, log of recent sessions.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="read_memory",
            description="Read MEMORY.md — curated durable facts and key decisions across all sessions.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="read_daily_log",
            description="Read a specific daily memory log. Defaults to today.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format. Defaults to today.",
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="search_memory",
            description="Semantic search across all .md memory files using sentence-transformers embeddings (falls back to TF-IDF). Supports date filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language search query"},
                    "from_date": {"type": "string", "description": "Filter results from this date (YYYY-MM-DD)"},
                    "to_date": {"type": "string", "description": "Filter results up to this date (YYYY-MM-DD)"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_stale_docs",
            description="Return memory docs that have low search hit counts and are older than a threshold. Useful for AutoDream pruning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_days_old": {"type": "integer", "description": "Minimum file age in days (default 30)", "default": 30},
                    "max_hits": {"type": "integer", "description": "Maximum search hits to qualify as stale (default 0)", "default": 0},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="append_heartbeat_log",
            description="Append a timestamped entry to the ## Log section of HEARTBEAT.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Log entry text (one or more lines)"}
                },
                "required": ["message"],
            },
        ),
        types.Tool(
            name="run_context_pack",
            description="Run context-pack.py to regenerate MEMORY.md from all memory sources.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="list_memory_files",
            description="List all daily memory log files.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="write_memory",
            description="Append a durable fact or decision to MEMORY.md under a given section heading. Creates the section if it doesn't exist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {"type": "string", "description": "Section heading to append under (e.g. 'Key Decisions')"},
                    "fact": {"type": "string", "description": "The fact or decision to record as a bullet point"},
                },
                "required": ["section", "fact"],
            },
        ),
        types.Tool(
            name="update_preferences",
            description="Add or update a preference in the '## Preferences I've Learned' section of SOUL.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "preference": {"type": "string", "description": "The preference to add (one line)"},
                },
                "required": ["preference"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    def text(s: str) -> list[types.TextContent]:
        return [types.TextContent(type="text", text=s)]

    if name == "read_soul":
        return text(_read(SOUL))

    if name == "read_heartbeat":
        return text(_read(HEARTBEAT))

    if name == "read_memory":
        return text(_read(MEMORY))

    if name == "read_daily_log":
        date_str = arguments.get("date") or datetime.now().strftime("%Y-%m-%d")
        log_file = MEMORY_DIR / f"{date_str}.md"
        return text(_read(log_file))

    if name == "search_memory":
        query = arguments.get("query", "")
        if not query:
            return text("[error: query is required]")
        out = _search_memory(query, arguments.get("from_date"), arguments.get("to_date"))
        return text(out)

    if name == "get_stale_docs":
        min_days = int(arguments.get("min_days_old", 30))
        max_hits = int(arguments.get("max_hits", 0))
        stale = _get_stale_docs(min_days, max_hits)
        if not stale:
            return text(f"No stale docs found (age >= {min_days}d, hits <= {max_hits}).")
        lines = [f"Stale docs (age >= {min_days}d, hits <= {max_hits}):\n"]
        for item in stale:
            lines.append(f"  {item['doc_id']}  [{item['age_days']}d old, {item['hits']} hits]")
        return text("\n".join(lines))

    if name == "append_heartbeat_log":
        message = arguments.get("message", "").strip()
        if not message:
            return text("[error: message is required]")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n### {ts}\n{message}\n"
        hb_text = _read(HEARTBEAT)
        if "## Log" not in hb_text:
            hb_text += "\n## Log\n"
        HEARTBEAT.write_text(hb_text + entry, encoding="utf-8")
        return text(f"[appended to HEARTBEAT.md at {ts}]")

    if name == "run_context_pack":
        out = _run_script(CONTEXT_PACK)
        return text(out)

    if name == "list_memory_files":
        if not MEMORY_DIR.exists():
            return text("[memory/ directory not found]")
        files = sorted(MEMORY_DIR.glob("????-??-??.md"))
        if not files:
            return text("[no daily logs found]")
        listing = "\n".join(f.name for f in files)
        return text(f"Daily memory logs:\n{listing}")

    if name == "write_memory":
        section = arguments.get("section", "").strip()
        fact = arguments.get("fact", "").strip()
        if not section or not fact:
            return text("[error: section and fact are required]")
        mem_text = _read(MEMORY)
        heading = f"## {section}"
        bullet = f"- {fact}"
        if heading in mem_text:
            mem_text = mem_text.replace(heading, heading + f"\n{bullet}", 1)
        else:
            mem_text = mem_text.rstrip() + f"\n\n{heading}\n{bullet}\n"
        MEMORY.write_text(mem_text, encoding="utf-8")
        return text(f"[written to MEMORY.md under '{section}']")

    if name == "update_preferences":
        preference = arguments.get("preference", "").strip()
        if not preference:
            return text("[error: preference is required]")
        soul_text = _read(SOUL)
        prefs_heading = "## Preferences I've Learned"
        bullet = f"- {preference}"
        if prefs_heading in soul_text:
            soul_text = soul_text.replace(prefs_heading, prefs_heading + f"\n{bullet}", 1)
        else:
            soul_text = soul_text.rstrip() + f"\n\n{prefs_heading}\n{bullet}\n"
        SOUL.write_text(soul_text, encoding="utf-8")
        return text(f"[preference added to SOUL.md]")

    return text(f"[unknown tool: {name}]")


async def main() -> None:
    # Warm embedder at startup to avoid cold-call timeouts
    _load_embedder()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
