---
title: "mattpocock/skills — Personal SKILL.md Library Goes Viral (20k Stars)"
date: 2026-04-26
source: https://github.com/mattpocock/skills
tags: [skills, claude-code, agentskills, engram, skill-manager-mcp, dotfiles]
signal: high
---

## Summary

Matt Pocock — author of Total TypeScript, 200k+ developer audience — published his personal Claude Code skill library as a public GitHub repo. It hit 20k stars and ranked #2 on GitHub Trending daily (all languages, +1,139 today). This is the "dotfiles moment" for agent skills: a prominent practitioner publishing their `.claude/` directory as a shareable artefact.

**Repo:** https://github.com/mattpocock/skills  
**Stars:** 20,419 | **Daily gain:** +1,139 | **License:** MIT | **Language:** Shell

---

## What It Contains

20 skills across 5 categories, all installable via `npx skills@latest add mattpocock/<skill-name>`:

**Planning & Design**
- `to-prd` — converts requirements to PRD
- `to-issues` — breaks PRD into GitHub issues
- `grill-me` — interview-driven requirements extraction
- `design-an-interface` — interface design from spec
- `request-refactor-plan` — structured refactor planning

**Development**
- `tdd` — test-driven development workflow
- `triage-issue` — issue classification + priority
- `improve-codebase-architecture` — architecture review
- `migrate-to-shoehorn` — migration skill (Shoehorn ORM)
- `scaffold-exercises` — exercise scaffolding

**Tooling & Setup**
- `setup-pre-commit` — pre-commit hook configuration
- `git-guardrails-claude-code` — guardrails for Claude Code git ops

**Writing & Knowledge**
- `write-a-skill` — skill authoring workflow
- `edit-article` — article editing
- `ubiquitous-language` — DDD ubiquitous language capture
- `obsidian-vault` — Obsidian vault integration skill

**Other**
- `caveman` — caveman mode (terse output, as in Jason's CLAUDE.md)
- `domain-model` — domain model documentation
- `github-triage` — GitHub issue/PR triage
- `zoom-out` — step back and reconsider approach

---

## Key Signals

### 1. Dotfiles Movement Has Arrived for Agent Skills
Pocock's personal `.claude/` directory becoming a public 20k-star repo confirms that practitioners are treating agent skill libraries as first-class shareable artefacts — the same cultural shift that made dotfiles repositories mainstream ~2012. The install pattern (`npx skills@latest add owner/repo`) is frictionless but has **no discovery layer**: you must know the repo exists. This is the gap skill-manager-mcp fills with semantic FTS5+vector search.

### 2. `write-a-skill` Skill — Skills Writing Themselves
The meta-skill `write-a-skill` (a skill for authoring new skills) is the same pattern as the ENGRAM `writing-skills` skill. Independent convergence by a prominent practitioner confirms this is the correct abstraction.

### 3. `obsidian-vault` and `caveman` Skills
Pocock uses both Obsidian and caveman-mode — direct ENGRAM/ClaudesCorner cultural alignment. The `obsidian-vault` skill is likely an analog to the mcp-obsidian integration in ClaudesCorner.

### 4. No MCP Layer
Like marketingskills, HuggingFace skills, and anthropics/skills, mattpocock/skills has no MCP server. The install mechanism is file-copy via `npx skills`. skill-manager-mcp remains the only runtime that provides:
- Semantic search across multiple skill libraries
- `agent_activation_allowed` governance gate
- Cross-session skill promotion from task outcomes

### 5. `git-guardrails-claude-code` — Safety Hooks Pattern
A dedicated skill for constraining Claude Code's git operations mirrors the ClaudesCorner DENY clause pattern and dispatch.py worker scope bounding. Worth reading the implementation for patterns applicable to dispatch.py worker git safety.

---

## Relevance to Jason's Work

| Project | Relevance |
|---------|-----------|
| skill-manager-mcp | Pocock's library is an import candidate; confirms semantic discovery gap |
| ENGRAM | `write-a-skill` + `obsidian-vault` are independent validation of ENGRAM core skills |
| dispatch.py | `git-guardrails-claude-code` skill worth reviewing for worker scope patterns |
| HEARTBEAT.md | `zoom-out` skill pattern (step back, reconsider) could be a periodic dispatch gate |

---

## Action Items

- Import mattpocock/skills into skill-manager-mcp index (add to skill discovery corpus)
- Read `git-guardrails-claude-code` implementation — patterns for dispatch.py worker git safety
- Note: `caveman` skill confirms caveman-mode is a recognized practice, not idiosyncratic
