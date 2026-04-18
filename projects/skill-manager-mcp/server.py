"""
skill-manager-mcp/server.py

MCP server for skill management. Queries vectorstore.db for search/list.
File writes still go to ~/.claude/skills/ (source of truth for files).

Tools:
  skill_search    — semantic search via vectordb
  skill_read      — fetch full skill body (DB first, file fallback)
  skill_list      — list skills from DB
  skill_create    — write new skill file + upsert to DB
  skill_edit      — rewrite skill file + upsert to DB
  skill_patch     — find-and-replace in skill file + re-upsert to DB
  skill_catalog   — generate agent-skills.json manifest (/.well-known/ discovery)
  skill_deprecate — soft-delete from DB
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"
LEARNED_DIR = SKILLS_DIR / "learned"
TOP_K = 5

# vectordb lives in brain-memory project
_BRAIN = Path(__file__).parent.parent / "brain-memory" / "src"
sys.path.insert(0, str(_BRAIN))

import vectordb

DB_PATH = vectordb.DB_PATH


def _load_soul_vec() -> list[float] | None:
    try:
        import numpy as np
        p = Path(__file__).parent.parent.parent / "core" / "soul_vec.npy"
        if p.exists():
            return np.load(str(p)).tolist()
    except Exception:
        pass
    return None


def _embed(texts: list[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("all-MiniLM-L6-v2")
    return m.encode(texts, show_progress_bar=False).tolist()


def _extract_description(text: str, fallback: str) -> str:
    m = re.search(r'^description:\s*(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return fallback


def _extract_tags(text: str) -> list[str]:
    m = re.search(r'^tags:\s*(.+)$', text, re.MULTILINE)
    if not m:
        return []
    val = m.group(1).strip()
    if val.startswith("["):
        return re.findall(r'[\w-]+', val)
    return [val.strip()]


def _upsert_skill(name: str, path: Path, content: str) -> None:
    description = _extract_description(content, name)
    tags = _extract_tags(content)
    title = name.replace("-", " ").title()
    rel = str(path.relative_to(Path.home() / ".claude"))
    vec = _embed([description])[0]
    vectordb.upsert(
        path=str(path), rel_path=rel, doc_type="skill",
        name=name, title=title, description=description,
        body=content, tags=tags, mtime=path.stat().st_mtime,
        embedding=vec,
    )


# ── Tool implementations ─────────────────────────────────────────────────────

def skill_search(query: str, top_k: int = TOP_K) -> dict:
    try:
        soul = _load_soul_vec()
        q_vec = _embed([query])[0]
        results = vectordb.search(
            query_embedding=q_vec, query=query, top_k=top_k,
            doc_type="skill", status="active", soul_bias=soul,
        )
        if not results:
            return {"query": query, "results": [],
                    "hint": "Run: python projects/brain-memory/src/index_all.py --doc-type skill"}
        return {
            "query": query,
            "results": [{"name": r["name"], "title": r["title"],
                         "description": r["description"], "score": r["score"],
                         "tags": r["tags"]}
                        for r in results],
        }
    except Exception as e:
        return {"error": str(e)}


def skill_list(status: str = "active") -> dict:
    docs = vectordb.list_docs(doc_type="skill", status=status, limit=200)
    skills = [{"name": d["name"], "title": d["title"],
               "description": d["description"], "status": d["status"],
               "type": "learned" if "learned" in d.get("rel_path", "") else "bundled"}
              for d in docs]
    return {"skills": skills, "total": len(skills)}


def skill_read(name: str) -> dict:
    conn = vectordb.get_connection()
    row = conn.execute(
        "SELECT path, body, status FROM docs WHERE doc_type='skill' AND name=?", (name,)
    ).fetchone()
    # singleton — don't close
    if row:
        body = row["body"]
        if row["status"] == "deprecated":
            body = f"<!-- DEPRECATED -->\n\n{body}"
        return {"name": name, "content": body, "path": row["path"]}
    # file fallback
    for base in (SKILLS_DIR, LEARNED_DIR):
        p = base / name / "SKILL.md"
        if p.exists():
            return {"name": name, "content": p.read_text(encoding="utf-8"), "path": str(p)}
    return {"error": f"Skill '{name}' not found"}


def skill_create(name: str, content: str) -> dict:
    p = LEARNED_DIR / name / "SKILL.md"
    if p.exists():
        return {"error": f"Skill '{name}' already exists. Use skill_edit or skill_patch."}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    _upsert_skill(name, p, content)
    return {"created": str(p), "checksum": hashlib.md5(content.encode()).hexdigest(), "bytes": len(content)}


def skill_edit(name: str, content: str) -> dict:
    p = LEARNED_DIR / name / "SKILL.md"
    if not p.exists():
        bundled = SKILLS_DIR / name / "SKILL.md"
        if bundled.exists():
            return {"error": f"'{name}' is bundled. Use skill_create with name='{name}-override'."}
        return {"error": f"Skill '{name}' not found"}
    old = p.read_text(encoding="utf-8")
    p.write_text(content, encoding="utf-8")
    _upsert_skill(name, p, content)
    return {"edited": str(p), "old_bytes": len(old), "new_bytes": len(content)}


def skill_patch(name: str, old_string: str, new_string: str) -> dict:
    p = LEARNED_DIR / name / "SKILL.md"
    if not p.exists():
        return {"error": f"Skill '{name}' not found in learned/"}
    content = p.read_text(encoding="utf-8")
    if old_string not in content:
        return {"error": f"old_string not found in {name}/SKILL.md"}
    updated = content.replace(old_string, new_string, 1)
    p.write_text(updated, encoding="utf-8")
    _upsert_skill(name, p, updated)
    return {"patched": str(p), "replaced": old_string[:80]}


def skill_catalog(output_file: str = "") -> dict:
    """Generate agent-skills.json manifest for /.well-known/ discovery."""
    docs = vectordb.list_docs(doc_type="skill", status="active", limit=200)
    skills = []
    for d in docs:
        skill_type = "learned" if "learned" in d.get("rel_path", "") else "bundled"
        skills.append({
            "name": d["name"],
            "title": d["title"],
            "description": d["description"],
            "type": skill_type,
            "tags": d.get("tags") or [],
        })
    manifest = {
        "$schema": "https://agentskills.io/schema/v1/catalog.json",
        "name": "ClaudesCorner Skill Catalog",
        "description": "Jason Nicolini's personal AI assistant skill library",
        "version": "1.0",
        "skills": skills,
        "total": len(skills),
        "generated": datetime.now(timezone.utc).isoformat(),
    }
    if output_file:
        Path(output_file).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return {"written": output_file, "total": len(skills)}
    return manifest


def skill_deprecate(name: str, reason: str = "") -> dict:
    conn = vectordb.get_connection()
    row = conn.execute(
        "SELECT path FROM docs WHERE doc_type='skill' AND name=?", (name,)
    ).fetchone()
    # singleton — don't close
    if not row:
        return {"error": f"Skill '{name}' not found"}
    vectordb.deprecate(path=row["path"], reason=reason)
    return {"name": name, "status": "deprecated", "reason": reason}


# ── MCP protocol ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "skill_search",
        "description": "PRIMARY ENTRY POINT. Always call this first before any other skill tool. Semantic search returns names + scores without loading bodies — saves 40-60% tokens vs listing all skills. Call skill_read only after confirming a match here.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "skill_list",
        "description": "List all skills from vectordb (names + descriptions, no bodies).",
        "inputSchema": {
            "type": "object",
            "properties": {"status": {"type": "string", "default": "active"}},
            "required": [],
        },
    },
    {
        "name": "skill_read",
        "description": "Fetch full skill body by name.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "skill_create",
        "description": "Create a new learned skill. Writes file + indexes to vectordb.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["name", "content"],
        },
    },
    {
        "name": "skill_edit",
        "description": "Full rewrite of an existing learned skill. Updates file + vectordb.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["name", "content"],
        },
    },
    {
        "name": "skill_patch",
        "description": "Find-and-replace within a learned skill. Updates file + vectordb.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
            },
            "required": ["name", "old_string", "new_string"],
        },
    },
    {
        "name": "skill_catalog",
        "description": "Generate agent-skills.json manifest for /.well-known/ discovery. Returns full catalog of active skills. Pass output_file path to write to disk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "output_file": {"type": "string", "description": "Optional path to write JSON to disk"},
            },
            "required": [],
        },
    },
    {
        "name": "skill_deprecate",
        "description": "Soft-delete a skill. Excluded from search but preserved in DB.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["name"],
        },
    },
]


def handle(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "skill-manager", "version": "2.1.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = request["params"]["name"]
        args = request["params"].get("arguments", {})
        try:
            if name == "skill_search":
                result = skill_search(args["query"], top_k=args.get("top_k", TOP_K))
            elif name == "skill_list":
                result = skill_list(status=args.get("status", "active"))
            elif name == "skill_read":
                result = skill_read(args["name"])
            elif name == "skill_create":
                result = skill_create(args["name"], args["content"])
            elif name == "skill_edit":
                result = skill_edit(args["name"], args["content"])
            elif name == "skill_patch":
                result = skill_patch(args["name"], args["old_string"], args["new_string"])
            elif name == "skill_catalog":
                result = skill_catalog(output_file=args.get("output_file", ""))
            elif name == "skill_deprecate":
                result = skill_deprecate(args["name"], args.get("reason", ""))
            else:
                result = {"error": f"Unknown tool: {name}"}
        except Exception as e:
            result = {"error": str(e)}

        is_error = "error" in result
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                "isError": is_error,
            },
        }

    if method == "notifications/initialized":
        return None

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(req)
        if resp is not None:
            print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
