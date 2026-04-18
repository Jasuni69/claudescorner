# Markdown to VectorDB Migration
## Company-Wide Skill Sharing via Azure AI Search

> **Purpose:** Migrate local Claude Code skills (`.md` files) into a centralized Azure AI Search vector index, enabling semantic search and discovery of skills across every developer and agent at Numberskills AB.
>
> **Status:** Architecture + implementation guide. Ready to build.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Architecture Overview](#2-architecture-overview)
3. [Technology Decisions](#3-technology-decisions)
4. [Data Model](#4-data-model)
5. [Azure AI Search Setup](#5-azure-ai-search-setup)
6. [Embedding Strategy](#6-embedding-strategy)
7. [MCP Server: company-skills-mcp](#7-mcp-server-company-skills-mcp)
8. [The Bootstrap Skill: query-company-skills](#8-the-bootstrap-skill-query-company-skills)
9. [Migration Pipeline](#9-migration-pipeline)
10. [Sync & Governance](#10-sync--governance)
11. [Auth & Access Control](#11-auth--access-control)
12. [Teams Digest Integration](#12-teams-digest-integration)
13. [Deployment Checklist](#13-deployment-checklist)
14. [Cost Model](#14-cost-model)
15. [Future Roadmap](#15-future-roadmap)

---

## 1. Problem Statement

### Current State

Every Claude Code installation at Numberskills maintains a local skill library under `~/.claude/skills/`. Skills are markdown files that teach Claude how to perform repeatable tasks: querying Fabric lakehouses, generating DAX measures, running security audits, etc.

**The problem:**
- A skill written by one developer is invisible to every other developer and agent.
- Corrections and improvements are not propagated.
- Bad patterns spread independently — there is no single source of truth.
- Onboarding a new developer means manually copying skills.
- Agents running in background dispatch jobs have no way to discover what skills exist.

### Target State

A centralized Azure AI Search index contains every approved skill. Any agent or developer queries it with plain English. The best matching skill is fetched and executed locally. Skills written by one person propagate company-wide within minutes.

```
Developer A writes skill → skill_push → Azure AI Search index
Developer B's agent → query_company_skills("how to query lakehouse") → gets skill → executes
```

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    NUMBERSKILLS AB                               │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  Dev A       │    │  Dev B       │    │  Agent Pool  │       │
│  │  Claude Code │    │  Claude Code │    │  (dispatch)  │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │               │
│         └───────────────────┴───────────────────┘               │
│                             │                                   │
│                    company-skills-mcp                           │
│                    (local MCP server)                           │
│                             │                                   │
│              ┌──────────────▼──────────────┐                   │
│              │   AZURE AI SEARCH           │                   │
│              │   skills-index              │                   │
│              │                             │                   │
│              │  ┌─────────────────────┐    │                   │
│              │  │ skill documents     │    │                   │
│              │  │ + vector embeddings │    │                   │
│              │  └─────────────────────┘    │                   │
│              └─────────────────────────────┘                   │
│                             │                                   │
│              ┌──────────────▼──────────────┐                   │
│              │   AZURE OPENAI              │                   │
│              │   text-embedding-3-small    │                   │
│              │   (embedding generation)    │                   │
│              └─────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Component Roles

| Component | Role |
|-----------|------|
| `company-skills-mcp` | Local MCP server running on each dev machine. Wraps Azure AI Search REST API. |
| Azure AI Search | Managed vector + keyword search. Stores skill documents + embeddings. |
| Azure OpenAI | Generates embeddings for new skills and queries. |
| `query-company-skills` skill | Bootstrap skill shipped with every install. Entry point for skill discovery. |
| GitHub repo (claudescorner) | Canonical source of truth for approved skills. Push here triggers sync. |
| `scripts/skill_sync.py` | CLI tool + CI step. Reads markdown files, generates embeddings, upserts to index. |

---

## 3. Technology Decisions

### Azure AI Search over ChromaDB

| Concern | Azure AI Search | ChromaDB on Container Apps |
|---------|----------------|---------------------------|
| Auth | Entra ID / AAD natively | Custom, roll your own |
| Infra | Zero — fully managed | Container + persistent disk |
| Hybrid search | Built in (keyword + vector) | Vector only by default |
| Azure ecosystem fit | Native | Grafted |
| Cost (Free tier) | Free up to 50MB / 3 indexes | ~$20/mo for container |
| Scale ceiling | Millions of docs | Millions of docs |
| Latency | ~100ms | ~50ms |

**Decision: Azure AI Search Basic tier ($25/mo).** Free tier (50MB) hits the ceiling fast once embeddings are stored — 1536-dim float32 vectors are ~6KB per skill. At 500 skills that's ~3MB of vectors alone, plus document storage. Basic tier gives 2GB and eliminates the ceiling concern.

### Azure OpenAI over local embeddings

Local `all-MiniLM-L6-v2` (384-dim) is adequate for personal use but produces weaker cross-domain similarity for technical content. `text-embedding-3-small` (1536-dim) significantly outperforms it on coding/technical retrieval benchmarks and costs ~$0.02 per 1M tokens — negligible for a skills corpus.

**Decision: Azure OpenAI `text-embedding-3-small`.**

If Azure OpenAI is not provisioned, fall back to `text-embedding-ada-002` or local `all-MiniLM-L6-v2` via the same interface.

---

## 4. Data Model

### Skill Document Schema

Each skill is stored as a document in the `skills-v1` Azure AI Search index.

```json
{
  "id": "sha256-first-16-chars-of-skill-body",
  "name": "query-lakehouse-dax",
  "title": "Query a Fabric Lakehouse with DAX",
  "description": "How to write and execute DAX queries against a Fabric lakehouse SQL endpoint from Claude Code",
  "body": "---\nfrontmatter...\n---\n\n# Full skill markdown here",
  "tags": ["fabric", "dax", "lakehouse", "sql"],
  "namespace": "fabric",
  "author": "jason.nicolini@numberskills.se",
  "source_repo": "claudescorner",
  "source_path": "skills/query-lakehouse-dax/SKILL.md",
  "status": "approved",
  "created_at": "2026-04-17T00:00:00Z",
  "updated_at": "2026-04-17T00:00:00Z",
  "version": 3,
  "embedding": [0.021, -0.043, ...]
}
```

### Field Notes

| Field | Type | Notes |
|-------|------|-------|
| `id` | String | SHA256(name + body)[:16]. Stable across renames. |
| `name` | String | Slug. Used for `skill_get` lookups. Must be unique. |
| `title` | String | Human-readable. Used in search result display. |
| `description` | String | One-line. **This is what gets embedded** — not the full body. |
| `body` | String | Full skill markdown. Retrieved on demand, not in search results. |
| `tags` | Collection(String) | Filterable. Namespace scoping. |
| `namespace` | String | `fabric`, `dax`, `python`, `infra`, `general` |
| `status` | String | `draft`, `approved`, `deprecated` |
| `embedding` | Collection(Single) | 1536-dim. Indexed as vector field. |

### Index Configuration (Azure AI Search)

```json
{
  "name": "skills-v1",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true, "filterable": true},
    {"name": "name", "type": "Edm.String", "searchable": true, "filterable": true},
    {"name": "title", "type": "Edm.String", "searchable": true},
    {"name": "description", "type": "Edm.String", "searchable": true},
    {"name": "tags", "type": "Collection(Edm.String)", "filterable": true, "facetable": true},
    {"name": "namespace", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "author", "type": "Edm.String", "filterable": true},
    {"name": "status", "type": "Edm.String", "filterable": true},
    {"name": "created_at", "type": "Edm.DateTimeOffset", "sortable": true},
    {"name": "updated_at", "type": "Edm.DateTimeOffset", "sortable": true},
    {"name": "version", "type": "Edm.Int32", "sortable": true},
    {"name": "body", "type": "Edm.String", "retrievable": true, "searchable": false},
    {
      "name": "embedding",
      "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchProfile": "hnsw-profile",
      "searchable": true
    }
  ],
  "vectorSearch": {
    "algorithms": [{"name": "hnsw-algo", "kind": "hnsw"}],
    "profiles": [{"name": "hnsw-profile", "algorithm": "hnsw-algo"}]
  }
}
```

---

## 5. Azure AI Search Setup

### Step 1 — Provision the resource

```bash
# Create resource group (if needed)
az group create --name rg-numberskills-ai --location swedencentral

# Create AI Search (Basic tier)
az search service create \
  --name numberskills-skills-search \
  --resource-group rg-numberskills-ai \
  --sku Basic \
  --location swedencentral \
  --partition-count 1 \
  --replica-count 1
```

### Step 2 — Get the admin key

```bash
az search admin-key show \
  --service-name numberskills-skills-search \
  --resource-group rg-numberskills-ai \
  --query primaryKey -o tsv
```

Store as `AZURE_SEARCH_KEY` in your environment / `.env`.

Also note the endpoint:
```
AZURE_SEARCH_ENDPOINT=https://numberskills-skills-search.search.windows.net
```

### Step 3 — Create the index

```bash
curl -X POST \
  "$AZURE_SEARCH_ENDPOINT/indexes?api-version=2024-05-01-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: $AZURE_SEARCH_KEY" \
  -d @scripts/search_index_schema.json
```

Where `scripts/search_index_schema.json` contains the schema from section 4.

### Step 4 — Provision Azure OpenAI (if not already)

```bash
az cognitiveservices account create \
  --name numberskills-openai \
  --resource-group rg-numberskills-ai \
  --kind OpenAI \
  --sku S0 \
  --location swedencentral

# Deploy the embedding model
az cognitiveservices account deployment create \
  --name numberskills-openai \
  --resource-group rg-numberskills-ai \
  --deployment-name text-embedding-3-small \
  --model-name text-embedding-3-small \
  --model-version "1" \
  --model-format OpenAI \
  --sku-capacity 50 \
  --sku-name Standard
```

---

## 6. Embedding Strategy

### What to embed

**Embed the `description` field only, not the full body.**

Reasons:
- Description is a single focused sentence — maximum signal, minimum noise.
- Body contains implementation details (code blocks, step numbers) that degrade similarity.
- Smaller embedding input = lower cost and faster retrieval.
- At query time, the user's natural language query maps cleanly onto description-space.

### Embedding generation

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

def embed(text: str) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding
```

### Batching

When running the initial migration of many skills, batch embed calls in groups of 16 to avoid rate limits:

```python
def embed_batch(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]
```

### Embedding freshness

Re-embed whenever `description` changes. `body`-only changes do not require re-embedding. The sync script (`skill_sync.py`) handles this by comparing SHA256 of description field before deciding to re-embed.

---

## 7. MCP Server: company-skills-mcp

### Location

```
projects/company-skills-mcp/
├── server.py
├── requirements.txt
├── .env.example
└── README.md
```

### Tools exposed

| Tool | Args | Returns |
|------|------|---------|
| `skill_search` | `query: str`, `top_k: int = 5`, `namespace: str = None`, `status: str = "approved"` | List of `{name, title, description, score, tags}` |
| `skill_get` | `name: str` | Full skill body (markdown string) |
| `skill_push` | `name: str`, `body: str`, `description: str`, `tags: list[str]`, `namespace: str` | Upserted document ID |
| `skill_list` | `namespace: str = None`, `tag: str = None` | List of `{name, title, description, status}` |
| `skill_deprecate` | `name: str`, `reason: str` | Updated document |

### server.py

```python
"""
company-skills-mcp/server.py

MCP server wrapping Azure AI Search for company-wide skill discovery.

Environment variables required:
  AZURE_SEARCH_ENDPOINT   — e.g. https://numberskills-skills-search.search.windows.net
  AZURE_SEARCH_KEY        — admin or query key
  AZURE_OPENAI_ENDPOINT   — e.g. https://numberskills-openai.openai.azure.com
  AZURE_OPENAI_KEY        — API key
  AZURE_OPENAI_DEPLOYMENT — defaults to text-embedding-3-small
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional

import httpx
from openai import AzureOpenAI
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("company-skills")

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]
SEARCH_INDEX = "skills-v1"
API_VERSION = "2024-05-01-preview"

_openai = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)
EMBED_MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "text-embedding-3-small")


def _embed(text: str) -> list[float]:
    return _openai.embeddings.create(input=text, model=EMBED_MODEL).data[0].embedding


def _search_url(path: str) -> str:
    return f"{SEARCH_ENDPOINT}/indexes/{SEARCH_INDEX}/{path}?api-version={API_VERSION}"


def _headers() -> dict:
    return {"Content-Type": "application/json", "api-key": SEARCH_KEY}


@mcp.tool()
def skill_search(
    query: str,
    top_k: int = 5,
    namespace: Optional[str] = None,
    status: str = "approved"
) -> list[dict]:
    """Semantic search for skills matching a natural language query."""
    vector = _embed(query)
    body: dict = {
        "count": True,
        "top": top_k,
        "select": "name,title,description,tags,namespace,author,score",
        "vectorQueries": [{
            "kind": "vector",
            "vector": vector,
            "fields": "embedding",
            "k": top_k
        }],
        "filter": f"status eq '{status}'"
            + (f" and namespace eq '{namespace}'" if namespace else "")
    }
    r = httpx.post(_search_url("docs/search"), headers=_headers(), json=body)
    r.raise_for_status()
    return [
        {
            "name": d["name"],
            "title": d["title"],
            "description": d["description"],
            "tags": d.get("tags", []),
            "score": d.get("@search.score", 0)
        }
        for d in r.json().get("value", [])
    ]


@mcp.tool()
def skill_get(name: str) -> str:
    """Fetch the full body of a skill by name."""
    r = httpx.get(
        _search_url(f"docs('{name}')"),
        headers=_headers(),
        params={"$select": "body,name,title,status"}
    )
    if r.status_code == 404:
        return f"Skill '{name}' not found."
    r.raise_for_status()
    doc = r.json()
    if doc.get("status") == "deprecated":
        return f"# DEPRECATED\n\n{doc['body']}"
    return doc["body"]


@mcp.tool()
def skill_push(
    name: str,
    body: str,
    description: str,
    tags: list[str],
    namespace: str = "general"
) -> dict:
    """Publish or update a skill in the company index. Status defaults to 'draft'."""
    doc_id = hashlib.sha256(f"{name}{body}".encode()).hexdigest()[:16]
    vector = _embed(description)
    doc = {
        "id": doc_id,
        "name": name,
        "title": name.replace("-", " ").title(),
        "description": description,
        "body": body,
        "tags": tags,
        "namespace": namespace,
        "author": os.environ.get("SKILL_AUTHOR", "unknown"),
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "version": 1,
        "embedding": vector
    }
    r = httpx.post(
        _search_url("docs/index"),
        headers=_headers(),
        json={"value": [{**doc, "@search.action": "mergeOrUpload"}]}
    )
    r.raise_for_status()
    return {"id": doc_id, "name": name, "status": "draft", "message": "Pushed. Pending approval."}


@mcp.tool()
def skill_list(
    namespace: Optional[str] = None,
    tag: Optional[str] = None,
    status: str = "approved"
) -> list[dict]:
    """Browse skills by namespace or tag."""
    filters = [f"status eq '{status}'"]
    if namespace:
        filters.append(f"namespace eq '{namespace}'")
    if tag:
        filters.append(f"tags/any(t: t eq '{tag}')")

    body = {
        "top": 100,
        "select": "name,title,description,tags,namespace,author,updated_at",
        "filter": " and ".join(filters),
        "orderby": "updated_at desc"
    }
    r = httpx.post(_search_url("docs/search"), headers=_headers(), json=body)
    r.raise_for_status()
    return r.json().get("value", [])


@mcp.tool()
def skill_deprecate(name: str, reason: str) -> dict:
    """Mark a skill as deprecated. It remains in the index but won't appear in searches."""
    r = httpx.post(
        _search_url("docs/index"),
        headers=_headers(),
        json={"value": [{
            "@search.action": "merge",
            "name": name,
            "status": "deprecated",
            "body": f"<!-- DEPRECATED: {reason} -->\n\n" + "{original body preserved}"
        }]}
    )
    r.raise_for_status()
    return {"name": name, "status": "deprecated", "reason": reason}


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### requirements.txt

```
mcp[cli]>=1.0
httpx>=0.27
openai>=1.30
python-dotenv>=1.0
```

### Wire into Claude Code settings.json

```json
{
  "mcpServers": {
    "company-skills": {
      "command": "python",
      "args": ["E:/2026/ClaudesCorner/projects/company-skills-mcp/server.py"],
      "env": {
        "AZURE_SEARCH_ENDPOINT": "${AZURE_SEARCH_ENDPOINT}",
        "AZURE_SEARCH_KEY": "${AZURE_SEARCH_KEY}",
        "AZURE_OPENAI_ENDPOINT": "${AZURE_OPENAI_ENDPOINT}",
        "AZURE_OPENAI_KEY": "${AZURE_OPENAI_KEY}",
        "SKILL_AUTHOR": "jason.nicolini@numberskills.se"
      }
    }
  }
}
```

---

## 8. The Bootstrap Skill: query-company-skills

This is the single skill that ships with every Claude Code installation at Numberskills. It teaches the agent how to discover and load remote skills on demand.

### File location

```
~/.claude/skills/query-company-skills/SKILL.md
```

Or distributed via the ENGRAM bootstrap kit.

### SKILL.md

````markdown
---
name: query-company-skills
description: Discover and load company-wide skills from the shared Azure AI Search index
tags: [meta, skills, company]
namespace: general
---

# Query Company Skills

Use this skill to find and load skills from the Numberskills shared skill index.

## When to use

- You need to perform a task and don't know if a skill exists for it
- You want to see what skills are available in a particular domain
- A user asks about available capabilities

## Steps

### 1. Search for a skill

Call `skill_search` with a natural language description of what you need:

```
mcp__company-skills__skill_search(
  query="how to query a Fabric lakehouse with DAX",
  top_k=3
)
```

Returns: list of `{name, title, description, score}` sorted by relevance.

### 2. Evaluate results

If `score > 0.82`: high confidence match — fetch and use it.
If `score 0.65–0.82`: moderate match — check description, decide.
If `score < 0.65`: no good match — proceed without a skill or write a new one.

### 3. Fetch the skill body

```
mcp__company-skills__skill_get(name="query-lakehouse-dax")
```

Returns the full skill markdown. Read it, then follow its instructions.

### 4. Contribute a new skill

If you write something reusable, push it back:

```
mcp__company-skills__skill_push(
  name="my-new-skill",
  body="---\n...\n---\n\n# Full skill content here",
  description="One-line description for semantic search",
  tags=["relevant", "tags"],
  namespace="fabric"
)
```

Status will be `draft` until a human approves it.

## Namespaces

| Namespace | Coverage |
|-----------|----------|
| `fabric` | Fabric lakehouses, pipelines, notebooks, eventstream |
| `dax` | DAX queries, measures, calculated columns |
| `python` | Python scripting, data processing, automation |
| `infra` | Claude Code infrastructure, MCP servers, dispatch |
| `general` | Cross-cutting, meta, onboarding |

## Score thresholds

| Score | Meaning |
|-------|---------|
| > 0.90 | Exact match |
| 0.82–0.90 | Strong match |
| 0.65–0.82 | Partial match — review description |
| < 0.65 | No confident match |
````

---

## 9. Migration Pipeline

### scripts/skill_sync.py

This script reads all local skill markdown files and upserts them to Azure AI Search. Run it manually or via CI on push to main.

```python
"""
skill_sync.py — Migrate local Claude Code skills to Azure AI Search

Usage:
  python scripts/skill_sync.py --dry-run        # Preview what would be upserted
  python scripts/skill_sync.py                  # Run the migration
  python scripts/skill_sync.py --skill name     # Sync a single skill by name
  python scripts/skill_sync.py --namespace dax  # Sync all skills with a given namespace tag
"""

import os
import re
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone

import httpx
from openai import AzureOpenAI

SKILLS_DIRS = [
    Path.home() / ".claude" / "skills",
    Path("skills"),  # repo-local skills
]

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]
SEARCH_INDEX = "skills-v1"
API_VERSION = "2024-05-01-preview"

openai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from skill markdown."""
    import yaml
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    try:
        meta = yaml.safe_load(match.group(1))
    except Exception:
        meta = {}
    return meta or {}, match.group(2).strip()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts."""
    response = openai_client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]


def collect_skills(skill_filter: str = None, ns_filter: str = None) -> list[dict]:
    """Walk skill directories and collect skill documents."""
    skills = []
    for base_dir in SKILLS_DIRS:
        for skill_file in base_dir.rglob("SKILL.md"):
            content = skill_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)
            name = meta.get("name") or skill_file.parent.name
            if skill_filter and name != skill_filter:
                continue
            tags = meta.get("tags", [])
            namespace = meta.get("namespace", "general")
            if ns_filter and namespace != ns_filter:
                continue
            description = meta.get("description", name)
            skills.append({
                "name": name,
                "title": name.replace("-", " ").title(),
                "description": description,
                "body": content,
                "tags": tags if isinstance(tags, list) else [tags],
                "namespace": namespace,
                "source_path": str(skill_file.relative_to(Path.home())),
                "full_content_hash": hashlib.sha256(content.encode()).hexdigest()[:16],
                "description_hash": hashlib.sha256(description.encode()).hexdigest()[:8],
            })
    return skills


def upsert_batch(docs: list[dict], dry_run: bool = False) -> int:
    """Upsert a batch of skill documents to Azure AI Search."""
    if dry_run:
        for d in docs:
            print(f"  [dry-run] Would upsert: {d['name']}")
        return len(docs)

    payload = []
    for d in docs:
        payload.append({
            "@search.action": "mergeOrUpload",
            "id": d["full_content_hash"],
            "name": d["name"],
            "title": d["title"],
            "description": d["description"],
            "body": d["body"],
            "tags": d["tags"],
            "namespace": d["namespace"],
            "author": os.environ.get("SKILL_AUTHOR", "sync-script"),
            "status": "approved",
            "source_path": d["source_path"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "version": 1,
            "embedding": d["embedding"]
        })

    r = httpx.post(
        f"{SEARCH_ENDPOINT}/indexes/{SEARCH_INDEX}/docs/index?api-version={API_VERSION}",
        headers={"Content-Type": "application/json", "api-key": SEARCH_KEY},
        json={"value": payload},
        timeout=30
    )
    r.raise_for_status()
    return len([x for x in r.json()["value"] if x["status"]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skill", type=str, default=None)
    parser.add_argument("--namespace", type=str, default=None)
    args = parser.parse_args()

    skills = collect_skills(skill_filter=args.skill, ns_filter=args.namespace)
    print(f"Found {len(skills)} skills to sync.")

    if not args.dry_run:
        # Batch embed descriptions
        descriptions = [s["description"] for s in skills]
        BATCH = 16
        embeddings = []
        for i in range(0, len(descriptions), BATCH):
            embeddings.extend(embed_batch(descriptions[i:i+BATCH]))
            print(f"  Embedded {min(i+BATCH, len(descriptions))}/{len(descriptions)}")
        for skill, emb in zip(skills, embeddings):
            skill["embedding"] = emb

    # Upsert in batches of 100 (Azure AI Search limit per request)
    total = 0
    UPLOAD_BATCH = 100
    for i in range(0, len(skills), UPLOAD_BATCH):
        batch = skills[i:i+UPLOAD_BATCH]
        total += upsert_batch(batch, dry_run=args.dry_run)
        print(f"  Upserted {min(i+UPLOAD_BATCH, len(skills))}/{len(skills)}")

    print(f"\nDone. {total} skills synced to Azure AI Search index '{SEARCH_INDEX}'.")


if __name__ == "__main__":
    main()
```

---

## 10. Sync & Governance

### The governance problem

Skills pushed directly to the index with `skill_push` arrive with `status: draft`. They are invisible to `skill_search` (which filters `status eq 'approved'`) until a human or automated reviewer promotes them.

### Approval flow

```
Developer writes skill locally
    ↓
skill_push → status: draft (visible only to author with status filter)
    ↓
Weekly review: human scans drafts via skill_list(status="draft")
    ↓
Approve: PATCH status → "approved"   OR   Reject: skill_deprecate with reason
    ↓
status: approved → appears in all skill_search results
```

### CI sync (GitHub Actions)

Skills committed to the `claudescorner` repo under `skills/` are auto-synced to the index on push to `main`. These arrive as `approved` because the commit itself is the review gate.

```yaml
# .github/workflows/skill_sync.yml
name: Sync skills to Azure AI Search

on:
  push:
    branches: [main]
    paths: ["skills/**"]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install httpx openai python-dotenv pyyaml
      - run: python scripts/skill_sync.py
        env:
          AZURE_SEARCH_ENDPOINT: ${{ secrets.AZURE_SEARCH_ENDPOINT }}
          AZURE_SEARCH_KEY: ${{ secrets.AZURE_SEARCH_KEY }}
          AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          AZURE_OPENAI_KEY: ${{ secrets.AZURE_OPENAI_KEY }}
          SKILL_AUTHOR: ci-sync@numberskills.se
```

### Stale skill detection

Any skill not updated in 90 days is flagged as potentially stale. The `memory-mcp` `get_stale_docs` pattern applies here too — add a scheduled Azure Function or dispatch task:

```python
# scripts/flag_stale_skills.py
# Run weekly via dispatch.py --push
# Flags skills where updated_at < (now - 90 days) and status == "approved"
```

---

## 11. Auth & Access Control

### Minimal setup (single team)

Use the Azure AI Search admin key stored as an environment variable. All team members share the same key. Simple, good enough for a small team.

```
AZURE_SEARCH_KEY=<admin-key>
```

### Production setup (multi-team)

Use role-based access with Entra ID (AAD):

| Role | Azure Search Permission | Who |
|------|------------------------|-----|
| `Search Index Data Reader` | `skill_search`, `skill_get`, `skill_list` | All developers, agents |
| `Search Index Data Contributor` | + `skill_push`, `skill_deprecate` | Senior devs, CI/CD |
| `Search Service Contributor` | Index admin | Infra team only |

Assign via Azure Portal → AI Search resource → Access Control (IAM) → Add role assignment.

Then authenticate with Managed Identity instead of API key:

```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

credential = DefaultAzureCredential()
client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=credential
)
```

`DefaultAzureCredential` picks up Managed Identity in Azure, developer credentials locally via `az login`.

---

## 12. Teams Digest Integration

Weekly digest of new skills pushed to a Teams channel using the existing `fab_graph_teams_message` MCP tool.

### scripts/skill_digest.py

```python
"""
skill_digest.py — Post weekly new skills digest to Teams.
Run via dispatch.py on Mondays.
"""
import os
import httpx
from datetime import datetime, timedelta, timezone

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]
TEAMS_WEBHOOK = os.environ["TEAMS_SKILL_WEBHOOK"]

def get_new_skills(days: int = 7) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    body = {
        "top": 20,
        "select": "name,title,description,tags,author",
        "filter": f"status eq 'approved' and created_at ge {since}",
        "orderby": "created_at desc"
    }
    r = httpx.post(
        f"{SEARCH_ENDPOINT}/indexes/skills-v1/docs/search?api-version=2024-05-01-preview",
        headers={"Content-Type": "application/json", "api-key": SEARCH_KEY},
        json=body
    )
    r.raise_for_status()
    return r.json().get("value", [])

def post_digest(skills: list[dict]):
    if not skills:
        return
    lines = [f"**New Claude Code Skills This Week ({len(skills)} added)**\n"]
    for s in skills:
        tags = ", ".join(s.get("tags", []))
        lines.append(f"• **{s['title']}** — {s['description']} `[{tags}]`")
    message = "\n".join(lines)
    r = httpx.post(TEAMS_WEBHOOK, json={"text": message})
    r.raise_for_status()

if __name__ == "__main__":
    skills = get_new_skills(days=7)
    post_digest(skills)
    print(f"Posted digest: {len(skills)} new skills.")
```

Add to dispatch schedule:

```bash
python scripts/dispatch.py --push "python scripts/skill_digest.py" --category infrastructure
```

Or via cron in `scripts/dispatch.py` on Monday mornings.

---

## 13. Deployment Checklist

```
Infrastructure
  [ ] Azure resource group created (rg-numberskills-ai)
  [ ] Azure AI Search provisioned (Basic tier, swedencentral)
  [ ] Azure OpenAI provisioned (text-embedding-3-small deployed)
  [ ] skills-v1 index created via search_index_schema.json
  [ ] Admin key stored as AZURE_SEARCH_KEY in team password manager

Local setup (per developer)
  [ ] .env updated with AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY,
        AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, SKILL_AUTHOR
  [ ] company-skills-mcp wired in settings.json
  [ ] pip install -r projects/company-skills-mcp/requirements.txt
  [ ] query-company-skills skill installed at ~/.claude/skills/

Migration
  [ ] python scripts/skill_sync.py --dry-run (preview)
  [ ] python scripts/skill_sync.py (run)
  [ ] Verify: mcp__company-skills__skill_search(query="test") returns results

CI/CD
  [ ] AZURE_SEARCH_ENDPOINT added as GitHub Actions secret
  [ ] AZURE_SEARCH_KEY added as GitHub Actions secret
  [ ] AZURE_OPENAI_ENDPOINT added as GitHub Actions secret
  [ ] AZURE_OPENAI_KEY added as GitHub Actions secret
  [ ] skill_sync.yml workflow enabled

Governance
  [ ] Draft review process documented in CONTRIBUTING.md
  [ ] First batch of skills reviewed and approved
  [ ] Teams webhook URL set as TEAMS_SKILL_WEBHOOK
  [ ] skill_digest.py added to dispatch schedule (Mondays)
```

---

## 14. Cost Model

### Azure AI Search Basic tier

| Resource | Cost |
|----------|------|
| Basic tier (1 partition, 1 replica) | ~$25/month |
| Storage included | 2 GB |
| Max documents | Unlimited within 2GB |

At ~6KB per skill document (including 1536-dim float32 vector = 6144 bytes):
- 500 skills ≈ 3MB → well within 2GB
- 5,000 skills ≈ 30MB → still within 2GB
- Free tier (50MB) handles ~8,000 skills in raw terms but has stricter API limits

**Recommendation: Start Free, upgrade to Basic when you hit 3 indexes or need SLA.**

### Azure OpenAI text-embedding-3-small

| Operation | Cost |
|-----------|------|
| Per 1M tokens | $0.02 |
| Average description length | ~15 tokens |
| 500 skills initial migration | 7,500 tokens ≈ $0.00015 |
| 10 searches/day × 15 tokens/query × 365 days | 54,750 tokens ≈ $0.001/year |

**Embedding cost is effectively zero at this scale.**

### Total monthly cost

| Item | Cost |
|------|------|
| Azure AI Search Basic | $25.00 |
| Azure OpenAI embeddings | ~$0.01 |
| **Total** | **~$25/month** |

---

## 15. Future Roadmap

### Near-term (next sprint)

- **Skill versioning UI** — view diff between v1 and v2 of a skill
- **Auto-deprecation** — skill flagged stale after 90 days with no usage
- **Usage tracking** — log `skill_get` calls to understand which skills are actually used

### Medium-term

- **ENGRAM integration** — `query-company-skills` ships as a default skill in the ENGRAM bootstrap kit, making this available to any team that adopts ENGRAM
- **Skill quality scoring** — track how often a fetched skill leads to successful task completion (via PostToolUse hook) and surface quality scores in search results
- **Cross-org federation** — multiple Azure AI Search indexes per org, federated search across them. Numberskills skills + client-specific skills queryable from one interface.

### Long-term

- **Skill marketplace** — public index for generic Claude Code skills, private index for company-specific ones. Same query interface, different auth scopes.
- **Automatic skill extraction** — PostToolUse hook detects successful multi-step patterns and proposes them as new skills. Human approves. Virtuous cycle.
- **Skill conflict detection** — when two skills cover the same ground, surface them to a reviewer for consolidation.

---

*Last updated: 2026-04-17 | Author: jason.nicolini@numberskills.se | Status: Architecture complete, implementation pending*
