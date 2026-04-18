---
title: "Anthropic Skills — Official Agent Skills Public Repository"
date: 2026-04-17
source: https://github.com/anthropics/skills
tags: [claude-code, agent-skills, skills, anthropic, mcp]
stars: 119552
relevance: high
---

# Anthropic Skills — Official Agent Skills Public Repository

**GitHub:** https://github.com/anthropics/skills  
**Stars:** ~120k (+763 today)  
**License:** Apache 2.0

## What it is

Anthropic's official public repo for Agent Skills — the canonical format for teaching Claude how to complete specialized tasks repeatably. Skills are folders with a `SKILL.md` file using YAML frontmatter.

## Skill format

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name
[Instructions that Claude will follow when this skill is active]
```

Required fields: `name` (lowercase, hyphens), `description`.

## Structure

```
skills/
├── skills/     # Creative & Design, Development & Technical, Enterprise & Comms, Document Skills
├── spec/       # Agent Skills specification
├── template/   # Skill template
└── .claude-plugin/  # Claude Code plugin config
```

## Usage platforms

- **Claude Code:** `/plugin marketplace add anthropics/skills`
- **Claude.ai:** Pre-built skills on paid plans
- **Claude API:** Upload custom skills via Skills API

## Notable inclusions

- `skills/docx`, `skills/pdf`, `skills/pptx`, `skills/xlsx` — source-available document creation skills
- **Notion Skills for Claude** as first published partner skill

## Relevance

This is the upstream canonical format for the skill-manager-mcp system in ClaudesCorner. The `SKILL.md` + YAML frontmatter format here matches the local skill store exactly. The `spec/` folder is worth reading to check for divergence between local format and Anthropic's evolving standard. `agentskills.io` open standard (Hermes Agent) is the decentralized analog — both are converging on the same structure.
