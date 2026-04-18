# Markdown to VectorDB Migration — Local PoC
## Brain-Like Semantic Memory via sqlite-vec

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate every `.md` file in ClaudesCorner and `~/.claude/` into a local sqlite-vec vector database, so the LLM retrieves knowledge by semantic similarity — nothing pre-loaded into context, everything pulled on demand like associative memory.

**Architecture:** Single `core/vectorstore.db` (sqlite + sqlite-vec). A `projects/shared/vectordb.py` library owns all DB operations. A `scripts/index_all.py` ingester crawls all `.md` roots, classifies documents by type, embeds descriptions, and upserts. Both `memory-mcp` and `skill-manager-mcp` are refactored to query the DB. A two-pass retrieval model (semantic memory + episodic memory, mtime-weighted) replaces flat-file scanning. Identity (SOUL.md) acts as an embedding bias, not a loaded file.

**Mirrors:** `docs/markdown_to_vectordb_migration.md` — same data model, tools, governance, and retrieval patterns as the Azure PoC, with sqlite-vec replacing Azure AI Search and `all-MiniLM-L6-v2` (384-dim, local) replacing Azure OpenAI embeddings.

**Tech Stack:** `sqlite-vec`, `sentence-transformers` (all-MiniLM-L6-v2, dim=384), Python 3.11+, MCP stdio transport, existing `projects/shared/embedder.py`.

---

## Brain ↔ System Mapping

| Brain concept | System equivalent |
|---|---|
| Hippocampus (episodic, recent, fragile) | `daily_log`, `inbox` — raw recent experience |
| Cortex (semantic, compressed, durable) | `memory/`, `core/`, `skills/` — consolidated facts |
| Working memory (~4 active chunks) | Context window — 5-8 retrieved chunks max |
| Identity prior (shapes what you notice) | SOUL.md embedding added as query bias vector |
| Consolidation (hippocampus → cortex) | `feedback_flywheel.py` — daily log → SOUL.md patterns |
| Forgetting (irrelevant traces decay) | mtime-weighted scoring — old episodic docs score lower |
| Associative retrieval (cue → traces) | Two-pass search: semantic memory + episodic, merged |

---

## Document Taxonomy

Mirrors the Azure plan's `namespace` field. Every `.md` file gets a `doc_type`:

| doc_type | Source roots | Brain layer |
|---|---|---|
| `skill` | `~/.claude/skills/**/SKILL.md` | Procedural memory |
| `agent` | `~/.claude/agents/*.md` | Procedural memory |
| `memory` | `memory/*.md` (non-date) | Semantic cortex |
| `daily_log` | `memory/YYYY-MM-DD.md` | Episodic hippocampus |
| `core` | `core/*.md` | Identity / semantic cortex |
| `research` | `research/**/*.md` | Episodic hippocampus |
| `inbox` | `inbox/*.md` | Episodic hippocampus |
| `digested` | `digested/**/*.md` | Semantic cortex |
| `journal` | `journal/*.md` | Episodic hippocampus |
| `project` | `projects/**/*.md` | Semantic cortex |
| `root` | `*.md` at base (SOUL, DEADLINES…) | Identity / semantic |
| `cert` | `ms-certifications/**/*.md` | Semantic cortex |

---

## DB Schema

Mirrors Azure AI Search `skills-v1` schema locally.

```sql
-- docs: metadata + raw text (mirrors Azure Search document fields)
CREATE TABLE IF NOT EXISTS docs (
    id          TEXT PRIMARY KEY,    -- sha1(abs_path)[:16]
    path        TEXT NOT NULL,       -- absolute path
    rel_path    TEXT NOT NULL,       -- relative to BASE or ~/.claude
    doc_type    TEXT NOT NULL,       -- taxonomy label
    name        TEXT NOT NULL,       -- skill name / file stem / human label
    title       TEXT NOT NULL,       -- human-readable title (name → Title Case)
    description TEXT NOT NULL,       -- one-line summary — THIS IS WHAT GETS EMBEDDED
    body        TEXT NOT NULL,       -- full file content — retrieved on demand only
    tags        TEXT NOT NULL,       -- JSON array of tags extracted from frontmatter
    status      TEXT NOT NULL DEFAULT 'active',  -- active | deprecated | draft
    author      TEXT NOT NULL DEFAULT '',
    mtime       REAL NOT NULL,       -- file modification time
    created_at  TEXT NOT NULL,       -- ISO8601
    updated_at  TEXT NOT NULL        -- ISO8601
);

-- vec_docs: embedding index (sqlite-vec virtual table)
-- 384-dim float32, HNSW index via sqlite-vec
CREATE VIRTUAL TABLE IF NOT EXISTS vec_docs USING vec0(
    id        TEXT PRIMARY KEY,
    embedding FLOAT[384]
);
```

**Key design decisions matching Azure plan:**
- `description` is embedded, not `body` — maximum signal, minimum noise
- `body` is stored but never returned in search results — fetched on demand via `doc_get`
- `tags` extracted from frontmatter for namespace-style filtering
- `status` enables soft-delete / deprecation without data loss

---

## Two-Pass Retrieval (Brain Model)

Every search runs two passes then merges:

**Pass 1 — Semantic memory** (`doc_type IN (memory, core, skill, agent, digested, project, root, cert)`)
- Pure cosine similarity
- These are consolidated, durable, high-signal

**Pass 2 — Episodic memory** (`doc_type IN (daily_log, inbox, research, journal)`)
- Cosine similarity × recency weight: `score × (1 / log(1 + days_old + 1))`
- Recent episodes score higher; old ones decay unless very relevant

**Merge:** deduplicate by `id`, interleave by final score, return top N. Working memory = max 8 chunks.

**Identity bias:** SOUL.md embedding is loaded once at MCP server startup and added as a small weight to every query vector: `query_vec = 0.85 * query_vec + 0.15 * soul_vec`. This makes retrieval subtly shaped by identity without SOUL.md ever entering the context window explicitly.

---

## File Structure

```
projects/shared/
  embedder.py           ← already built
  vectordb.py           ← NEW: DB init, upsert, search, delete, fetch_body
  test_vectordb.py      ← NEW: unit tests

scripts/
  index_all.py          ← NEW: crawl all roots → classify → embed → upsert
  test_index_all.py     ← NEW: unit tests for classify + extract_summary

projects/brain-mcp/
  server.py             ← NEW: unified MCP server replacing memory-mcp + skill-manager-mcp queries
                              tools: search, get, push, list, deprecate (mirrors company-skills-mcp)

projects/memory-mcp/
  server.py             ← MODIFY: search_memory queries vectordb, two-pass brain retrieval

projects/skill-manager-mcp/
  server.py             ← MODIFY: skill_search queries vectordb, skill_list from DB

core/
  vectorstore.db        ← NEW: created at first index_all.py run
  soul_vec.npy          ← NEW: cached SOUL.md embedding (identity bias vector)
```

---

## Task 1: Install sqlite-vec and verify

**Files:** no code changes

- [ ] **Step 1: Install**

```bash
pip install sqlite-vec
```

- [ ] **Step 2: Verify sqlite-vec loads**

```python
python -c "
import sqlite3, sqlite_vec
conn = sqlite3.connect(':memory:')
conn.enable_load_extension(True)
sqlite_vec.load(conn)
conn.enable_load_extension(False)
print('sqlite-vec OK, version:', conn.execute('SELECT vec_version()').fetchone()[0])
"
```

Expected: `sqlite-vec OK, version: 0.x.x`

- [ ] **Step 3: Verify embedding dim**

```bash
python -c "
import sys; sys.path.insert(0,'projects/shared')
from embedder import load_embedder, embed
load_embedder()
v = embed(['test'])
print('dim:', v.shape[1])
"
```

Expected: `dim: 384`

- [ ] **Step 4: Commit**

```bash
git add requirements.txt 2>/dev/null || true
git commit -m "deps: add sqlite-vec for local vector store"
```

---

## Task 2: Build `vectordb.py` — DB schema + core operations

**Files:**
- Create: `projects/shared/vectordb.py`
- Create: `projects/shared/test_vectordb.py`

Mirrors the Azure AI Search document schema and operations locally.

- [ ] **Step 1: Write failing tests**

Create `projects/shared/test_vectordb.py`:

```python
import os, sys, pytest
sys.path.insert(0, os.path.dirname(__file__))

def test_init_creates_tables(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    conn = vectordb.get_connection(db)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','shadow','virtual')"
    ).fetchall()}
    assert "docs" in tables
    conn.close()

def test_upsert_and_search(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db,
        path="/fake/memory/2026-04-17.md",
        rel_path="memory/2026-04-17.md",
        doc_type="daily_log",
        name="2026-04-17",
        title="Daily Log 2026-04-17",
        description="Built vectordb, migrated skill-manager, brain model design",
        body="Full session log here.",
        tags=["infra", "vectordb"],
        mtime=1.0,
        embedding=[0.1] * 384,
    )
    results = vectordb.search(db, query_embedding=[0.1] * 384, top_k=1)
    assert len(results) == 1
    assert results[0]["name"] == "2026-04-17"
    assert results[0]["doc_type"] == "daily_log"
    assert "body" not in results[0]  # body not returned in search

def test_fetch_body(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db,
        path="/fake/core/SOUL.md",
        rel_path="core/SOUL.md",
        doc_type="core",
        name="SOUL",
        title="Soul",
        description="Identity and context",
        body="I am Claude. My purpose is...",
        tags=["identity"],
        mtime=1.0,
        embedding=[0.2] * 384,
    )
    body = vectordb.fetch_body(db, path="/fake/core/SOUL.md")
    assert body == "I am Claude. My purpose is..."

def test_doc_type_filter(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db, path="/fake/skills/brainstorming/SKILL.md",
        rel_path="skills/brainstorming/SKILL.md", doc_type="skill",
        name="brainstorming", title="Brainstorming", description="Creative ideation skill",
        body="...", tags=["meta"], mtime=1.0, embedding=[0.5] * 384)
    vectordb.upsert(db, path="/fake/memory/note.md",
        rel_path="memory/note.md", doc_type="memory",
        name="note", title="Note", description="A memory note",
        body="...", tags=[], mtime=1.0, embedding=[0.5] * 384)
    results = vectordb.search(db, query_embedding=[0.5] * 384, top_k=10, doc_type="skill")
    assert all(r["doc_type"] == "skill" for r in results)
    assert len(results) == 1

def test_delete(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db, path="/fake/inbox/clip.md",
        rel_path="inbox/clip.md", doc_type="inbox",
        name="clip", title="Clip", description="web clip",
        body="...", tags=[], mtime=1.0, embedding=[0.3] * 384)
    vectordb.delete(db, path="/fake/inbox/clip.md")
    results = vectordb.search(db, query_embedding=[0.3] * 384, top_k=5)
    assert all(r["name"] != "clip" for r in results)

def test_deprecate(tmp_path):
    import vectordb
    db = str(tmp_path / "test.db")
    vectordb.upsert(db, path="/fake/skills/old/SKILL.md",
        rel_path="skills/old/SKILL.md", doc_type="skill",
        name="old-skill", title="Old Skill", description="Outdated approach",
        body="...", tags=[], mtime=1.0, embedding=[0.4] * 384)
    vectordb.deprecate(db, path="/fake/skills/old/SKILL.md", reason="Superseded by new-skill")
    results = vectordb.search(db, query_embedding=[0.4] * 384, top_k=5, status="active")
    assert all(r["name"] != "old-skill" for r in results)
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd E:\2026\ClaudesCorner
python -m pytest projects/shared/test_vectordb.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'vectordb'`

- [ ] **Step 3: Implement `vectordb.py`**

Create `projects/shared/vectordb.py`:

```python
"""
shared/vectordb.py — sqlite-vec vector store for all .md documents.

Local PoC equivalent of Azure AI Search skills-v1 index.
Schema mirrors markdown_to_vectordb_migration.md data model.
"""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sqlite_vec

BASE = Path(__file__).parent.parent.parent
DB_PATH = str(BASE / "core" / "vectorstore.db")
DIM = 384
SEMANTIC_TYPES = {"memory", "core", "skill", "agent", "digested", "project", "root", "cert"}
EPISODIC_TYPES = {"daily_log", "inbox", "research", "journal"}


def _doc_id(path: str) -> str:
    return hashlib.sha1(path.encode()).hexdigest()[:16]


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
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
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_docs_type   ON docs(doc_type);
        CREATE INDEX IF NOT EXISTS idx_docs_status ON docs(status);
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_docs USING vec0(
            id        TEXT PRIMARY KEY,
            embedding FLOAT[384]
        );
    """)
    conn.commit()
    return conn


def upsert(db_path: str = DB_PATH, *, path: str, rel_path: str, doc_type: str,
           name: str, title: str, description: str, body: str,
           tags: list[str], mtime: float, embedding: list[float],
           status: str = "active", author: str = "") -> None:
    doc_id = _doc_id(path)
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(db_path)
    conn.execute("""
        INSERT INTO docs (id, path, rel_path, doc_type, name, title, description,
                          body, tags, status, author, mtime, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            rel_path=excluded.rel_path, doc_type=excluded.doc_type,
            name=excluded.name, title=excluded.title,
            description=excluded.description, body=excluded.body,
            tags=excluded.tags, status=excluded.status,
            author=excluded.author, mtime=excluded.mtime,
            updated_at=excluded.updated_at
    """, (doc_id, path, rel_path, doc_type, name, title, description,
          body, json.dumps(tags), status, author, mtime, now, now))
    vec_bytes = sqlite_vec.serialize_float32(embedding)
    conn.execute("""
        INSERT INTO vec_docs (id, embedding) VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET embedding=excluded.embedding
    """, (doc_id, vec_bytes))
    conn.commit()
    conn.close()


def delete(db_path: str = DB_PATH, *, path: str) -> None:
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    conn.execute("DELETE FROM docs WHERE id=?", (doc_id,))
    conn.execute("DELETE FROM vec_docs WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()


def deprecate(db_path: str = DB_PATH, *, path: str, reason: str = "") -> None:
    doc_id = _doc_id(path)
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection(db_path)
    conn.execute(
        "UPDATE docs SET status='deprecated', updated_at=? WHERE id=?",
        (now, doc_id)
    )
    conn.commit()
    conn.close()


def search(db_path: str = DB_PATH, *, query_embedding: list[float],
           top_k: int = 8, doc_type: str | None = None,
           status: str = "active",
           soul_bias: list[float] | None = None) -> list[dict[str, Any]]:
    """
    Two-pass brain retrieval:
    - Pass 1: semantic memory types — pure cosine similarity
    - Pass 2: episodic memory types — cosine × recency weight
    Merge, deduplicate, return top_k. Body excluded from results.
    """
    import numpy as np
    from datetime import datetime, timezone

    # Apply identity bias if soul_vec provided
    q = np.array(query_embedding, dtype="float32")
    if soul_bias is not None:
        s = np.array(soul_bias, dtype="float32")
        q = 0.85 * q + 0.15 * s
    q = q / (np.linalg.norm(q) + 1e-9)

    conn = get_connection(db_path)
    vec_bytes = sqlite_vec.serialize_float32(q.tolist())

    # Over-fetch to allow post-filtering
    raw = conn.execute("""
        SELECT v.id, v.distance
        FROM vec_docs v
        ORDER BY vec_distance_cosine(v.embedding, ?)
        LIMIT ?
    """, (vec_bytes, top_k * 6)).fetchall()

    if not raw:
        conn.close()
        return []

    ids = [r["id"] for r in raw]
    dist_map = {r["id"]: float(r["distance"]) for r in raw}

    placeholders = ",".join("?" * len(ids))
    type_filter = " AND doc_type=?" if doc_type else ""
    status_filter = f" AND status=?" if status else ""
    params = ids
    if doc_type:
        params = params + [doc_type]
    if status:
        params = params + [status]

    docs = conn.execute(
        f"SELECT id, path, rel_path, doc_type, name, title, description, tags, mtime "
        f"FROM docs WHERE id IN ({placeholders}){type_filter}{status_filter}",
        params
    ).fetchall()
    conn.close()

    now_ts = datetime.now(timezone.utc).timestamp()
    results = []
    for d in docs:
        cosine_score = 1.0 - dist_map[d["id"]]
        if d["doc_type"] in EPISODIC_TYPES:
            days_old = max(0, (now_ts - d["mtime"]) / 86400)
            import math
            recency = 1.0 / math.log(1 + days_old + 1)
            final_score = cosine_score * recency
        else:
            final_score = cosine_score
        results.append({
            "id": d["id"],
            "path": d["path"],
            "rel_path": d["rel_path"],
            "doc_type": d["doc_type"],
            "name": d["name"],
            "title": d["title"],
            "description": d["description"],
            "tags": json.loads(d["tags"]),
            "score": round(final_score, 4),
        })

    return sorted(results, key=lambda x: -x["score"])[:top_k]


def fetch_body(db_path: str = DB_PATH, *, path: str) -> str | None:
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    row = conn.execute("SELECT body FROM docs WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    return row["body"] if row else None


def count(db_path: str = DB_PATH, doc_type: str | None = None,
          status: str | None = None) -> int:
    conn = get_connection(db_path)
    q = "SELECT COUNT(*) FROM docs WHERE 1=1"
    params = []
    if doc_type:
        q += " AND doc_type=?"
        params.append(doc_type)
    if status:
        q += " AND status=?"
        params.append(status)
    n = conn.execute(q, params).fetchone()[0]
    conn.close()
    return n


def list_docs(db_path: str = DB_PATH, doc_type: str | None = None,
              status: str = "active", limit: int = 100) -> list[dict]:
    conn = get_connection(db_path)
    q = "SELECT id, rel_path, doc_type, name, title, description, tags, status, updated_at FROM docs WHERE status=?"
    params: list = [status]
    if doc_type:
        q += " AND doc_type=?"
        params.append(doc_type)
    q += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest projects/shared/test_vectordb.py -v
```

Expected: 6 PASSED

- [ ] **Step 5: Commit**

```bash
git add projects/shared/vectordb.py projects/shared/test_vectordb.py
git commit -m "feat: sqlite-vec vectordb library, mirrors Azure AI Search schema locally"
```

---

## Task 3: Build `scripts/index_all.py` — full ingester

**Files:**
- Create: `scripts/index_all.py`
- Create: `scripts/test_index_all.py`
- Create: `core/soul_vec.npy` (identity bias vector, generated on first run)

Mirrors `skill_sync.py` from the Azure plan — crawls all roots, classifies, embeds descriptions, upserts. Adds identity bias vector generation from SOUL.md.

- [ ] **Step 1: Write failing tests**

Create `scripts/test_index_all.py`:

```python
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'projects', 'shared'))
sys.path.insert(0, os.path.dirname(__file__))

def test_classify():
    import index_all
    assert index_all.classify("/c/Users/x/.claude/skills/brainstorming/SKILL.md") == "skill"
    assert index_all.classify("/c/Users/x/.claude/agents/ml-engineer.md") == "agent"
    assert index_all.classify("E:/2026/ClaudesCorner/memory/2026-04-17.md") == "daily_log"
    assert index_all.classify("E:/2026/ClaudesCorner/memory/reddit-brief.md") == "memory"
    assert index_all.classify("E:/2026/ClaudesCorner/core/SOUL.md") == "core"
    assert index_all.classify("E:/2026/ClaudesCorner/research/foo.md") == "research"
    assert index_all.classify("E:/2026/ClaudesCorner/inbox/clip.md") == "inbox"
    assert index_all.classify("E:/2026/ClaudesCorner/digested/article.md") == "digested"
    assert index_all.classify("E:/2026/ClaudesCorner/journal/2026-04.md") == "journal"
    assert index_all.classify("E:/2026/ClaudesCorner/projects/bi-agent/README.md") == "project"
    assert index_all.classify("E:/2026/ClaudesCorner/ms-certifications/dp700.md") == "cert"
    assert index_all.classify("E:/2026/ClaudesCorner/SOUL.md") == "root"

def test_extract_description():
    import index_all
    # frontmatter wins
    md = "---\nname: foo\ndescription: Does something useful\n---\n# body"
    assert index_all.extract_description(md, "foo") == "Does something useful"
    # H1 fallback
    md2 = "# My Document\nsome content"
    assert index_all.extract_description(md2, "fallback") == "My Document"
    # plain text fallback
    md3 = "Just plain text here\nmore text"
    assert index_all.extract_description(md3, "fallback") == "Just plain text here"

def test_extract_tags():
    import index_all
    md = "---\ntags: [fabric, dax, lakehouse]\n---\nbody"
    assert index_all.extract_tags(md) == ["fabric", "dax", "lakehouse"]
    md2 = "---\ntags: fabric\n---\nbody"
    assert index_all.extract_tags(md2) == ["fabric"]
    md3 = "no frontmatter"
    assert index_all.extract_tags(md3) == []

def test_make_title():
    import index_all
    assert index_all.make_title("systematic-debugging") == "Systematic Debugging"
    assert index_all.make_title("SOUL") == "Soul"
    assert index_all.make_title("2026-04-17") == "2026-04-17"
```

- [ ] **Step 2: Run — expect ImportError**

```bash
python -m pytest scripts/test_index_all.py -v 2>&1 | head -10
```

- [ ] **Step 3: Implement `index_all.py`**

Create `scripts/index_all.py`:

```python
#!/usr/bin/env python3
"""
scripts/index_all.py — Crawl all .md roots and upsert into vectorstore.db.

Mirrors skill_sync.py from the Azure plan but operates locally.
Also generates core/soul_vec.npy (identity bias vector) from SOUL.md.

Usage:
  python scripts/index_all.py              # index new/changed files only
  python scripts/index_all.py --force      # re-embed everything
  python scripts/index_all.py --dry-run    # preview without writing
  python scripts/index_all.py --doc-type skill  # re-index one type only
  python scripts/index_all.py --soul-only  # regenerate soul_vec.npy only
"""
import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
SHARED = BASE / "projects" / "shared"
sys.path.insert(0, str(SHARED))

import vectordb
import embedder as emb

CLAUDE_DIR = Path.home() / ".claude"
SOUL_VEC_PATH = BASE / "core" / "soul_vec.npy"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")

ROOTS: list[tuple[Path, str]] = [
    (CLAUDE_DIR / "skills",      "**/SKILL.md"),
    (CLAUDE_DIR / "agents",      "*.md"),
    (BASE / "memory",            "*.md"),
    (BASE / "core",              "*.md"),
    (BASE / "research",          "**/*.md"),
    (BASE / "inbox",             "*.md"),
    (BASE / "digested",          "**/*.md"),
    (BASE / "journal",           "*.md"),
    (BASE / "projects",          "**/*.md"),
    (BASE / "ms-certifications", "**/*.md"),
    (BASE,                       "*.md"),  # root-level .md files
]


def classify(path: str) -> str:
    s = path.replace("\\", "/")
    p = Path(path)
    if "/.claude/skills/" in s or "\\.claude\\skills\\" in s:
        return "skill"
    if "/.claude/agents/" in s or "\\.claude\\agents\\" in s:
        return "agent"
    if re.search(r"[/\\]memory[/\\]", s):
        return "daily_log" if DATE_RE.match(p.name) else "memory"
    if re.search(r"[/\\]core[/\\]", s):
        return "core"
    if re.search(r"[/\\]research[/\\]", s):
        return "research"
    if re.search(r"[/\\]inbox[/\\]", s):
        return "inbox"
    if re.search(r"[/\\]digested[/\\]", s):
        return "digested"
    if re.search(r"[/\\]journal[/\\]", s):
        return "journal"
    if re.search(r"[/\\]projects[/\\]", s):
        return "project"
    if re.search(r"[/\\]ms-certifications[/\\]", s):
        return "cert"
    return "root"


def extract_description(text: str, fallback: str) -> str:
    m = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped not in ("---", "===", ""):
            return stripped[:120]
    return fallback


def extract_tags(text: str) -> list[str]:
    m = re.search(r'^tags:\s*(.+)$', text, re.MULTILINE)
    if not m:
        return []
    val = m.group(1).strip()
    # YAML list: [a, b, c] or inline
    if val.startswith("["):
        try:
            import yaml
            parsed = yaml.safe_load(val)
            return [str(t) for t in parsed] if isinstance(parsed, list) else [str(parsed)]
        except Exception:
            return re.findall(r'[\w-]+', val)
    return [val.strip()]


def make_title(name: str) -> str:
    if re.match(r"^\d{4}-\d{2}-\d{2}$", name):
        return name
    return name.replace("-", " ").replace("_", " ").title()


def extract_name(path: Path, doc_type: str) -> str:
    if doc_type == "skill":
        return path.parent.name
    return path.stem


def iter_files(doc_type_filter: str | None = None):
    seen: set[str] = set()
    for root, pattern in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.glob(pattern)):
            s = str(p)
            if p.name.startswith(".") or s in seen:
                continue
            if doc_type_filter and classify(s) != doc_type_filter:
                continue
            seen.add(s)
            yield p


def generate_soul_vec() -> None:
    """Embed SOUL.md description and save as identity bias vector."""
    import numpy as np
    soul_path = BASE / "core" / "SOUL.md"
    if not soul_path.exists():
        print("  WARN: core/SOUL.md not found, skipping soul_vec generation")
        return
    text = soul_path.read_text(encoding="utf-8", errors="ignore")
    desc = extract_description(text, "Claude Code identity and context")
    vec = emb.embed([desc])[0]
    np.save(str(SOUL_VEC_PATH), vec)
    print(f"  soul_vec.npy saved ({vec.shape[0]}-dim)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--doc-type", default=None)
    parser.add_argument("--soul-only", action="store_true")
    parser.add_argument("--db", default=vectordb.DB_PATH)
    args = parser.parse_args()

    if not emb.load_embedder():
        print("ERROR: sentence-transformers not installed", file=sys.stderr)
        sys.exit(1)

    if args.soul_only:
        generate_soul_vec()
        return

    files = list(iter_files(doc_type_filter=args.doc_type))
    print(f"Found {len(files)} .md files" + (f" (type={args.doc_type})" if args.doc_type else ""))

    skipped = indexed = errors = 0
    BATCH = 16

    # Collect files that need (re)indexing
    to_index: list[tuple[Path, str, str, str, str, str, list, float]] = []
    for p in files:
        doc_type = classify(str(p))
        mtime = p.stat().st_mtime

        if not args.force and not args.dry_run:
            conn = vectordb.get_connection(args.db)
            doc_id = vectordb._doc_id(str(p))
            row = conn.execute("SELECT mtime FROM docs WHERE id=?", (doc_id,)).fetchone()
            conn.close()
            if row and abs(row["mtime"] - mtime) < 0.01:
                skipped += 1
                continue

        try:
            body = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  ERR  {p}: {e}")
            errors += 1
            continue

        name = extract_name(p, doc_type)
        description = extract_description(body, name)
        title = make_title(name)
        tags = extract_tags(body)

        try:
            rel = str(p.relative_to(BASE))
        except ValueError:
            try:
                rel = str(p.relative_to(CLAUDE_DIR))
            except ValueError:
                rel = p.name

        if args.dry_run:
            print(f"  DRY  [{doc_type:12}] {name}: {description[:60]}")
            continue

        to_index.append((p, doc_type, name, title, description, rel, tags, mtime, body))

    if args.dry_run:
        print(f"\nDry run complete — would index {len(to_index) + len(files) - skipped - errors} files")
        return

    # Batch embed descriptions
    descriptions = [item[4] for item in to_index]
    embeddings: list[list[float]] = []
    for i in range(0, len(descriptions), BATCH):
        batch_vecs = emb.embed(descriptions[i:i+BATCH])
        embeddings.extend(batch_vecs.tolist())
        done = min(i + BATCH, len(descriptions))
        if done % 50 == 0 or done == len(descriptions):
            print(f"  Embedded {done}/{len(descriptions)}")

    # Upsert
    for item, vec in zip(to_index, embeddings):
        p, doc_type, name, title, description, rel, tags, mtime, body = item
        vectordb.upsert(
            args.db,
            path=str(p), rel_path=rel, doc_type=doc_type,
            name=name, title=title, description=description,
            body=body, tags=tags, mtime=mtime, embedding=vec,
        )
        indexed += 1

    # Regenerate soul_vec after indexing
    generate_soul_vec()

    print(f"\nDone — indexed={indexed}, skipped={skipped}, errors={errors}")
    print(f"DB stats:")
    for dt in ["skill", "memory", "daily_log", "core", "research", "inbox",
               "agent", "project", "journal", "cert", "root", "digested"]:
        n = vectordb.count(args.db, doc_type=dt)
        if n > 0:
            print(f"  {dt:14}: {n}")
    print(f"  {'TOTAL':14}: {vectordb.count(args.db)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest scripts/test_index_all.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Dry run**

```bash
python scripts/index_all.py --dry-run 2>&1 | head -50
```

Verify doc_type classification looks correct across different roots.

- [ ] **Step 6: Full index run**

```bash
python scripts/index_all.py
```

Expected output ends with total count per doc_type and `TOTAL: ~200+`

- [ ] **Step 7: Verify DB and soul_vec**

```python
python -c "
import sys; sys.path.insert(0,'projects/shared')
import vectordb, numpy as np

print('Total docs:', vectordb.count())
soul = np.load('core/soul_vec.npy')
print('soul_vec shape:', soul.shape)

# Test retrieval
from embedder import load_embedder, embed
load_embedder()
q = embed(['debugging test failures'])[0].tolist()
results = vectordb.search(query_embedding=q, top_k=5)
for r in results:
    print(f\"  {r['score']:.4f} [{r['doc_type']:12}] {r['name']}: {r['description'][:50]}\")
" 2>/dev/null
```

- [ ] **Step 8: Commit**

```bash
git add scripts/index_all.py scripts/test_index_all.py core/vectorstore.db core/soul_vec.npy
git commit -m "feat: index_all.py ingester + initial vectorstore.db with brain-model retrieval"
```

---

## Task 4: Refactor `skill-manager-mcp` to query vectordb

**Files:**
- Modify: `projects/skill-manager-mcp/server.py`

Mirrors `company-skills-mcp` tools: `skill_search`, `skill_get`, `skill_push`, `skill_list`, `skill_deprecate`.

- [ ] **Step 1: Replace imports block**

Remove old embed imports, add vectordb:

```python
import os
from pathlib import Path
_SHARED = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(_SHARED))
import vectordb
import embedder as emb

TOP_K = 5
```

- [ ] **Step 2: Replace `skill_search`**

```python
def skill_search(query: str, top_k: int = TOP_K,
                 namespace: str | None = None) -> dict:
    """Semantic search over skills. Mirrors company-skills-mcp skill_search."""
    if not emb.load_embedder():
        return {"error": "sentence-transformers not installed"}
    soul_bias = _load_soul_vec()
    q_vec = emb.embed([query])[0].tolist()
    results = vectordb.search(
        query_embedding=q_vec, top_k=top_k,
        doc_type="skill", status="active", soul_bias=soul_bias
    )
    if not results:
        return {"query": query, "results": [],
                "hint": "Run: python scripts/index_all.py --doc-type skill"}
    if namespace:
        results = [r for r in results if namespace in r.get("tags", [])]
    return {
        "query": query,
        "results": [{"name": r["name"], "title": r["title"],
                     "description": r["description"], "score": r["score"],
                     "tags": r["tags"]}
                    for r in results],
    }


def _load_soul_vec() -> list[float] | None:
    try:
        import numpy as np
        path = Path(__file__).parent.parent.parent / "core" / "soul_vec.npy"
        if path.exists():
            return np.load(str(path)).tolist()
    except Exception:
        pass
    return None
```

- [ ] **Step 3: Replace `skill_list`**

```python
def skill_list(namespace: str | None = None, status: str = "active") -> dict:
    """List skills from DB. Mirrors company-skills-mcp skill_list."""
    docs = vectordb.list_docs(doc_type="skill", status=status, limit=200)
    if namespace:
        import json
        docs = [d for d in docs if namespace in json.loads(d.get("tags", "[]"))]
    skills = [{"name": d["name"], "title": d["title"],
               "description": d["description"], "status": d["status"],
               "type": "learned" if "learned" in d.get("rel_path", "") else "bundled"}
              for d in docs]
    return {"skills": skills, "total": len(skills)}
```

- [ ] **Step 4: Replace `skill_read` → `skill_get`**

```python
def skill_read(name: str) -> dict:
    """Fetch full skill body. Mirrors company-skills-mcp skill_get."""
    # Try DB first
    conn = vectordb.get_connection()
    row = conn.execute(
        "SELECT path, body, status FROM docs WHERE doc_type='skill' AND name=?", (name,)
    ).fetchone()
    conn.close()
    if row:
        body = row["body"]
        if row["status"] == "deprecated":
            body = f"<!-- DEPRECATED -->\n\n{body}"
        return {"name": name, "content": body, "path": row["path"]}
    # File fallback
    for base in (SKILLS_DIR, LEARNED_DIR):
        p = base / name / "SKILL.md"
        if p.exists():
            return {"name": name, "content": p.read_text(encoding="utf-8"), "path": str(p)}
    return {"error": f"Skill '{name}' not found"}
```

- [ ] **Step 5: Add `skill_deprecate` tool**

```python
def skill_deprecate(name: str, reason: str = "") -> dict:
    """Soft-delete a skill. Mirrors company-skills-mcp skill_deprecate."""
    conn = vectordb.get_connection()
    row = conn.execute(
        "SELECT path FROM docs WHERE doc_type='skill' AND name=?", (name,)
    ).fetchone()
    conn.close()
    if not row:
        return {"error": f"Skill '{name}' not found"}
    vectordb.deprecate(path=row["path"], reason=reason)
    return {"name": name, "status": "deprecated", "reason": reason}
```

- [ ] **Step 6: Add `skill_deprecate` to TOOLS list and handler**

Add to `TOOLS`:

```python
{
    "name": "skill_deprecate",
    "description": "Mark a skill as deprecated. Remains in DB but excluded from search results.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "reason": {"type": "string", "description": "Why deprecated"}
        },
        "required": ["name"]
    }
}
```

Add to `handle()`:

```python
elif name == "skill_deprecate":
    result = skill_deprecate(args["name"], args.get("reason", ""))
```

- [ ] **Step 7: Remove dead functions**

Delete: `_collect_skills`, `skill_index_build`, and any reference to `EMBED_INDEX_FILE`.

- [ ] **Step 8: Smoke test**

```bash
python -c "
import sys
sys.path.insert(0,'projects/shared')
sys.path.insert(0,'projects/skill-manager-mcp')
import server
print(server.skill_list()['total'], 'skills')
r = server.skill_search('debugging test failures')
print('top hit:', r['results'][0]['name'], r['results'][0]['score'])
print('read:', server.skill_read('systematic-debugging')['name'])
" 2>/dev/null
```

Expected: skill count > 0, top hit is `systematic-debugging`, read returns content.

- [ ] **Step 9: Commit**

```bash
git add projects/skill-manager-mcp/server.py
git commit -m "refactor: skill-manager-mcp queries vectordb, adds skill_deprecate, mirrors company-skills-mcp"
```

---

## Task 5: Refactor `memory-mcp` to query vectordb

**Files:**
- Modify: `projects/memory-mcp/server.py`

Two-pass brain retrieval exposed via `search_memory`. `doc_type` filter maps to brain layer selection. Identity bias applied via soul_vec.

- [ ] **Step 1: Add vectordb + embedder imports**

After existing imports in server.py:

```python
_SHARED = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(_SHARED))
import vectordb as vdb
import embedder as emb_util
import numpy as np

def _load_soul_vec() -> list[float] | None:
    try:
        p = BASE / "core" / "soul_vec.npy"
        if p.exists():
            return np.load(str(p)).tolist()
    except Exception:
        pass
    return None
```

- [ ] **Step 2: Replace `search_memory` implementation**

Find the existing `search_memory` tool handler and replace its body:

```python
async def _search_memory_impl(query: str, top_k: int = 8,
                               doc_type: str | None = None) -> list[dict]:
    if not emb_util.load_embedder():
        return [{"error": "embedder unavailable"}]
    soul_bias = _load_soul_vec()
    q_vec = emb_util.embed([query])[0].tolist()
    results = vdb.search(
        query_embedding=q_vec, top_k=top_k,
        doc_type=doc_type, status="active",
        soul_bias=soul_bias
    )
    return [{"name": r["name"], "doc_type": r["doc_type"],
             "description": r["description"], "score": r["score"],
             "rel_path": r["rel_path"], "title": r["title"]}
            for r in results]
```

- [ ] **Step 3: Add `doc_type` parameter to `search_memory` tool schema**

```python
"doc_type": {
    "type": "string",
    "description": (
        "Brain layer filter — "
        "semantic: memory|core|skill|agent|digested|project|root|cert  "
        "episodic: daily_log|inbox|research|journal  "
        "omit for full two-pass retrieval"
    )
}
```

- [ ] **Step 4: Replace `read_memory` body fetch**

Wherever `read_memory` currently reads file content, replace with:

```python
body = vdb.fetch_body(path=abs_path)
if body is None:
    body = Path(abs_path).read_text(encoding="utf-8", errors="ignore")
```

- [ ] **Step 5: Remove dead code**

Delete:
- `_collect_docs`
- `_build_embed_index`
- `_is_embed_stale`
- `_any_md_newer_than`
- `_load_embedder` (now in shared embedder.py)
- `_embed`, `_cosine_scores`
- `_build_embed_index`
- All references to `EMBED_INDEX_FILE`, `INDEX_FILE`

- [ ] **Step 6: Smoke test**

```bash
python -c "
import sys, asyncio
sys.path.insert(0,'projects/shared')
sys.path.insert(0,'projects/memory-mcp')
# Verify imports load cleanly
import server
print('memory-mcp imports OK')
" 2>/dev/null
```

- [ ] **Step 7: Commit**

```bash
git add projects/memory-mcp/server.py
git commit -m "refactor: memory-mcp two-pass brain retrieval via vectordb, identity bias from soul_vec"
```

---

## Task 6: Update CLAUDE.md — remove pre-loading, add vectordb retrieval at startup

**Files:**
- Modify: `~/.claude/CLAUDE.md`

Session startup should no longer read SOUL.md, HEARTBEAT.md, claude_memory.json directly. Instead: `search_memory` with session keywords pulls the relevant fragments. HEARTBEAT.md is still read (it's operational state, not knowledge).

- [ ] **Step 1: Update startup sequence in CLAUDE.md**

Replace the current startup block:

```markdown
- At the start of every session, BEFORE responding, do ALL of the following in order:
  1. Call `mcp__memory__search_memory` with 2-3 keywords from the user's first message.
     The vectordb returns relevant identity, memory, and skill context automatically.
     Do NOT manually read SOUL.md or claude_memory.json — they are indexed in the DB.
  2. Read `E:\2026\ClaudesCorner\core\HEARTBEAT.md` for current operational state
     (pending tasks, recent log — this is state not knowledge, so read directly).
  3. Run `date +%H` in Bash to get current hour. If hour < 10, call `get_tasks` via
     Todoist MCP and flag overdue tasks. If hour >= 10, skip.
```

- [ ] **Step 2: Verify CLAUDE.md reads correctly**

```bash
head -50 ~/.claude/CLAUDE.md
```

Confirm the new startup block is present and the old `Read SOUL.md` line is gone.

- [ ] **Step 3: Commit**

```bash
git add ~/.claude/CLAUDE.md 2>/dev/null || git add /c/Users/JasonNicolini/.claude/CLAUDE.md
git commit -m "config: session startup uses vectordb retrieval instead of pre-loading .md files"
```

---

## Task 7: PostToolUse hook — auto-index on Write/Edit to .md files

**Files:**
- Modify: `.claude/settings.json`

Mirrors the CI sync in the Azure plan — any `.md` write triggers re-indexing of that file.

- [ ] **Step 1: Add PostToolUse hook**

In `.claude/settings.json` under `hooks`, add or extend `PostToolUse`:

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "python E:\\2026\\ClaudesCorner\\scripts\\index_all.py 2>>E:\\2026\\ClaudesCorner\\logs\\index_all.log"
    }
  ]
}
```

The mtime check in `index_all.py` means only changed files are re-embedded. Full run takes <1s when nothing changed.

- [ ] **Step 2: Test hook fires**

Write a test file, confirm it gets indexed:

```bash
python -c "
from pathlib import Path
p = Path('E:/2026/ClaudesCorner/memory/test-hook-vectordb.md')
p.write_text('---\ndescription: test hook indexing\n---\ntest content')
"
# Hook fires here on the Write above (if run inside Claude Code session)
# Manually verify:
python -c "
import sys; sys.path.insert(0,'projects/shared')
import vectordb
conn = vectordb.get_connection()
row = conn.execute(\"SELECT name, description FROM docs WHERE name='test-hook-vectordb'\").fetchone()
print('indexed:', dict(row) if row else 'NOT FOUND')
conn.close()
"
python -c "from pathlib import Path; Path('E:/2026/ClaudesCorner/memory/test-hook-vectordb.md').unlink()"
```

- [ ] **Step 3: Commit**

```bash
git add .claude/settings.json
git commit -m "infra: auto-reindex .md files on Write/Edit via PostToolUse hook"
```

---

## Task 8: Cleanup and governance

**Files:**
- Delete: `memory/.embed_index.json`
- Delete: `memory/.index.json`
- Delete: `~/.claude/skills/.skill_embed_index.json`
- Update: memory entries for memory-mcp, skill-manager-mcp

Mirrors the Azure plan's governance section — soft-delete via `deprecate`, no hard deletes.

- [ ] **Step 1: Remove legacy index files**

```bash
rm -f E:/2026/ClaudesCorner/memory/.embed_index.json
rm -f E:/2026/ClaudesCorner/memory/.index.json
rm -f ~/.claude/skills/.skill_embed_index.json
```

- [ ] **Step 2: Update memory entries**

Run `index_all.py --soul-only` to refresh identity bias after any SOUL.md change:

```bash
python scripts/index_all.py --soul-only
```

- [ ] **Step 3: Verify end-to-end session startup**

Simulate a session cold start:

```python
python -c "
import sys
sys.path.insert(0, 'projects/shared')
import vectordb, embedder as emb, numpy as np

emb.load_embedder()
soul = np.load('core/soul_vec.npy').tolist()

# Simulate: user says 'Hey, let's work on the BI agent today'
q = emb.embed(['BI agent DAX Power BI'])[0].tolist()
results = vectordb.search(query_embedding=q, top_k=8, soul_bias=soul)

print('Session startup context (what would enter working memory):')
for r in results:
    print(f\"  {r['score']:.4f} [{r['doc_type']:12}] {r['name']}: {r['description'][:55]}\")
" 2>/dev/null
```

Verify relevant context surfaces (bi-agent memory, DAX skills, relevant research) without loading everything.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "cleanup: remove legacy embed indexes, governance docs updated"
```

---

## Score Threshold Guide

Mirrors the `query-company-skills` skill from the Azure plan:

| Score | Meaning | Action |
|---|---|---|
| > 0.85 | Exact match | Use directly |
| 0.70–0.85 | Strong match | Review description, likely use |
| 0.50–0.70 | Partial match | Check body before using |
| < 0.50 | Weak match | May not be relevant |

Note: episodic results (daily_log, research, inbox) are recency-weighted so scores are not directly comparable to semantic results. A daily_log from yesterday at 0.45 may be more useful than a research doc at 0.60.

---

## Governance

### Soft-delete only (mirrors Azure `skill_deprecate`)

Never hard-delete from the DB. Use `skill_deprecate` (for skills) or `vectordb.deprecate()` directly. Deprecated docs remain in the DB with `status='deprecated'`, excluded from all searches. Recoverable.

### Draft workflow (for new skills)

When `skill_create` writes a new skill file, it upserts with `status='draft'`. Draft skills appear in `skill_list(status='draft')` but not in `skill_search` (which filters `status='active'`). Promote via:

```python
# In skill-manager-mcp, add a skill_approve tool:
def skill_approve(name: str) -> dict:
    conn = vectordb.get_connection()
    row = conn.execute("SELECT path FROM docs WHERE doc_type='skill' AND name=?", (name,)).fetchone()
    conn.close()
    if not row:
        return {"error": f"Skill '{name}' not found"}
    vectordb.get_connection().execute(
        "UPDATE docs SET status='active' WHERE path=?", (row["path"],)
    )
    return {"name": name, "status": "active"}
```

### Stale detection (mirrors Azure `flag_stale_skills.py`)

Query the DB for docs not updated in 90 days:

```python
python -c "
import sys, sqlite3
sys.path.insert(0,'projects/shared')
import vectordb
from datetime import datetime, timedelta, timezone
cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
conn = vectordb.get_connection()
rows = conn.execute(
    \"SELECT name, doc_type, updated_at FROM docs WHERE status='active' AND updated_at < ? ORDER BY updated_at\",
    (cutoff,)
).fetchall()
print(f'{len(rows)} stale docs (>90 days):')
for r in rows[:20]:
    print(f'  {r[\"doc_type\"]:12} {r[\"name\"]:30} last updated: {r[\"updated_at\"][:10]}')
conn.close()
" 2>/dev/null
```

---

## Expected Context Savings

| Before | After |
|---|---|
| Skills pre-loaded: ~28K tokens | Skills: ~0 tokens at startup |
| Memory embed index: in RAM | Index: vectorstore.db on disk |
| SOUL.md always read: ~3K tokens | SOUL: identity bias only, never in context |
| search_memory scans all .md | search_memory: single DB query, <50ms |
| Baseline session burn: ~22% | Target baseline: ~8% |

**~14K tokens reclaimed (~7% of 200K window) every session.**

---

## Upgrade Path to Azure (Production)

This PoC mirrors the Azure plan exactly so migration is a config swap:

| PoC (this plan) | Azure (production) |
|---|---|
| `sqlite_vec.serialize_float32` | Azure AI Search REST upsert |
| `all-MiniLM-L6-v2` 384-dim | `text-embedding-3-small` 1536-dim |
| `vectorstore.db` file | Azure AI Search `skills-v1` index |
| `index_all.py` | `skill_sync.py` + GitHub Actions CI |
| `skill_deprecate` in DB | `skill_deprecate` via Search REST API |
| Local file governance | Draft/approve flow with Teams digest |

Same data model, same tool names, same retrieval logic. Swap the backend, keep everything else.

---

*Local PoC of `docs/markdown_to_vectordb_migration.md` | 2026-04-17 | Status: Plan complete*
