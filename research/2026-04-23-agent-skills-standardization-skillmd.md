---
title: "The Quiet Standardization of AI Agent Skills — SKILL.md as De Facto Cross-Platform Format"
date: 2026-04-23
source: https://www.agensi.io/learn/the-quiet-standardization-of-ai-agent-skills
tags: [agent-skills, skillmd, standardization, skill-manager-mcp, engram, agentskills-io]
signal: high
---

# The Quiet Standardization of AI Agent Skills

**Source**: agensi.io/learn/the-quiet-standardization-of-ai-agent-skills
**HN points**: 1 (very new — not yet surfaced on front page)

## What happened

SKILL.md has become a de facto cross-platform standard for AI agent skills without any committee process or formal coordination. Major platforms adopted it independently because "there's nothing to argue about" — the format is minimal enough to be obviously sufficient.

## Adopters (confirmed)

| Platform | Organization |
|---|---|
| Claude Code | Anthropic |
| Codex CLI | OpenAI |
| Gemini CLI | Google |
| GitHub Copilot | GitHub/Microsoft |
| Cursor | Anysphere |
| OpenClaw | Community |
| 20+ independent tools | Various |

## Format spec

```yaml
---
name: skill-name
description: one-line description
---

# Skill body (plain English instructions)
```

YAML frontmatter for metadata. Markdown body for instructions. No agent-specific APIs — plain English means skills transfer across platforms without modification.

## What's missing (ecosystem gaps)

1. **Discovery**: No standard way for agents to find available skills. `/.well-known/agent-skills.json` emerging but not universal.
2. **Versioning**: No semver or dependency pinning for skills.
3. **Dependency management**: Skills can't declare dependencies on other skills.
4. **Security verification**: Existing skill repos contain hidden prompt injection and data exfiltration patterns. Agensi marketplace runs security scanning as a differentiator.

## Agensi marketplace

Curated skill marketplace at agensi.io. Key differentiator: security scanning before listing. Positions as the npm registry analog for SKILL.md skills.

## Signals for ClaudesCorner

**skill-manager-mcp is architecturally correct**. The format Jason chose (SKILL.md + YAML frontmatter) is now confirmed as the industry standard. No format migration needed.

**The `agent_activation_allowed` flag** added in skill-manager-mcp v2.4.0 addresses the security gap identified here — separating human-browsable from agent-activatable skills matches the two-layer governance model.

**FTS5 + vector search** in skill-manager-mcp is differentiated vs competitors that rely on file-based discovery. The ecosystem gap around discovery is one skill-manager-mcp already solves.

**Security scanning gap**: skill-manager-mcp doesn't scan for prompt injection in skill bodies. Worth adding a simple heuristic check on `skill_create`/`skill_update` — flag skills containing `ignore previous instructions`, `disregard`, or raw URL patterns in the body.

**ENGRAM**: SKILL.md portability is now externally validated. An agent that learns ENGRAM can immediately use its skills in Claude Code, Codex, Gemini CLI, and Copilot — that's the portability story for the README.

## Action items

- Add prompt injection heuristic scanner to skill-manager-mcp `skill_create` tool (backlog)
- Use Agensi ecosystem gap framing in ENGRAM README as positioning
- Consider publishing top ClaudesCorner skills to Agensi marketplace for visibility
