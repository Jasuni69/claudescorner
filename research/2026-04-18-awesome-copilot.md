---
title: "awesome-copilot — GitHub's community skill/agent/hook repo"
date: 2026-04-18
source: https://github.com/github/awesome-copilot
stars: 30253
stars_today: 194
tags: [skills, agents, hooks, mcp, claude-code, copilot, developer-tooling]
relevance: skill-manager-mcp, ENGRAM, hooks architecture
---

# awesome-copilot

**GitHub's official community repo for Copilot extensions — agents, skills, hooks, instructions, and plugins.**

## What it is

A curated, community-driven collection targeting GitHub Copilot but directly parallel to ClaudesCorner's own skill/agent architecture. 30k stars, actively maintained by GitHub.

## Content categories

| Category | Description |
|---|---|
| **Agents** | Specialized Copilot agents that integrate with MCP servers |
| **Instructions** | Coding standards applied automatically by file pattern |
| **Skills** | Self-contained folders with instructions + bundled assets |
| **Plugins** | Curated bundles of agents and skills for specific workflows |
| **Hooks** | Automated actions triggered during Copilot agent sessions |
| **Agentic Workflows** | AI-powered GitHub Actions automations written in markdown |
| **Cookbook** | Copy-paste recipes for working with Copilot APIs |

Install via: `copilot plugin install <plugin-name>@awesome-copilot`

## Why it matters

- **Skill format convergence**: Their skill structure (self-contained folder + instructions + assets) is converging on the same pattern as `anthropics/skills` and skill-manager-mcp's SKILL.md format. Worth monitoring for cross-pollination.
- **Hooks pattern**: Hooks-triggered-on-agent-session directly mirrors ClaudesCorner's PostToolUse/PostCompact hook architecture in settings.json. Their hook examples are a free pattern library.
- **MCP-integrated agents**: Their agents section documents how to wire MCP servers into agent sessions — directly applicable to how skill-manager-mcp and memory-mcp are wired.
- **Plugin bundles**: "Plugin = bundle of agents + skills" is the same composable unit as APM's `apm.yml` manifest (microsoft/apm, also trending today).

## Action items

- [ ] Skim hooks section for patterns not yet in ClaudesCorner settings.json
- [ ] Check if any skills overlap with installed superpowers skills — avoid duplication
- [ ] `apm.yml` manifest + awesome-copilot plugins = two convergent standards; ENGRAM should pick one as canonical export format
