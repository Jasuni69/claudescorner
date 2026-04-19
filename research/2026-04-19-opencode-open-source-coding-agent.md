---
title: "OpenCode — Open-Source Coding Agent"
source: https://github.com/anomalyco/opencode
clipped: 2026-04-19
tags: [ai-agents, claude-code, mcp, open-source, coding-agent]
relevance: high
---

# OpenCode — Open-Source Coding Agent

**anomalyco/opencode** · 145.6k stars · +525 today · TypeScript

## What it is

Provider-agnostic open-source coding agent. Terminal-first TUI, built by neovim users. Runs client/server — can run on your machine while driven remotely from a mobile app.

## Architecture

Two built-in agents:
- **Build agent** — full-access default; reads, writes, executes
- **Plan agent** — read-only; analysis and exploration; denies file edits by default
- **@general subagent** — invoked via `@general` syntax for complex searches

## Key differentiators vs Claude Code

- 100% open-source codebase
- LSP (Language Server Protocol) support out-of-the-box
- Provider-agnostic: Claude, OpenAI, Google, local models
- MCP Registry integration for external tools
- Desktop apps for macOS, Windows, Linux (beta)

## Install

```sh
# npm
npm i -g opencode-ai

# curl
curl -fsSL https://opencode.ai/install | sh
```

## Relevance to ClaudesCorner

- Direct structural analog to Claude Code — plan/build agent split mirrors dispatch.py worker roles
- MCP Registry integration = same pattern as skill-manager-mcp tool discovery
- Provider-agnostic design validates bi-agent's Claude API approach; could swap to OpenCode shell if needed
- Open codebase = reference implementation for agent tool-use patterns
- LSP integration gap in current dispatch.py workers — worth investigating for code-edit quality
