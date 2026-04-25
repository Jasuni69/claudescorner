---
title: "Building Agents That Reach Production Systems with MCP"
source: https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp
date: 2026-04-23
tags: [MCP, agents, production, authentication, Claude Code, skill-manager-mcp, fabric-mcp]
signal: high
clipped_by: dispatch-agent
---

# Building Agents That Reach Production Systems with MCP

**Source:** claude.com/blog | **HN:** 2 pts (newest, 2026-04-23) | **Author:** Anthropic

## Core Thesis

As agents move from local to cloud deployments, MCP provides the essential standardized layer for connecting to production systems. Three integration patterns exist — direct API calls, CLIs, and MCP — with MCP being preferred for portability across platforms, built-in auth handling, and rich semantics.

## Key MCP Design Patterns

### Tool Grouping — Intent Over Endpoints
> "A single `create_issue_from_thread` tool beats `get_thread` + `parse_messages` + `create_issue`"

Group tools by **user intent**, not API surface. Fewer, higher-level tools reduce model confusion and cut token overhead. For large service surfaces (AWS, Kubernetes), expose thin tools that accept code and run it in a sandboxed execution environment.

### Tool Search — 85% Token Reduction
MCP supports deferred tool loading. Tool search loads only matched tool definitions rather than the full catalog, cutting tool-definition tokens by **85%+** while maintaining selection accuracy. This is the same pattern Claude Code uses natively (`tool_search` baked into system prompt since Opus 4.7).

### Elicitation Extensions — OAuth Without Credential Exposure
Two elicitation modes for handling missing parameters or auth:
- **Form mode** — server pauses tool execution, requests user input via native UI forms
- **URL mode** — redirects to OAuth completion flows without exposing credentials to the model

URL mode is currently live in Claude Code; broader client adoption in progress.

### Vaults — Managed Credential Injection
Claude Managed Agents include **Vaults**: OAuth tokens stored once, auto-injected into MCP connections, with automatic token refresh. Eliminates the credential-in-prompt anti-pattern entirely.

### Skills + MCP Bundled as Plugins
Skills provide procedural knowledge for orchestrating MCP tools. The recommended pattern bundles both as a single plugin unit. Example: Claude's data analytics plugin = 10 skills + 8 MCP servers for analytics platform orchestration.

### Programmatic Tool Calling — 37% Token Reduction
Process tool results in code sandboxes rather than returning raw output to the model. Reduces tokens by ~37% on complex multi-tool workflows.

## Architecture Recommendation — Remote Servers

Build **remote MCP servers** (not local stdio) for production:
- Maximum distribution: web, mobile, cloud clients all connect
- CIMD (Client ID Metadata Documents) standardizes OAuth client registration with faster first-time flows
- Scales independently of the agent runtime

## Relevance to ClaudesCorner

| Pattern | Apply Where |
|---|---|
| Intent-grouped tools | fabric-mcp: collapse get_dataset + filter + format → single semantic tools |
| Tool search (85% saving) | skill-manager-mcp: already has FTS5+vector; confirm deferred-load wiring |
| Elicitation URL mode | memory-mcp: OAuth prompt flows for external write authority |
| Vaults pattern | dispatch.py workers: replace env-var credential passing with injected token pattern |
| Skills+MCP plugin bundle | ENGRAM: package memory-mcp + skill-manager-mcp skills as unified plugin |
| Remote server architecture | fabric-mcp: move from local stdio to remote HTTP for Fairford multi-client access |

## Signal

Anthropic's own production guidance validates the ClaudesCorner architectural bets: MCP-first stack, intent-based tool design, skill-manager-mcp semantic search. The Vaults + elicitation pattern fills the exact credential governance gap that AgentKey and CrabTrap address at the proxy layer — now confirmed as a first-party MCP feature.
