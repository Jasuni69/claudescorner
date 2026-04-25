---
title: "Android Reverse Engineering Skill for Claude Code"
date: 2026-04-21
source: https://github.com/SimoneAvogadro/android-reverse-engineering-skill
stars: 1921
tags: [claude-code, skills, android, reverse-engineering, security, agentskills]
relevance: high
---

# Android Reverse Engineering Skill for Claude Code

**Repo**: SimoneAvogadro/android-reverse-engineering-skill (+1,921 stars this week)
**Install**: `/plugin marketplace add SimoneAvogadro/android-reverse-engineering-skill`

## What It Does

Marketplace-installable Claude Code skill that decompiles APK, XAPK, JAR, and AAR files and extracts HTTP endpoints, authentication patterns, and call flows — without source code access.

## Key Capabilities

- `/decompile` slash command for automated workflows
- Natural language triggers: "Extract API endpoints from this app"
- Multi-engine decompilation: jadx, Fernflower, Vineflower (comparison mode)
- Automated HTTP API extraction from obfuscated bytecode
- Speaker diarization and authentication pattern detection

## Why It Matters

This is a production example of the agentskills.io pattern in the wild — a self-contained skill folder with instructions and tooling, installed via the marketplace in one command. It validates:

1. **skill-manager-mcp**: Real users are publishing and consuming skills via the marketplace format. The semantic search gap (FTS5 + vector vs file-only) remains skill-manager-mcp's differentiator.
2. **Security-adjacent agent use**: Authorized reverse engineering (pen testing, API compatibility, legacy integration) is a real dispatch.py worker use case — a `/decompile` skill wrapping jadx is a pattern worth adding.
3. **Skill granularity signal**: Security skills are domain-specific enough that they work as standalone installable units rather than baked-in Claude Code behavior — confirms the skill-per-domain architecture.

## Action Items

- [ ] Add this as a reference in ENGRAM's skill ecosystem documentation
- [ ] Consider a `fabric-ingestion` skill in the same format for markitdown-mcp pipeline
- [ ] Verify whether agentskills.io now indexes community-published marketplace skills
