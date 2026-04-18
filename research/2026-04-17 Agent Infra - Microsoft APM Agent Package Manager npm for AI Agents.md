---
title: "Microsoft APM — Agent Package Manager (npm for AI Agents)"
date: 2026-04-17
source: https://github.com/microsoft/apm
tags: [mcp, agent-skills, microsoft, package-manager, ci-cd, infrastructure]
stars: 1799
relevance: high
---

# Microsoft APM — Agent Package Manager

**GitHub:** https://github.com/microsoft/apm  
**Stars:** 1,799 (+363 today)  
**Maintainer:** Microsoft (community-driven)

## What it is

APM is a dependency manager for AI agents — npm/pip/Cargo but for agent configuration. Declares instructions, skills, prompts, agents, hooks, plugins, and MCP servers in a single `apm.yml` manifest. Teams share fully configured agent setups with reproducibility and portability.

## Core problem solved

AI coding agents need significant context setup (standards, prompts, skills, plugins) but developers configure this manually with no reproducibility. APM makes agent configuration declarable, shareable, and versionable.

## apm.yml manifest covers

- Instructions
- Skills
- Prompts
- Agents
- Hooks
- Plugins
- **MCP servers**

## Key features

- **Multi-source install** — GitHub, GitLab, Bitbucket, Azure DevOps, any git host
- **Transitive dependencies** — packages can depend on other packages
- **Security scanning** — `apm audit` for hidden Unicode; install-time compromise protection
- **Marketplace support** — curated registries via `apm-policy.yaml`
- **GitHub Actions** — `microsoft/apm-action` for CI/CD agent config deployment

## Install

```bash
# Unix
curl -sSL https://aka.ms/apm-unix | sh

# Windows
irm https://aka.ms/apm-windows | iex

apm install microsoft/apm-sample-package#v1.0.0
```

## Built on open standards

AGENTS.md + Agent Skills + Model Context Protocol (MCP) — same stack as skill-manager-mcp.

Companion tool: `agentrc` (microsoft/agentrc) generates tailored agent instructions from codebases.

## Relevance

Direct analog to the ClaudesCorner skill-manager-mcp + dispatch.py stack — but Microsoft-flavored and portable across teams. The `apm.yml` manifest pattern is worth adopting for ENGRAM: a declarable, versionable agent config format would make ENGRAM significantly more shareable. The MCP server dependency declaration in `apm.yml` is the missing piece in current ENGRAM bootstrap docs. Action: check if ENGRAM's `setup.md` should adopt an `apm.yml`-compatible manifest format.
