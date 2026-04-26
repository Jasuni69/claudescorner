---
title: "awesome-codex-skills — ComposioHQ SKILL.md library with mcp-builder"
date: 2026-04-25
source: https://github.com/ComposioHQ/awesome-codex-skills
tags: [skills, mcp, codex, composio, claude-code, skill-manager-mcp]
stars: 1237
today_gain: +174
license: unknown
relevance: skill-manager-mcp, dispatch.py, ENGRAM
---

# awesome-codex-skills — ComposioHQ

**GitHub:** https://github.com/ComposioHQ/awesome-codex-skills
**Stars:** 1.2k (+174 today) | **Language:** Python | **Trending:** 2026-04-25 daily

## What It Is

50+ SKILL.md modular instruction bundles for Codex CLI/API, organized into 5 categories. Each skill follows the standard `skill-name/SKILL.md` directory structure with YAML frontmatter + step-by-step instructions — the same format used by Anthropic, OpenAI, HuggingFace, VoltAgent, and marketingskills.

**ComposioHQ = the 6th major org independently adopting SKILL.md as de facto standard without coordination.**

## MCP-Specific Skills

- **`mcp-builder/`** — "Build and evaluate MCP servers with best practices and an evaluation harness." First known skill for *constructing and testing MCP servers*, not just consuming them. Harness pattern directly applicable to skill-manager-mcp + memory-mcp pre-release validation.
- **`helium-mcp/`** — Real-time news with bias scoring, live market data, ML options pricing via MCP. Fairford alternative-data signal layer candidate.

## Skill Categories (50+ total)

| Category | Count | Notable Skills |
|---|---|---|
| Development & Code Tools | ~11 | codebase migration, GitHub PR review, CI/CD fixes, linting, **mcp-builder** |
| Productivity & Collaboration | ~14 | Linear/Jira triage, Notion integration, Slack automation |
| Communication & Writing | ~5 | changelog generation, email drafting |
| Data & Analysis | ~8 | spreadsheet formulas, competitive analysis, Datadog logs |
| Meta & Utilities | ~8 | design tokens, image enhancement |

## Composio Integration

Skills connect Codex to **1000+ third-party apps** via `composio connect` + `composio connect-apps`. Covers Slack, GitHub, Notion, Linear, Stripe — same integrations fabric-mcp lacks for Fairford. Composio CLI fills the action-execution gap that dispatch.py workers hit when they need to *write* to external systems.

## Install Pattern

```bash
# Automated installer places skills into $CODEX_HOME/skills (~/.codex/skills)
# Codex auto-discovers and triggers based on matching descriptions
```

## Relevance to ClaudesCorner

1. **mcp-builder skill** — eval harness pattern for MCP server quality gate; apply to skill-manager-mcp + memory-mcp before ENGRAM public release
2. **6th SKILL.md org confirmation** — ENGRAM portability story is now provably cross-platform (Anthropic/OpenAI/HF/VoltAgent/marketingskills/Composio)
3. **helium-mcp** — real-time market data via MCP; evaluate as Fairford alternative-data complement to Kronos
4. **Composio 1000+ app integrations** — action-execution primitive for dispatch.py workers needing external writes; evaluate before building custom connectors
