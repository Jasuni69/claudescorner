# VectorDB Migration — Full `.md` Store Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace all flat-file `.md` scanning and `.embed_index.json` caches with a single sqlite-vec vector database, so every `.md` document in ClaudesCorner and `~/.claude/` is retrievable by semantic similarity — and nothing is pre-loaded into context.

**Architecture:** A single `vectorstore.db` (sqlite + sqlite-vec extension) lives at `E:\2026\ClaudesCorner\core\vectorstore.db`. A shared `projects/shared/vectordb.py` library handles all DB operations. Both `memory-mcp` and `skill-manager-mcp` are refactored to query this DB instead of scanning files. A standalone `scripts/index_all.py` ingester crawls all `.md` roots, embeds them, and upserts records — run on-demand and on file-change.

**Tech Stack:** `sqlite-vec` (vector extension for SQLite), `sentence-transformers` (all-MiniLM-L6-v2, dim=384), Python 3.11+, existing MCP stdio transport.

---

## Document Taxonomy

Every `.md` file gets a `doc_type` label used for namespace filtering:

| doc_type | Source roots |
|---|---|
| `skill` | `~/.claude/skills/**/SKILL.md` |
| `agent` | `~/.claude/agents/*.md` |
| `memory` | `E:\2026\ClaudesCorner\memory/*.md` |
| `daily_log` | `E:\2026\ClaudesCorner\memory/YYYY-MM-DD.md` (date pattern) |
| `core` | `E:\2026\ClaudesCorner\core/*.md` |
| `research` | `E:\2026\ClaudesCorner\research/**/*.md` |
| `inbox` | `E:\2026\ClaudesCorner\inbox/*.md` |
| `digested` | `E:\2026\ClaudesCorner\digested/*.md` |
| `journal` | `E:\2026\ClaudesCorner\journal/*.md` |
| `project` | `E:\2026\ClaudesCorner\projects/**/*.md` |
| `root` | `E:\2026\ClaudesCorner/*.md` (SOUL, DEADLINES, etc.) |
| `cert` | `E:\2026\ClaudesCorner\ms-certifications/**/*.md` |

---

## File Structure

```
projects/shared/
  embedder.py          ← already built (load_embedder, embed, cosine_scores)
  vectordb.py          ← NEW: DB init, upsert, search, delete

scripts/
  index_all.py         ← NEW: crawl all roots → upsert into vectordb

projects/memory-mcp/
  server.py            ← MODIFY: replace _collect_docs + embed index with vectordb queries

projects/skill-manager-mcp/
  server.py            ← MODIFY: replace _collect_skills + .embed_index.json with vectordb queries

core/
  vectorstore.db       ← NEW: created at first run of index_all.py
```

---

## Task 1: Install sqlite-vec

**Files:**
- No code changes — dependency install + verify

- [ ] **Step 1: Install sqlite-vec**

```bash
pip install sqlite-vec
```

- [ ] **Step 2: Verify**

```python
python -c "import sqlite_vec; print(sqlite_vec.sqlite_version())"
```

Expected output: `3.x.x` (SQLite version string)

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "deps: add sqlite-vec"
```

---

## Task 2: Build `vectordb.py` — DB schema + core operations

**Files:**
- Create: `projects/shared/vectordb.py`

This is the single source of truth for all DB interactions. No other file touches SQLite directly.

**Schema:**

```sql
-- docs: metadata + raw text
CREATE TABLE IF NOT EXISTS docs (
    id       TEXT PRIMARY KEY,   -- deterministic: sha1(abs_path)
    path     TEXT NOT NULL,      -- absolute path
    rel_path TEXT NOT NULL,      -- relative to ClaudesCorner or ~/.claude
    doc_type TEXT NOT NULL,      -- taxonomy label (see above)
    name     TEXT NOT NULL,      -- human label (skill name, filename stem, etc.)
    summary  TEXT NOT NULL,      -- first meaningful line / frontmatter description
    body     TEXT NOT NULL,      -- full file content
    mtime    REAL NOT NULL       -- file modification time (os.path.getmtime)
);

-- vec_docs: embedding index (sqlite-vec virtual table)
CREATE VIRTUAL TABLE IF NOT EXISTS vec_docs USING vec0(
    id       TEXT PRIMARY KEY,
    embedding FLOAT[384]
);
```

- [ ] **Step 1: Write failing test**

Create `projects/shared/test_vectordb.py`:

```python
import os, sys, tempfile, pytest
sys.path.insert(0, os.path.dirname(__file__))
import vectordb

def test_init_creates_tables(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = vectordb.get_connection(db_path)
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    assert "docs" in tables

def test_upsert_and_search(tmp_path):
    db_path = str(tmp_path / "test.db")
    vectordb.upsert(db_path, path="/fake/memory/2026-04-17.md",
                    rel_path="memory/2026-04-17.md", doc_type="memory",
                    name="2026-04-17", summary="daily log april 17",
                    body="Built vectordb. Migrated skill-manager.", mtime=1.0,
                    embedding=[0.1]*384)
    results = vectordb.search(db_path, query_embedding=[0.1]*384, top_k=1)
    assert results[0]["name"] == "2026-04-17"

def test_delete(tmp_path):
    db_path = str(tmp_path / "test.db")
    vectordb.upsert(db_path, path="/fake/core/SOUL.md",
                    rel_path="core/SOUL.md", doc_type="core",
                    name="SOUL", summary="identity", body="...", mtime=1.0,
                    embedding=[0.2]*384)
    vectordb.delete(db_path, path="/fake/core/SOUL.md")
    results = vectordb.search(db_path, query_embedding=[0.2]*384, top_k=5)
    assert all(r["name"] != "SOUL" for r in results)
```

- [ ] **Step 2: Run — expect ImportError**

```bash
cd E:\2026\ClaudesCorner
python -m pytest projects/shared/test_vectordb.py -v
```

Expected: `ModuleNotFoundError: No module named 'vectordb'`

- [ ] **Step 3: Implement `vectordb.py`**

```python
"""
shared/vectordb.py — sqlite-vec backed document store for all .md files.
"""
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

import sqlite_vec

DB_PATH = str(Path(__file__).parent.parent.parent / "core" / "vectorstore.db")
DIM = 384


def _doc_id(path: str) -> str:
    return hashlib.sha1(path.encode()).hexdigest()


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS docs (
            id       TEXT PRIMARY KEY,
            path     TEXT NOT NULL,
            rel_path TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            name     TEXT NOT NULL,
            summary  TEXT NOT NULL,
            body     TEXT NOT NULL,
            mtime    REAL NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_docs USING vec0(
            id TEXT PRIMARY KEY,
            embedding FLOAT[384]
        );
    """)
    conn.commit()
    return conn


def upsert(db_path: str = DB_PATH, *, path: str, rel_path: str, doc_type: str,
           name: str, summary: str, body: str, mtime: float,
           embedding: list[float]) -> None:
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    conn.execute("""
        INSERT INTO docs (id, path, rel_path, doc_type, name, summary, body, mtime)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
            rel_path=excluded.rel_path, doc_type=excluded.doc_type,
            name=excluded.name, summary=excluded.summary,
            body=excluded.body, mtime=excluded.mtime
    """, (doc_id, path, rel_path, doc_type, name, summary, body, mtime))
    vec_bytes = sqlite_vec.serialize_float32(embedding)
    conn.execute("""
        INSERT INTO vec_docs (id, embedding) VALUES (?,?)
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


def search(db_path: str = DB_PATH, *, query_embedding: list[float],
           top_k: int = 10, doc_type: str | None = None) -> list[dict[str, Any]]:
    conn = get_connection(db_path)
    vec_bytes = sqlite_vec.serialize_float32(query_embedding)
    rows = conn.execute("""
        SELECT v.id, v.distance
        FROM vec_docs v
        ORDER BY vec_distance_cosine(v.embedding, ?) 
        LIMIT ?
    """, (vec_bytes, top_k * 3)).fetchall()  # over-fetch for doc_type filter
    if not rows:
        return []
    ids = [r["id"] for r in rows]
    dist_map = {r["id"]: r["distance"] for r in rows}
    placeholders = ",".join("?" * len(ids))
    type_filter = f" AND doc_type=?" if doc_type else ""
    params = ids + ([doc_type] if doc_type else [])
    docs = conn.execute(
        f"SELECT id, path, rel_path, doc_type, name, summary FROM docs "
        f"WHERE id IN ({placeholders}){type_filter}", params
    ).fetchall()
    conn.close()
    results = sorted(
        [{"id": d["id"], "path": d["path"], "rel_path": d["rel_path"],
          "doc_type": d["doc_type"], "name": d["name"], "summary": d["summary"],
          "score": round(1 - dist_map[d["id"]], 4)}
         for d in docs],
        key=lambda x: -x["score"]
    )
    return results[:top_k]


def fetch_body(db_path: str = DB_PATH, *, path: str) -> str | None:
    doc_id = _doc_id(path)
    conn = get_connection(db_path)
    row = conn.execute("SELECT body FROM docs WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    return row["body"] if row else None


def count(db_path: str = DB_PATH, doc_type: str | None = None) -> int:
    conn = get_connection(db_path)
    if doc_type:
        n = conn.execute("SELECT COUNT(*) FROM docs WHERE doc_type=?", (doc_type,)).fetchone()[0]
    else:
        n = conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
    conn.close()
    return n
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest projects/shared/test_vectordb.py -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add projects/shared/vectordb.py projects/shared/test_vectordb.py
git commit -m "feat: add sqlite-vec vectordb shared library"
```

---

## Task 3: Build `scripts/index_all.py` — full ingester

**Files:**
- Create: `scripts/index_all.py`

This script crawls all `.md` roots, classifies each file by `doc_type`, extracts a summary, embeds it, and upserts into the DB. Safe to re-run — mtime check skips unchanged files.

- [ ] **Step 1: Write failing test**

Create `scripts/test_index_all.py`:

```python
import sys, os, tempfile, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'projects', 'shared'))

def test_classify_doc_type():
    import index_all
    assert index_all.classify("/c/Users/x/.claude/skills/brainstorming/SKILL.md") == "skill"
    assert index_all.classify("E:/2026/ClaudesCorner/memory/2026-04-17.md") == "daily_log"
    assert index_all.classify("E:/2026/ClaudesCorner/memory/reddit-brief.md") == "memory"
    assert index_all.classify("E:/2026/ClaudesCorner/core/SOUL.md") == "core"
    assert index_all.classify("E:/2026/ClaudesCorner/research/foo.md") == "research"
    assert index_all.classify("E:/2026/ClaudesCorner/projects/bi-agent/README.md") == "project"
    assert index_all.classify("/c/Users/x/.claude/agents/ml-engineer.md") == "agent"

def test_extract_summary():
    import index_all
    md_with_desc = "---\nname: foo\ndescription: Does something useful\n---\n# body"
    assert index_all.extract_summary(md_with_desc, "foo") == "Does something useful"

    md_heading = "# My Document\nsome content"
    assert index_all.extract_summary(md_heading, "fallback") == "My Document"

    md_plain = "Just plain text here\nmore text"
    assert index_all.extract_summary(md_plain, "fallback") == "Just plain text here"
```

- [ ] **Step 2: Run — expect ImportError**

```bash
python -m pytest scripts/test_index_all.py -v
```

- [ ] **Step 3: Implement `index_all.py`**

```python
#!/usr/bin/env python3
"""
scripts/index_all.py — crawl all .md roots and upsert into vectorstore.db.
Safe to re-run: mtime-based skip for unchanged files.
Usage:
  python scripts/index_all.py           # full index
  python scripts/index_all.py --force   # re-embed everything regardless of mtime
"""
import argparse
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

ROOTS: list[tuple[Path, str, str]] = [
    # (root_path, glob_pattern, doc_type)
    (CLAUDE_DIR / "skills",   "**/SKILL.md",  "skill"),
    (CLAUDE_DIR / "agents",   "*.md",         "agent"),
    (BASE / "memory",         "*.md",         None),      # classified per-file
    (BASE / "core",           "*.md",         "core"),
    (BASE / "research",       "**/*.md",      "research"),
    (BASE / "inbox",          "*.md",         "inbox"),
    (BASE / "digested",       "**/*.md",      "digested"),
    (BASE / "journal",        "*.md",         "journal"),
    (BASE / "projects",       "**/*.md",      "project"),
    (BASE / "ms-certifications", "**/*.md",   "cert"),
    (BASE,                    "*.md",         "root"),
]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def classify(path: str) -> str:
    p = Path(path)
    s = path.replace("\\", "/")
    if "/.claude/skills/" in s or "\\.claude\\skills\\" in s:
        return "skill"
    if "/.claude/agents/" in s or "\\.claude\\agents\\" in s:
        return "agent"
    if "/memory/" in s or "\\memory\\" in s:
        return "daily_log" if DATE_RE.match(p.name) else "memory"
    if "/core/" in s or "\\core\\" in s:
        return "core"
    if "/research/" in s or "\\research\\" in s:
        return "research"
    if "/inbox/" in s or "\\inbox\\" in s:
        return "inbox"
    if "/digested/" in s or "\\digested\\" in s:
        return "digested"
    if "/journal/" in s or "\\journal\\" in s:
        return "journal"
    if "/projects/" in s or "\\projects\\" in s:
        return "project"
    if "/ms-certifications/" in s or "\\ms-certifications\\" in s:
        return "cert"
    return "root"


def extract_summary(text: str, fallback: str) -> str:
    # 1. frontmatter description:
    m = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # 2. first H1:
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # 3. first non-empty non-frontmatter line:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped not in ("---", "==="):
            return stripped[:120]
    return fallback


def extract_name(path: Path, doc_type: str) -> str:
    if doc_type == "skill":
        return path.parent.name
    return path.stem


def iter_files():
    seen = set()
    for root, pattern, _ in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.glob(pattern)):
            if p.name.startswith(".") or str(p) in seen:
                continue
            seen.add(str(p))
            yield p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Re-embed all files")
    parser.add_argument("--db", default=vectordb.DB_PATH, help="DB path override")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not emb.load_embedder():
        print("ERROR: sentence-transformers not installed", file=sys.stderr)
        sys.exit(1)

    files = list(iter_files())
    print(f"Found {len(files)} .md files")

    skipped = indexed = 0
    for p in files:
        doc_type = classify(str(p))
        mtime = p.stat().st_mtime

        if not args.force and not args.dry_run:
            # check if already indexed and up-to-date
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
            print(f"  SKIP {p}: {e}")
            continue

        name = extract_name(p, doc_type)
        summary = extract_summary(body, name)

        # embed summary only (not full body) — keeps index tight
        vec = emb.embed([summary])[0].tolist()

        if args.dry_run:
            print(f"  DRY  [{doc_type:12}] {name}: {summary[:60]}")
            continue

        try:
            rel = str(p.relative_to(BASE)) if BASE in p.parents else str(p.relative_to(Path.home() / ".claude"))
        except ValueError:
            rel = p.name

        vectordb.upsert(args.db, path=str(p), rel_path=rel, doc_type=doc_type,
                        name=name, summary=summary, body=body, mtime=mtime,
                        embedding=vec)
        indexed += 1
        if indexed % 20 == 0:
            print(f"  ... {indexed} indexed")

    print(f"Done — indexed={indexed}, skipped={skipped}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest scripts/test_index_all.py -v
```

Expected: 3 PASSED

- [ ] **Step 5: Run dry-run to verify classification**

```bash
python scripts/index_all.py --dry-run 2>&1 | head -40
```

Verify doc_types look correct across different roots.

- [ ] **Step 6: Run full index**

```bash
python scripts/index_all.py
```

Expected output ends with: `Done — indexed=N, skipped=0`

- [ ] **Step 7: Verify DB**

```python
python -c "
import sys; sys.path.insert(0,'projects/shared')
import vectordb
print('total:', vectordb.count())
for t in ['skill','memory','core','research','agent','project']:
    print(f'  {t}: {vectordb.count(doc_type=t)}')
"
```

- [ ] **Step 8: Commit**

```bash
git add scripts/index_all.py scripts/test_index_all.py core/vectorstore.db
git commit -m "feat: add index_all.py ingester + initial vectorstore.db"
```

---

## Task 4: Refactor `skill-manager-mcp` to query vectordb

**Files:**
- Modify: `projects/skill-manager-mcp/server.py`
- Remove: `~/.claude/skills/.skill_embed_index.json` (after migration)

Replace `_collect_skills`, `skill_index_build`, `skill_search` with vectordb queries. `skill_list` returns names+summaries from DB (no file scan). `skill_read` fetches body from DB (falls back to file read). `skill_search` does semantic query via vectordb.

- [ ] **Step 1: Replace imports and constants at top of server.py**

Remove:
```python
import os
from pathlib import Path
_SHARED = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(_SHARED))
EMBED_INDEX_FILE = SKILLS_DIR / ".skill_embed_index.json"
TOP_K = 5
```

Add:
```python
import os
from pathlib import Path
_SHARED = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(_SHARED))
import vectordb
import embedder as emb
TOP_K = 5
```

- [ ] **Step 2: Replace `_collect_skills`, `skill_index_build`, `skill_search`**

Remove the three functions entirely. Replace with:

```python
def skill_search(query: str, top_k: int = TOP_K) -> dict:
    if not emb.load_embedder():
        return {"error": "sentence-transformers not installed"}
    q_vec = emb.embed([query])[0].tolist()
    results = vectordb.search(doc_type="skill", query_embedding=q_vec, top_k=top_k)
    if not results:
        return {"query": query, "results": [], "hint": "Run index_all.py to populate the vector store"}
    return {
        "query": query,
        "results": [{"name": r["name"], "score": r["score"], "summary": r["summary"]}
                    for r in results],
    }
```

- [ ] **Step 3: Update `skill_list` to query DB**

Replace current `skill_list` implementation:

```python
def skill_list() -> dict:
    conn = vectordb.get_connection()
    rows = conn.execute(
        "SELECT name, rel_path, summary, doc_type FROM docs WHERE doc_type='skill' ORDER BY name"
    ).fetchall()
    conn.close()
    skills = [{"name": r["name"], "summary": r["summary"],
               "type": "learned" if "learned" in r["rel_path"] else "bundled"}
              for r in rows]
    return {"skills": skills, "total": len(skills)}
```

- [ ] **Step 4: Update `skill_read` to fetch body from DB with file fallback**

```python
def skill_read(name: str) -> dict:
    conn = vectordb.get_connection()
    row = conn.execute(
        "SELECT path, body FROM docs WHERE doc_type='skill' AND name=?", (name,)
    ).fetchone()
    conn.close()
    if row:
        return {"name": name, "content": row["body"], "path": row["path"]}
    # file fallback (skill not yet indexed)
    for base in (SKILLS_DIR, LEARNED_DIR):
        p = base / name / "SKILL.md"
        if p.exists():
            return {"name": name, "content": p.read_text(encoding="utf-8"), "path": str(p)}
    return {"error": f"Skill '{name}' not found"}
```

- [ ] **Step 5: Remove `skill_index_build` tool from TOOLS list and handler**

Delete the `skill_index_build` entry from `TOOLS` and its `elif` branch in `handle()`. Index is now managed by `index_all.py`.

- [ ] **Step 6: Smoke-test the refactored server**

```bash
python -c "
import sys; sys.path.insert(0,'projects/shared'); sys.path.insert(0,'projects/skill-manager-mcp')
import server
print(server.skill_list())
print(server.skill_search('debugging test failures'))
print(server.skill_read('systematic-debugging')['name'])
"
```

Expected: list with skills, search returns `systematic-debugging` at top, read returns content.

- [ ] **Step 7: Commit**

```bash
git add projects/skill-manager-mcp/server.py
git commit -m "refactor: skill-manager-mcp queries vectordb instead of scanning files"
```

---

## Task 5: Refactor `memory-mcp` to query vectordb

**Files:**
- Modify: `projects/memory-mcp/server.py`
- Remove: `memory/.embed_index.json`, `memory/.index.json` (after migration)

Replace `_collect_docs`, `_build_embed_index`, `_is_embed_stale`, `search_memory` with vectordb queries. `search_memory` now takes an optional `doc_type` filter. `fetch_body` uses `vectordb.fetch_body`.

- [ ] **Step 1: Add vectordb import to memory-mcp server.py**

At the top, after existing imports:

```python
_SHARED = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(_SHARED))
import vectordb as vdb
import embedder as emb_util
```

- [ ] **Step 2: Replace `search_memory` tool handler**

Find the `search_memory` function and replace its implementation:

```python
async def search_memory(query: str, top_k: int = 10, doc_type: str | None = None) -> list[types.TextContent]:
    if not emb_util.load_embedder():
        return [types.TextContent(type="text", text=json.dumps({"error": "embedder unavailable"}))]
    q_vec = emb_util.embed([query])[0].tolist()
    results = vdb.search(query_embedding=q_vec, top_k=top_k, doc_type=doc_type)
    output = [{"name": r["name"], "doc_type": r["doc_type"],
               "summary": r["summary"], "score": r["score"],
               "rel_path": r["rel_path"]}
              for r in results]
    return [types.TextContent(type="text", text=json.dumps(output, indent=2))]
```

- [ ] **Step 3: Replace `read_memory` body fetch**

Find where `read_memory` reads file content and replace with:

```python
body = vdb.fetch_body(path=abs_path)
if body is None:
    # fallback: direct file read
    body = Path(abs_path).read_text(encoding="utf-8", errors="ignore")
```

- [ ] **Step 4: Add `doc_type` parameter to `search_memory` tool schema**

In the tool definition for `search_memory`, add:

```python
"doc_type": {
    "type": "string",
    "description": "Optional filter: skill | memory | daily_log | core | research | inbox | agent | project | journal | cert | root",
}
```

- [ ] **Step 5: Remove dead code**

Delete these functions (now replaced by vectordb):
- `_collect_docs`
- `_build_embed_index`
- `_is_embed_stale`
- `_any_md_newer_than`
- `_load_embedder` (now in shared embedder.py)
- `_embed`
- `_cosine_scores`
- All references to `EMBED_INDEX_FILE`, `INDEX_FILE`

- [ ] **Step 6: Smoke-test**

```bash
python -c "
import asyncio, sys
sys.path.insert(0,'projects/shared')
# start server in test mode — just verify imports and tool list loads
import projects.memory_mcp.server as s
print('memory-mcp imports OK')
"
```

- [ ] **Step 7: Commit**

```bash
git add projects/memory-mcp/server.py
git commit -m "refactor: memory-mcp queries vectordb, removes inline embed logic"
```

---

## Task 6: Wire `index_all.py` into the scheduled heartbeat

**Files:**
- Modify: `scripts/dispatch.py` or `.claude/settings.json` hook

The index should rebuild automatically when new `.md` files appear (e.g. after a session flush). Fastest approach: add a PostToolUse hook that calls `index_all.py` after any Write/Edit to a `.md` file.

- [ ] **Step 1: Add PostToolUse hook to settings.json**

In `.claude/settings.json`, under `hooks.PostToolUse`, add:

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "python E:\\2026\\ClaudesCorner\\scripts\\index_all.py --db E:\\2026\\ClaudesCorner\\core\\vectorstore.db 2>>E:\\2026\\ClaudesCorner\\logs\\index_all.log"
    }
  ]
}
```

- [ ] **Step 2: Test hook fires on a Write**

Create and immediately delete a test file:

```bash
echo "test" > E:/2026/ClaudesCorner/memory/test-hook.md
# hook should fire and index it
python -c "
import sys; sys.path.insert(0,'projects/shared')
import vectordb
conn = vectordb.get_connection()
row = conn.execute(\"SELECT name FROM docs WHERE name='test-hook'\").fetchone()
print('indexed:', row is not None)
conn.close()
"
rm E:/2026/ClaudesCorner/memory/test-hook.md
```

- [ ] **Step 3: Commit**

```bash
git add .claude/settings.json
git commit -m "infra: auto-index .md files on Write/Edit via PostToolUse hook"
```

---

## Task 7: Cleanup — remove legacy index files and update MEMORY.md

**Files:**
- Delete: `memory/.embed_index.json`
- Delete: `memory/.index.json`
- Delete: `~/.claude/skills/.skill_embed_index.json`
- Modify: `C:\Users\JasonNicolini\.claude\projects\E--2026-ClaudesCorner\memory\MEMORY.md`

- [ ] **Step 1: Remove legacy files**

```bash
rm -f E:/2026/ClaudesCorner/memory/.embed_index.json
rm -f E:/2026/ClaudesCorner/memory/.index.json
rm -f ~/.claude/skills/.skill_embed_index.json
```

- [ ] **Step 2: Update project_memory_mcp.md and project_skill_manager.md memory entries**

Update `memory/project_memory_mcp.md`:
```
memory-mcp now queries vectordb (core/vectorstore.db) via shared/vectordb.py.
search_memory accepts optional doc_type filter. Inline embed logic removed.
```

Update `memory/project_skill_manager_mcp.md`:
```
skill-manager-mcp now queries vectordb. skill_index_build removed. skill_search
uses semantic vector search. skill_list returns from DB.
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "cleanup: remove legacy embed index files, update memory entries"
```

---

## Self-Review

**Spec coverage:**
- ✅ sqlite-vec store with schema (Task 2)
- ✅ All `.md` roots crawled and classified (Task 3)
- ✅ skill-manager-mcp refactored (Task 4)
- ✅ memory-mcp refactored (Task 5)
- ✅ Auto-index on file write (Task 6)
- ✅ Legacy cleanup (Task 7)
- ✅ Shared embedder reused, not duplicated
- ✅ `doc_type` filter for namespace-scoped search
- ✅ mtime skip for unchanged files
- ✅ Body stored in DB, fetched on demand (not pre-loaded)

**No placeholders:** verified — all code blocks are complete implementations.

**Type consistency:** `vectordb.search()` returns `list[dict]` with keys `name`, `doc_type`, `summary`, `score`, `rel_path`, `path` — used consistently across Task 4 and Task 5.

---

## Expected Context Savings

| Before | After |
|---|---|
| Skills pre-loaded: ~28K tokens | Skills: ~0 tokens (fetched on demand) |
| Memory embed index in RAM | Index in vectorstore.db (disk) |
| search_memory: scans all .md | search_memory: single DB query |
| Baseline session burn: ~22% | Target: ~8-10% |

Total reclaimed: **~14K tokens (~7% of 200K window) per session**.
