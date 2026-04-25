---
title: "HuggingFace Skills — Official SKILL.md Agent Skills for Claude Code"
source: https://github.com/huggingface/skills
date: 2026-04-22
tags: [agent-skills, skill-manager-mcp, claude-code, mcp, engram, huggingface]
relevance: high
---

# HuggingFace Skills — Official SKILL.md Format for Claude Code

**Repo**: huggingface/skills · 10,262 stars · +15 today · GitHub Trending Python #5

## What It Is

HuggingFace's official Claude Code skill plugin — 11 specialized skills that give coding agents access to the full HuggingFace ecosystem (datasets, model training, Gradio UI, paper publishing, JS/TS inference).

This is the **second major organization** (after Anthropic's `anthropics/skills`) to ship a production agent skill plugin using the agentskills.io SKILL.md format.

## Skill Format

Each skill is a self-contained folder:
```
skills/
  hf-cli/
    SKILL.md        # YAML frontmatter + instructions
    scripts/        # helper scripts
    templates/      # file templates
```

SKILL.md frontmatter:
```yaml
name: hf-cli
description: What the skill does and when to use it
```

## Discovery & Installation

| Platform | Mechanism |
|---|---|
| Claude Code | `/plugin marketplace add huggingface/skills` then `/plugin install <skill>@huggingface/skills` |
| Codex | `.agents/skills/` directory auto-discovery |
| Gemini CLI | `gemini-extension.json` manifest |
| Cursor | `.cursor-plugin/plugin.json` + `.mcp.json` |

Claude Code auto-loads the SKILL.md instructions + helper scripts when a matching request triggers the skill.

## MCP Integration

`.mcp.json` wires directly to the HuggingFace MCP server URL — skill activation can delegate to MCP tools. This is the **skill → MCP** composition pattern: skill handles intent routing, MCP handles API execution.

## Governance Pattern: marketplace.json

`.claude-plugin/marketplace.json` separates:
- **Human-readable descriptions** (for browsing)
- **Technical SKILL.md content** (for agent activation logic)

This two-layer manifest is a governance primitive — humans browse one view, agents consume another. skill-manager-mcp currently conflates these; this separation is worth adopting.

## Available Skills (11)

- `hf-cli` — HuggingFace CLI operations
- `huggingface-datasets` — dataset exploration
- `huggingface-llm-trainer` — LLM fine-tuning
- `huggingface-vision-trainer` — vision model training
- `huggingface-gradio` — Gradio UI creation
- `huggingface-paper-publisher` — arXiv paper publication
- `transformers-js` — JS/TS inference with Transformers.js
- + 4 evaluation/experiment tracking skills

## Relevance to ClaudesCorner

| ClaudesCorner component | Implication |
|---|---|
| skill-manager-mcp | HF validates SKILL.md YAML frontmatter as the canonical cross-platform format; adopt `marketplace.json` two-layer separation |
| ENGRAM | Two major orgs (Anthropic + HuggingFace) now shipping skills in this format — ENGRAM should reference this as the standard, not just agentskills.io |
| dispatch.py | Worker skills could be discoverable via `/plugin marketplace` — current `tasks.json` approach is pre-standard |
| fabric-mcp | Pattern: fabric-mcp as a skill plugin with `.mcp.json` wiring — exposes Fabric as both MCP tool AND installable skill |

**Key insight**: HuggingFace shipping official Claude Code skills confirms the skill-as-distribution-unit pattern is solidifying. The `marketplace.json` two-layer governance (human-browse vs agent-activate) is a concrete spec gap in skill-manager-mcp v2.2.0.

## Action Items

- Add `marketplace.json` support to skill-manager-mcp — separate human description from agent activation SKILL.md
- Benchmark skill-manager-mcp FTS5+vector search against marketplace browsing UX
- Consider wrapping fabric-mcp as an installable skill plugin alongside its MCP server role
