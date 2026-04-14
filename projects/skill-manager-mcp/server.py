"""
skill-manager-mcp/server.py

MCP server giving Claude autonomous skill management tools.
Modeled on Hermes Agent's skill_manager_tool pattern.

Tools:
  skill_create  — write a new skill to ~/.claude/skills/<name>/SKILL.md
  skill_patch   — targeted find-and-replace within an existing skill
  skill_edit    — full rewrite of an existing skill
  skill_list    — list all skills (bundled + learned)
  skill_read    — read a skill by name

Skills are written to:
  - ~/.claude/skills/<name>/SKILL.md   (for production skills)
  - ~/.claude/skills/learned/<name>/SKILL.md  (for agent-created skills)

Security: agent-created skills are isolated in the learned/ subdirectory.
"""

import hashlib
import json
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"
LEARNED_DIR = SKILLS_DIR / "learned"


def _skill_path(name: str, learned: bool = True) -> Path:
    base = LEARNED_DIR if learned else SKILLS_DIR
    return base / name / "SKILL.md"


def skill_list() -> dict:
    skills = []
    for p in sorted(SKILLS_DIR.rglob("SKILL.md")):
        rel = p.relative_to(SKILLS_DIR)
        parts = rel.parts
        tag = "learned" if "learned" in parts else "bundled"
        skills.append({"name": parts[0], "path": str(p), "type": tag})
    return {"skills": skills, "total": len(skills)}


def skill_read(name: str) -> dict:
    for base in (SKILLS_DIR, LEARNED_DIR):
        p = base / name / "SKILL.md"
        if p.exists():
            return {"name": name, "content": p.read_text(encoding="utf-8"), "path": str(p)}
    return {"error": f"Skill '{name}' not found"}


def skill_create(name: str, content: str) -> dict:
    p = _skill_path(name, learned=True)
    if p.exists():
        return {"error": f"Skill '{name}' already exists at {p}. Use skill_edit or skill_patch."}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    checksum = hashlib.md5(content.encode()).hexdigest()
    return {"created": str(p), "checksum": checksum, "bytes": len(content)}


def skill_edit(name: str, content: str) -> dict:
    p = _skill_path(name, learned=True)
    # Allow editing bundled skills too (but warn)
    if not p.exists():
        bundled = SKILLS_DIR / name / "SKILL.md"
        if bundled.exists():
            return {"error": f"'{name}' is a bundled skill. Create a learned override instead with skill_create using name='{name}-override'."}
        return {"error": f"Skill '{name}' not found"}
    old = p.read_text(encoding="utf-8")
    p.write_text(content, encoding="utf-8")
    return {"edited": str(p), "old_bytes": len(old), "new_bytes": len(content)}


def skill_patch(name: str, old_string: str, new_string: str) -> dict:
    p = _skill_path(name, learned=True)
    if not p.exists():
        return {"error": f"Skill '{name}' not found in learned/"}
    content = p.read_text(encoding="utf-8")
    if old_string not in content:
        return {"error": f"old_string not found in {name}/SKILL.md"}
    updated = content.replace(old_string, new_string, 1)
    p.write_text(updated, encoding="utf-8")
    return {"patched": str(p), "replaced": old_string[:80]}


# ── MCP protocol ────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "skill_list",
        "description": "List all available skills (bundled + learned). Use to see what skills exist before creating duplicates.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "skill_read",
        "description": "Read a skill's SKILL.md content by name.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Skill directory name"}},
            "required": ["name"],
        },
    },
    {
        "name": "skill_create",
        "description": "Create a new learned skill. Writes to ~/.claude/skills/learned/<name>/SKILL.md. Use when you identify a reusable pattern worth saving.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Skill name (kebab-case, e.g. 'fabric-dax-review')"},
                "content": {"type": "string", "description": "Full SKILL.md content"},
            },
            "required": ["name", "content"],
        },
    },
    {
        "name": "skill_edit",
        "description": "Full rewrite of an existing learned skill.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "content": {"type": "string", "description": "New full SKILL.md content"},
            },
            "required": ["name", "content"],
        },
    },
    {
        "name": "skill_patch",
        "description": "Targeted find-and-replace within an existing learned skill. Faster than skill_edit for small changes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "old_string": {"type": "string", "description": "Text to find"},
                "new_string": {"type": "string", "description": "Replacement text"},
            },
            "required": ["name", "old_string", "new_string"],
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
                "serverInfo": {"name": "skill-manager", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = request["params"]["name"]
        args = request["params"].get("arguments", {})
        try:
            if name == "skill_list":
                result = skill_list()
            elif name == "skill_read":
                result = skill_read(args["name"])
            elif name == "skill_create":
                result = skill_create(args["name"], args["content"])
            elif name == "skill_edit":
                result = skill_edit(args["name"], args["content"])
            elif name == "skill_patch":
                result = skill_patch(args["name"], args["old_string"], args["new_string"])
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
