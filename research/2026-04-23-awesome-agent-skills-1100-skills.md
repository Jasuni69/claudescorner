---
title: "Awesome Agent Skills — 1100+ Curated Official Skills Across 12 Platforms"
source: https://github.com/VoltAgent/awesome-agent-skills
date: 2026-04-23
tags: [agent-skills, skill-manager-mcp, ENGRAM, SKILL.md, multi-platform, Claude-Code, agentskills]
signal: high
clipped_by: dispatch-agent
---

# Awesome Agent Skills — 1100+ Curated Official Skills Across 12 Platforms

**Source:** github.com/VoltAgent/awesome-agent-skills | **Stars:** 17.7k (+176 today) | **License:** MIT

## What It Is

A curated repository of 1,100+ agent skills from official dev teams and community contributors. Explicitly positioned as "real-world Agent Skills created and used by actual engineering teams" — contrasted against bulk AI-generated skill repos.

## Scope

Skills organized by organization/team:

| Org | Skills | Notes |
|---|---|---|
| Microsoft | 133 | Azure SDK coverage across 6 languages |
| Sentry | 40+ | Framework-specific instrumentation |
| OpenAI | 40+ | Codex/GPT tooling |
| Anthropic | — | Official agentskills.io format |
| Google | — | Gemini CLI integration |
| Vercel | — | Frontend/deployment |
| Stripe | — | Payments/API |
| Cloudflare | — | Edge/workers |
| Trail of Bits | — | Security-focused tooling |
| 50+ more orgs | — | Frontend/React, cloud platforms, databases, Terraform, advertising, marketing |

## Platform Support

Compatible with: Claude Code, Codex, Antigravity, Gemini CLI, Cursor, GitHub Copilot, OpenCode, Windsurf, and more (12 platforms total).

## Format

Skills use Markdown documentation linked via `officialskills.sh`. Organization-grouped rather than technically specified — doesn't enforce SKILL.md/YAML frontmatter but references agentskills.io as the upstream standard.

## Relevance to ClaudesCorner

- **skill-manager-mcp**: 1100+ skills across 50+ orgs is a direct expansion source for the local skill library. FTS5+vector search in skill-manager-mcp makes this collection semantically queryable vs file-based search
- **ENGRAM**: ENGRAM's skill layer claims portability — this repo is concrete evidence of the multi-platform skill ecosystem; cite in ENGRAM README as proof of convergence
- **Agent Skills Standardization** (clipped today): Complements the agensi.io finding — convergence happening at ecosystem level with 50+ major orgs; validates the `agent_activation_allowed` two-layer governance flag in skill-manager-mcp v2.4.0
- **Microsoft's 133 skills across 6 languages**: Direct import candidate for Fairford Azure/Fabric-related skill categories
- **Trail of Bits security skills**: Relevant to dispatch.py worker security review step

## Signal

Third major aggregate signal (after anthropics/skills 120k and huggingface/skills 10.3k) confirming SKILL.md as the de facto cross-platform agent skill format. MIT license = no deployment friction.

## Action Items

- Pull Trail of Bits security skills into skill-manager-mcp for dispatch.py worker security review
- Pull Microsoft Azure skills for Fairford Phase 2 Fabric/Azure coverage
- Add `officialskills.sh` as a reference source in skill-manager-mcp `skill_search` documentation
- Cite in ENGRAM README alongside anthropics/skills and HuggingFace/skills as ecosystem proof
