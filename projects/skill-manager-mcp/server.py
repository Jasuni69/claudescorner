"""
skill-manager-mcp/server.py

MCP server for skill management. Queries vectorstore.db for search/list.
File writes still go to ~/.claude/skills/ (source of truth for files).

Skill frontmatter follows the agentskills.io SKILL.md open standard
(convergently validated by Hermes Agent 102k+ stars and anthropics/skills):

  ---
  name: skill-name
  description: "One-line trigger description"
  version: "1.0.0"
  tools: [Read, Edit, Bash]
  parameters:
    - name: param_name
      description: "What it does"
      required: true
  ---

Minimum required fields: name, description. All others are optional but
recommended for agent-skills.json catalog interoperability.

Two-layer governance (HuggingFace/skills pattern, v2.4.0+):
  marketplace.json — human-readable browsing layer (title, summary, use_when, category)
  SKILL.md         — agent-activation layer (full instructions, tools, parameters)

  agent_activation_allowed: true/false frontmatter flag controls autonomous access.
  skill_search(context="autonomous") filters to allowed=true only.
  Skills without the flag default to allowed=true (backward-compatible).

Injection guard (v2.5.0+):
  skill_create and skill_edit scan content for scope-redefinition/injection patterns
  before writing. Fail-closed: blocked skills return an error and are never stored.
  Patterns: ignore/disregard/forget previous instructions, you are now, new system prompt,
  act as alternative, new persona, <system>, [SYSTEM], JAILBREAK.

Credential scan (v2.6.0+):
  skill_create and skill_edit scan content for embedded credentials before writing.
  Fail-closed: skills containing raw secrets return an error and are never stored.
  Patterns: API keys (sk-/ghp_/xoxb-/eyJ...), Bearer tokens, password= assignments,
  secret= assignments, high-entropy 40+ char alphanum strings.

Tools:
  skill_search           — semantic search via vectordb (PRIMARY ENTRY POINT)
  skill_read             — fetch full skill body (DB first, file fallback)
  skill_list             — list skills from DB
  skill_create           — write new skill file + upsert to DB
  skill_edit             — rewrite skill file + upsert to DB
  skill_patch            — find-and-replace in skill file + re-upsert to DB
  skill_catalog          — generate agent-skills.json manifest (/.well-known/ discovery)
  skill_deprecate        — soft-delete from DB
  skill_marketplace_list — list marketplace.json human layer (browsing, no SKILL.md bodies)
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_DIR = Path.home() / ".claude" / "skills"
MARKETPLACE_JSON = Path(__file__).parent / "marketplace.json"
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


def _extract_version(text: str) -> str:
    """Extract version field from agentskills.io frontmatter."""
    m = re.search(r'^version:\s*["\']?([^\s"\']+)["\']?$', text, re.MULTILINE)
    return m.group(1).strip() if m else "1.0.0"


_CREDENTIAL_PATTERNS = [
    r'\bsk-[A-Za-z0-9_\-]{20,}',           # OpenAI / Anthropic API keys
    r'\bghp_[A-Za-z0-9]{36,}',             # GitHub personal access tokens
    r'\bgho_[A-Za-z0-9]{36,}',             # GitHub OAuth tokens
    r'\bxoxb-[0-9A-Za-z\-]{50,}',          # Slack bot tokens
    r'\bxoxp-[0-9A-Za-z\-]{50,}',          # Slack user tokens
    r'\beyJ[A-Za-z0-9_\-]{40,}',           # JWT bearer tokens
    r'\bBearer\s+[A-Za-z0-9_\-\.]{20,}',   # Bearer token in value position
    r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']{8,}["\']',   # password=".." assignments
    r'(?:secret|api_?key|auth_?token)\s*=\s*["\'][^"\']{8,}["\']',  # secret="..." assignments
    r'(?<![a-z])[A-Za-z0-9+/]{40,}(?:[A-Za-z0-9]{0,4}={0,2})(?![a-z])',  # high-entropy b64
]
_CREDENTIAL_RE = re.compile(
    '|'.join(_CREDENTIAL_PATTERNS), re.IGNORECASE
)

_ALLOWLIST_RE = re.compile(
    r'(?:example|placeholder|your[-_]?(?:api[-_]?)?key|<[^>]+>|xxx|000)',
    re.IGNORECASE
)


def _check_credentials(content: str) -> str | None:
    """Return matched pattern string if embedded credential detected, else None."""
    for m in _CREDENTIAL_RE.finditer(content):
        hit = m.group(0)
        if _ALLOWLIST_RE.search(hit):
            continue
        return hit[:60]
    return None


_INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions',
    r'disregard\s+(all\s+)?previous',
    r'forget\s+(all\s+)?previous',
    r'override\s+(all\s+)?(previous|above|prior)',
    r'you\s+are\s+now\b',
    r'new\s+(system\s+)?prompt',
    r'act\s+as\s+a?\s*(?:different|new|alternative)',
    r'new\s+persona',
    r'<\s*system\s*>',
    r'\[SYSTEM\]',
    r'\bJAILBREAK\b',
]
_INJECTION_RE = re.compile(
    '|'.join(_INJECTION_PATTERNS), re.IGNORECASE | re.DOTALL
)


def _check_injection(content: str) -> str | None:
    """Return matched pattern string if injection detected, else None."""
    m = _INJECTION_RE.search(content)
    if m:
        return m.group(0)[:80]
    return None


def _extract_agent_activation(text: str) -> bool:
    """Extract agent_activation_allowed field; defaults to True if absent (backward-compat)."""
    m = re.search(r'^agent_activation_allowed:\s*(true|false)\s*$', text, re.MULTILINE | re.IGNORECASE)
    if m:
        return m.group(1).lower() == "true"
    return True  # default: allowed (preserves existing skill behavior)


def _extract_tools(text: str) -> list[str]:
    """Extract tools list from agentskills.io frontmatter (inline array or multiline)."""
    m = re.search(r'^tools:\s*\[([^\]]*)\]', text, re.MULTILINE)
    if m:
        return [t.strip().strip('"\'') for t in m.group(1).split(",") if t.strip()]
    # multiline YAML list: `tools:\n  - Read\n  - Edit`
    m2 = re.search(r'^tools:\s*\n((?:[ \t]+-[^\n]+\n?)+)', text, re.MULTILINE)
    if m2:
        return [re.sub(r'^[ \t]+-\s*', '', line).strip()
                for line in m2.group(1).splitlines() if line.strip()]
    return []


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

def skill_search(query: str, top_k: int = TOP_K, context: str = "interactive") -> dict:
    """Semantic skill search.

    Args:
        query:   Natural-language description of the task.
        top_k:   Number of results to return.
        context: "interactive" (default) returns all active skills.
                 "autonomous" returns only skills where agent_activation_allowed=true.
                 Use "autonomous" for dispatch workers and unattended agents.
    """
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

        if context == "autonomous":
            # Filter to skills that are explicitly agent-activatable.
            # Skills without the flag default to allowed (backward-compat).
            filtered = [r for r in results if _extract_agent_activation(r.get("body", ""))]
            blocked = len(results) - len(filtered)
            results = filtered
            if not results:
                return {"query": query, "results": [], "context": "autonomous",
                        "hint": f"{blocked} skill(s) found but none have agent_activation_allowed: true"}

        out = {
            "query": query,
            "context": context,
            "results": [{"name": r["name"], "title": r["title"],
                         "description": r["description"], "score": r["score"],
                         "tags": r["tags"],
                         "agent_activation_allowed": _extract_agent_activation(r.get("body", ""))}
                        for r in results],
        }
        if context == "autonomous":
            out["governance"] = "autonomous context: only agent_activation_allowed=true skills returned"
        return out
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
    hit = _check_injection(content)
    if hit:
        return {"error": f"[injection-guard]: suspicious pattern detected: {hit!r}"}
    cred = _check_credentials(content)
    if cred:
        return {"error": f"[credential-scan]: embedded secret detected: {cred!r}"}
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
    hit = _check_injection(content)
    if hit:
        return {"error": f"[injection-guard]: suspicious pattern detected: {hit!r}"}
    cred = _check_credentials(content)
    if cred:
        return {"error": f"[credential-scan]: embedded secret detected: {cred!r}"}
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
    """Generate agent-skills.json manifest for /.well-known/ discovery (agentskills.io v1 format)."""
    docs = vectordb.list_docs(doc_type="skill", status="active", limit=200)
    skills = []
    for d in docs:
        skill_type = "learned" if "learned" in d.get("rel_path", "") else "bundled"
        body = d.get("body") or ""
        skills.append({
            "name": d["name"],
            "title": d["title"],
            "description": d["description"],
            "version": _extract_version(body),
            "tools": _extract_tools(body),
            "type": skill_type,
            "tags": d.get("tags") or [],
            "agent_activation_allowed": _extract_agent_activation(body),
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


def skill_marketplace_list(category: str = "", search: str = "") -> dict:
    """Return the human-readable marketplace layer (no SKILL.md bodies).

    Separate from skill_list / skill_search which operate on the agent-activation
    layer (vectordb + SKILL.md). This is the browsing layer for humans: title,
    summary, use_when, category. Pattern from huggingface/skills marketplace.json.
    """
    if not MARKETPLACE_JSON.exists():
        return {"error": f"marketplace.json not found at {MARKETPLACE_JSON}"}
    data = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    skills = data.get("skills", [])
    if category:
        skills = [s for s in skills if s.get("category") == category]
    if search:
        q = search.lower()
        skills = [
            s for s in skills
            if q in s.get("name", "").lower()
            or q in s.get("title", "").lower()
            or q in s.get("summary", "").lower()
            or q in s.get("use_when", "").lower()
        ]
    return {
        "marketplace": data.get("name"),
        "governance": data.get("governance", {}).get("note"),
        "categories": data.get("categories", {}),
        "skills": skills,
        "total": len(skills),
        "hint": "These are human-readable descriptions. Call skill_search for agent-activation content (SKILL.md).",
    }


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
        "description": "PRIMARY ENTRY POINT. Always call this first before any other skill tool. Semantic search returns names + scores without loading bodies — saves 40-60% tokens vs listing all skills. Call skill_read only after confirming a match here. Pass context='autonomous' in dispatch workers to enforce agent_activation_allowed governance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
                "context": {
                    "type": "string",
                    "enum": ["interactive", "autonomous"],
                    "default": "interactive",
                    "description": "'interactive' returns all skills. 'autonomous' filters to agent_activation_allowed=true only (use in dispatch workers and unattended agents).",
                },
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
        "description": "Create a new learned skill. Writes SKILL.md + indexes to vectordb. Use agentskills.io frontmatter: name, description (required); version, tools, parameters (recommended for catalog interop).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Kebab-case skill identifier"},
                "content": {"type": "string", "description": "Full SKILL.md content with agentskills.io frontmatter"},
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
    {
        "name": "skill_marketplace_list",
        "description": "HUMAN BROWSING LAYER. Returns marketplace.json descriptions (title, summary, use_when, category) without loading SKILL.md bodies. Use this when a human wants to browse available skills. Use skill_search when an agent needs to activate a skill.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filter by category: planning, engineering, infrastructure, memory, meta",
                },
                "search": {
                    "type": "string",
                    "description": "Substring filter across name, title, summary, use_when",
                },
            },
            "required": [],
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
                "serverInfo": {"name": "skill-manager", "version": "2.6.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = request["params"]["name"]
        args = request["params"].get("arguments", {})
        try:
            if name == "skill_search":
                result = skill_search(args["query"], top_k=args.get("top_k", TOP_K),
                                      context=args.get("context", "interactive"))
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
            elif name == "skill_marketplace_list":
                result = skill_marketplace_list(
                    category=args.get("category", ""),
                    search=args.get("search", ""),
                )
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
