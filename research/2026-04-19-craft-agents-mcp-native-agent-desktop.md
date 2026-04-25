---
title: "Craft Agents OSS — MCP-Native Agent Desktop with Claude Agent SDK"
date: 2026-04-19
source: https://github.com/lukilabs/craft-agents-oss
stars: 4385
stars_today: +139
tags: [ai-agents, mcp, claude-agent-sdk, session-management, dispatch, obsidian, headless]
relevance: high
---

# Craft Agents OSS — MCP-Native Agent Desktop with Claude Agent SDK

**GitHub:** github.com/lukilabs/craft-agents-oss | 4,385 stars | +139 today | Apache 2.0

## What It Is

Open-source desktop application + server framework for building agent-native workflows. Document-centric interface over Claude Agent SDK — multi-session inbox, MCP-first data sources, permission modes. Built by a team that "uses Craft Agents to build Craft Agents."

## Architecture

```
apps/
├── cli/      — terminal client (craft-cli)
└── electron/ — desktop GUI (React + Vite + shadcn)

packages/
├── core/      — shared TypeScript types
└── shared/    — business logic
    ├── agent/       — CraftAgent, permissions
    ├── credentials/ — AES-256-GCM encrypted
    ├── sessions/    — persistence
    ├── sources/     — MCP, API, filesystem
    └── statuses/    — dynamic workflow states
```

Built with Bun. Multi-provider: Anthropic, OpenAI, Google AI Studio, GitHub Copilot.

## Key Features

**Session Workflow:**  
Todo → In Progress → Needs Review → Done — customizable status states per workspace.

**MCP Integration:**  
32+ Craft document tools. Pre-wired: Linear, GitHub, Notion. Local stdio MCP servers. Remote MCP servers. Natural language setup ("add Linear as a source").

**Permission Modes:**  
- **Explore** — read-only  
- **Ask to Edit** — approval prompts  
- **Auto** — unrestricted  

**Skills:** workspace-level agent instructions per session context.

**File Handling:** images, PDFs, Office docs auto-converted on attachment.

**Event-driven automations** triggered by labels, schedules, or tool usage.

## Headless / Remote Mode

Server runs on VPS; desktop is a thin client. Long-running sessions persist. Multi-machine access. TLS + auth token config via env vars.

**CLI (`craft-cli`):**  
WebSocket-based. Interactive or scripted. `craft run` = self-contained: spawns server, runs prompt, exits. Ideal for CI/CD pipelines.

## Relevance to ClaudesCorner

- **dispatch.py workers** — `craft run` = single-shot agent execution mirroring dispatch.py worker pattern; headless server = persistent orchestration layer
- **sessions management** — Todo→Done workflow maps directly to tasks.json queue model
- **MCP-native** — 32+ tools out of box including Obsidian vault access; complements memory-mcp and skill-manager-mcp
- **Claude Agent SDK** — same SDK powering memory-mcp/engram; Craft wraps it in desktop UX
- **ENGRAM** — Craft's Skills system = ENGRAM SOUL.md equivalent per workspace; session persistence = HEARTBEAT analog
- **credential governance** — AES-256-GCM at rest, same pattern as AgentKey; gap fills dispatch.py worker credential handling
- **Gap:** no fabric-mcp integration yet = Fairford PoC opportunity (add Fabric as Craft source)
