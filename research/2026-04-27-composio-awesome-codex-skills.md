---
title: "awesome-codex-skills — Composio Curated Codex Skill Library"
source: https://github.com/ComposioHQ/awesome-codex-skills
date: 2026-04-27
stars: 2100
stars_today: 517
license: unlicensed
tags: [skills, codex, composio, agent-skills, mcp, engram]
---

# awesome-codex-skills — Composio Curated Codex Skill Library

**Repo:** github.com/ComposioHQ/awesome-codex-skills  
**Stars:** 2,100 | **Today:** +517 | **Language:** Python  
**GitHub Trending:** #5 Python daily, 2026-04-27

## What It Is

Composio's curated collection of modular instruction bundles (SKILL.md format) for OpenAI Codex. Each skill is a self-contained folder with a `SKILL.md` frontmatter file and execution instructions. Install via Python script into `$CODEX_HOME/skills`.

## Skill Categories

Five categories, ~46 skills total:

- **Development & Code Tools** (~11): codebase migration, CI/CD fixes, PR reviews, **MCP server building** skill
- **Productivity & Collaboration** (~14): Linear/Jira triage, Notion integration, meeting notes
- **Communication & Writing** (~5): email drafting, changelog generation, resume tailoring
- **Data & Analysis** (~8): spreadsheet formulas, lead research, competitive analysis, Datadog log filtering
- **Meta & Utilities** (~8): design tools, skill installation helpers

## Key Signal: The "connect" Skill

The standout is a **"connect" skill** that wires 1000+ apps via the Composio CLI (Slack, GitHub, Notion, Jira, etc.). This is a cross-app integration primitive that no SKILL.md library has shipped before — it turns any Codex agent into a workflow automation hub for external services. skill-manager-mcp lacks this integration layer.

## Architecture Notes

- SKILL.md frontmatter format (name, description) = same de facto standard as Anthropic/OpenAI/HuggingFace/VoltAgent — 5th major org confirming convergence
- Progressive disclosure: references stay separate from core guidance (matches ENGRAM pattern)
- Python installer → `$CODEX_HOME/skills` (not MCP-native, no semantic search, no write-gate)
- No `agent_activation_allowed` governance flag = skill-manager-mcp is complementary runtime layer

## Relevance to Jason's Work

| Signal | Impact |
|--------|--------|
| 5th org confirming SKILL.md de facto standard | ENGRAM portability story confirmed across Claude Code, Codex, Cursor, OpenClaw |
| "connect" skill wiring 1000+ apps via Composio CLI | Gap in skill-manager-mcp: no cross-app action primitive; Composio SDK = potential integration target |
| MCP server building skill included | Validates meta-skill pattern (skill that creates other skills/MCPs) |
| No semantic search or agent_activation_allowed | skill-manager-mcp remains complementary, not competitive |

## Action Items

- **Backlog:** Import Composio "connect" skill wrapper concept into skill-manager-mcp as an integration bridge
- **ENGRAM:** Reference awesome-codex-skills as 5th ecosystem proof point alongside awesome-agent-skills, marketingskills, HuggingFace skills, OpenAI skills
- **Skill to evaluate:** The "build-mcp-server" skill — check if it follows patterns worth adopting in skill-manager-mcp's `skill_create` tool
