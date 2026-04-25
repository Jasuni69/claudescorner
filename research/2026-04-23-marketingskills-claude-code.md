---
title: "marketingskills — 40+ SKILL.md Marketing Skills for Claude Code"
date: 2026-04-23
source: https://github.com/coreyhaines31/marketingskills
stars: 23600
stars_today: +491
license: MIT
tags: [claude-code, skills, skill-manager-mcp, agentskills, ENGRAM, marketing]
---

# marketingskills — Production SKILL.md Marketing Skill Library

**Repo:** coreyhaines31/marketingskills · 23.6k stars · +491 today · MIT · JS + Shell

## What It Is

A marketplace-installable collection of 40+ AI agent skills for marketing, growth, and sales tasks. Structured in SKILL.md format, installable via `npx skills`, Claude Code plugin (`.claude-plugin`), git submodule, or SkillKit for multi-agent deployment.

All skills reference a foundational `product-marketing-context` skill that must be loaded first — it stores product positioning, target audience, and brand voice as shared context before any domain skill executes. This is the same foundational-context-first pattern used in dispatch.py tier 2/3 worker prompts.

## Skill Categories (40+ total)

| Category | Skills |
|---|---|
| Conversion Optimization | page, signup, onboarding, forms, popups |
| Content & Copy | copywriting, cold email, social content |
| SEO & Discovery | audits, AI search, programmatic SEO, schema markup |
| Paid Advertising | Google, Meta, LinkedIn campaigns |
| Measurement | analytics tracking, A/B testing |
| Growth Engineering | free tools, referral programs |
| Sales & RevOps | enablement, lead management |
| Strategy | pricing, launches, psychology-based marketing |

## Install Patterns

```bash
# CLI
npx skills

# Claude Code plugin
# Add to .mcp.json / settings.json

# Multi-agent
SkillKit deploy marketingskills
```

## Signals for ClaudesCorner

1. **skill-manager-mcp import candidate** — 40+ MIT-licensed skills in SKILL.md format ready to be ingested into the local skill store via `skill_create`. Microsoft Azure skills (from awesome-agent-skills) + marketingskills = two direct import batches.

2. **Foundational-context-first pattern** — `product-marketing-context` as prerequisite skill mirrors dispatch.py task_plan.md injection pattern: shared context loaded once, reused by all downstream workers. Worth applying to ENGRAM skill bundles.

3. **3rd production validation of agentskills.io format** — after anthropics/skills and huggingface/skills, a domain-specific 40+ skill library at 23.6k stars confirms SKILL.md is the de facto standard across the ecosystem. skill-manager-mcp's FTS5+vector differentiator is now load-bearing as the skill count grows.

4. **`.claude-plugin` config** — ships a ready-to-wire plugin config; pattern reusable for ENGRAM's plugin bundle (Skills+MCP bundled per Anthropic MCP Production Guide clipped earlier today).

## Gap Identified

No MCP server bundled — skills are prompt-only. Adding an MCP tool layer (e.g., `fetch_marketing_context`, `run_seo_audit`) would close the gap between skill invocation and live data. Backlog: `marketingskills-mcp` wrapper.
