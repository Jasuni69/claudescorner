---
title: "Thunderbolt (Mozilla/Thunderbird) — Self-Hosted AI Client with MCP Registry"
source: https://github.com/thunderbird/thunderbolt
date: 2026-04-19
tags: [ai-client, mcp, self-hosted, data-sovereignty, mozilla, tauri, vendor-lock-in]
stars: 2000
relevance: MCP ecosystem, ENGRAM deployment, Fairford on-prem requirement
---

## Summary

Thunderbolt is Mozilla/Thunderbird's open-source AI client addressing vendor lock-in. TypeScript + Tauri (Rust), cross-platform (Mac/Linux/Windows/iOS/Android), MPL-2.0. Users bring their own model (Ollama, llama.cpp, or any OpenAI-compatible endpoint). MCP Registry referenced in codebase — positions this as an agent-ready client that consumes MCP tool surfaces. Active development (2k stars, updated minutes before this clip).

## Architecture

- **Frontend**: TypeScript/React (97.7% of codebase)
- **Desktop shell**: Tauri (Rust bridge) — lightweight, no Electron overhead
- **Mobile**: iOS + Android via Tauri
- **Backend**: Node.js, PowerSync for data sync, Drizzle ORM
- **Deployment**: Docker Compose or Kubernetes on-prem

## Model Support

| Mode | Provider |
|---|---|
| Local | Ollama, llama.cpp |
| Cloud API | Any OpenAI-compatible endpoint (Claude via proxy) |
| Enterprise | Custom API config |

No hosted inference — fully BYOM (bring your own model).

## MCP Integration

MCP Registry referenced in codebase — users can wire in MCP tool surfaces. Exact integration depth unknown from README alone; warrants a follow-up read of the MCP integration code.

## Data Ownership Model

On-prem deployment as primary target. No telemetry to external hosts. Conversation history, model config, and usage data remain in user-controlled infrastructure. MPL-2.0 ensures source remains open even in commercial forks.

## Relevance to ClaudesCorner

| Concern | Thunderbolt angle |
|---|---|
| Fairford on-prem requirement | Self-hosted AI client with K8s deploy = Fabric-compatible deployment target |
| fabric-mcp MCP surface | MCP Registry = potential drop-in consumption layer |
| ENGRAM distribution | Thunderbolt as ENGRAM-compatible client host (skill-manager-mcp wired as MCP server) |
| Vendor lock-in avoidance | Tauri + BYOM = zero Anthropic/OpenAI dependency for UI layer |

## Action Items

- Read `mcp/` folder in repo to understand integration depth
- Assess as Fairford PoC UI layer alternative to Claude Desktop
- Flag if Sandbox Agents (OpenAI SDK) + Thunderbolt form a complete self-hosted stack
