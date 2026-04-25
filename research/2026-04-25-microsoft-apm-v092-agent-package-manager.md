---
title: "Microsoft APM v0.9.2 — Agent Package Manager"
source: https://github.com/microsoft/apm
date: 2026-04-25
stars: 2033
tags: [agent-tooling, mcp, claude-code, engram, microsoft, package-manager]
signal: high
---

# Microsoft APM v0.9.2 — Agent Package Manager

**Repo:** microsoft/apm — 2,033 stars (+242 this week)
**Latest release:** v0.9.2 (2026-04-23)

## What it is

APM is an open-source dependency manager for AI agents — the `npm`/`pip` equivalent for agent configuration. A single `apm.yml` manifest declares all agent dependencies (instructions, skills, prompts, agents, hooks, plugins, MCP servers). `apm install` reproduces an identical setup on any machine and any supported coding client.

## apm.yml manifest format

```yaml
name: your-project
version: 1.0.0
dependencies:
  apm:
    - anthropics/skills/skills/frontend-design
    - github/awesome-copilot/plugins/context-engineering
    - github/awesome-copilot/agents/api-architect.agent.md
    - microsoft/apm-sample-package#v1.0.0
  mcp:
    - name: io.github.github/github-mcp-server
      transport: http
```

Lock file `apm.lock.yaml` pins resolved sources + content hashes (full provenance, like `package-lock.json`).

## v0.9.x changelog (2026-04-21 → 2026-04-23)

**v0.9.0 (Apr 21)**
- `--mcp` flag: declarative MCP server addition to `apm.yml` from CLI
- Shell-string validation for MCP stdio entries
- Transport selector (strict-by-default: http vs stdio)
- Multiple targets support in config + CLI
- VS Code adapter fixes for HTTP/SSE remote MCP servers
- 75+ new unit tests

**v0.9.1 (Apr 22)**
- APM self-migrated to `.apm/` directory structure
- Policy enforcement at install time (not just audit time)
- Azure DevOps authentication via Entra ID (AAD) bearer tokens

**v0.9.2 (Apr 23)**
- Installation fixes for port handling and custom hosts
- Governance guide + enterprise adoption playbook docs
- Tutorial rewrite for first-package setup

## Security model

- Unicode prompt-injection scan at `apm install` time (blocks compromised packages before agent access)
- `apm audit` on-demand security check
- Transitive MCP servers require **explicit consent** — trust doesn't cascade automatically
- `apm-policy.yml` defines org-wide allowable sources/scopes/primitives
- Tighten-only inheritance: enterprise → org → repo (no scope escalation downstream)
- GitHub rulesets integration for CI/CD policy gates

## Supported platforms

GitHub Copilot, Claude Code, Cursor, OpenCode, Codex (MCP limitations noted for Codex CLI)

## Install

```bash
# Windows
irm https://aka.ms/apm-windows | iex
# Or: scoop install apm

# Linux/macOS
curl -sSL https://aka.ms/apm-unix | sh
# Or: brew install microsoft/apm/apm

# Add a package
apm install microsoft/apm-sample-package#v1.0.0
apm marketplace add github/awesome-copilot
apm install --mcp io.github.github/github-mcp-server --transport http
```

## Relevance to ClaudesCorner / ENGRAM

**Highest-priority signal:** `apm.yml` is the missing portable bootstrap manifest for ENGRAM. Currently ENGRAM requires manual wiring of SOUL.md + HEARTBEAT.md + memory-mcp + skill-manager-mcp across machines. An `apm.yml` at the ENGRAM repo root would declare all of these as versioned, reproducible dependencies — one `apm install` bootstraps the full stack on any machine or client.

- **skill-manager-mcp** already speaks the agentskills.io SKILL.md format that APM's `apm:` block installs. APM is the distribution layer skill-manager-mcp currently lacks.
- **MCP wiring**: `apm install --mcp` declaratively adds servers to `.mcp.json` — eliminates manual `settings.json` edits for memory-mcp, fabric-mcp, etc.
- **Security**: Unicode prompt-injection scan + explicit transitive MCP consent fills the skill-manager-mcp `injection_guard` gap for third-party skill installs.
- **Entra ID auth (v0.9.1)**: Azure DevOps backend for APM packages = Fairford-compatible enterprise skill registry without running a separate server.
- **agentrc complement**: APM + agentrc (codebase analysis → tailored `.instructions.md`) together cover the CLAUDE.md generation gap ENGRAM currently leaves manual.

## Action items

- [ ] Author `apm.yml` at `github.com/Jasuni69/engram` root declaring SOUL.md + HEARTBEAT.md + memory-mcp + skill-manager-mcp as dependencies
- [ ] Test `apm install --mcp` for fabric-mcp, memory-mcp, skill-manager-mcp to replace manual settings.json wiring
- [ ] Evaluate `apm-policy.yml` as governance layer for Fairford Phase 2 skill installs (restricts sources to trusted orgs)
- [ ] Wire `apm audit` into dispatch.py pre-task skill validation step
