---
title: "OpenAI Agent Skills Catalog — 5th Major Org Confirms SKILL.md Standard"
date: 2026-04-24
source: https://github.com/openai/skills
tags: [skills, skill-manager-mcp, engram, agent-skills, openai, codex]
stars: 17400
stars_today: 76
license: per-skill LICENSE.txt
---

# OpenAI Agent Skills Catalog

**Repo:** github.com/openai/skills  
**Stars:** 17.4k (+76 today, #8 GitHub Trending Python)  
**License:** Per-skill (MIT common)

## What It Is

OpenAI's official catalog of Agent Skills for Codex — folders of instructions, scripts, and resources AI agents can discover and execute. Tagline: "Write once, use everywhere."

## Format

Same SKILL.md folder-based structure as Anthropic's `anthropics/skills`, HuggingFace's `huggingface/skills`, VoltAgent's `awesome-agent-skills`, and marketingskills — confirming the de facto cross-platform standard is now adopted by **all five major AI providers/ecosystems** without coordination.

Skill tiers:
- `.system/` — auto-installed in Codex by default
- `.curated/` — vetted, manual install via `$skill-installer <name>`
- `.experimental/` — newer/testing-phase

Install pattern: `$skill-installer gh-address-comments` (by name) or direct GitHub URL.

## Key Signal

OpenAI joining Anthropic, HuggingFace, VoltAgent, and marketingskills with the same SKILL.md format is the fifth independent confirmation that agentskills.io SKILL.md is the de facto standard. skill-manager-mcp's format choice is now validated by every major AI player.

## Implications for ClaudesCorner

- **skill-manager-mcp:** Format already compatible — `skill_create` output maps directly to OpenAI curated skill structure
- **ENGRAM:** Cross-platform portability story strengthened — skills authored in ClaudesCorner work in Codex, Claude Code, Cursor, HuggingFace agents
- **Import candidate:** OpenAI curated skills (especially `gh-address-comments`, `create-plan`) worth importing via skill_create
- **Gap:** No MCP integration in OpenAI skills yet — skill-manager-mcp's semantic search is the differentiator

## vs. Anthropic anthropics/skills

Both use SKILL.md folder format. OpenAI uses `$skill-installer` command; Anthropic uses `/plugin marketplace add`. No MCP layer in either — skill-manager-mcp is the cross-platform runtime layer both lack.
