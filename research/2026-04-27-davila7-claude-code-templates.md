---
title: "claude-code-templates — CLI tool for configuring and monitoring Claude Code"
source: https://github.com/davila7/claude-code-templates
author: davila7
date: 2026-04-27
clipped: 2026-04-27
stars: 25553
stars_today: 320
tags: [claude-code, mcp, agents, skills, hooks, templates, monitoring, analytics]
---

# claude-code-templates

**Source:** https://github.com/davila7/claude-code-templates
**Stars:** 25.6k (+320 today, GitHub Trending Python 2026-04-27)

## What It Is

A comprehensive CLI + web dashboard for discovering, installing, and monitoring Claude Code configurations. Covers agents, custom commands, MCP integrations, settings, hooks, and project templates. Installable via `aitmpl.com` or CLI.

## Key Components

### Component Library (100+ items)
- Pre-built specialist agents (security auditing, React optimization, database architecture)
- Custom command templates
- MCP server wiring configs
- Settings profiles and hook templates
- Reusable skills with progressive disclosure

### Claude Code Analytics
- Real-time session state detection
- Conversation Monitor with mobile-optimized interface
- Optional Cloudflare Tunnel support for remote monitoring
- Health diagnostics to optimize Claude Code installations
- Plugin dashboard for marketplace access and permission management

### Installation Pattern
Users browse at `aitmpl.com` or use CLI to select agents, commands, MCPs, settings, and hooks — either individually or as complete stacks. Interactive selection supports mixing components across sources.

## Attribution Sources
- Anthropic official skills
- K-Dense AI scientific skills (139 items)
- Community projects under MIT and Apache 2.0 licenses
- v1.28.3: added plugin skills support

## Signal for ClaudesCorner

**Skill scaffolding gap:** This is the closest public analog to what skill-manager-mcp does — but as a CLI/web tool rather than an MCP server. The analytics dashboard and session monitoring fill a genuine gap that ClaudesCorner's dispatch.py doesn't yet have (real-time burn-rate + session state visibility). Complements Fuelgauge (status line) and cc-canary (drift detection).

**Template import candidate:** The 100+ pre-built configurations are worth scanning for patterns applicable to dispatch.py worker prompts (especially the security auditing and database architecture specialists). The K-Dense AI scientific skills library (139 items) is an underexplored source for bi-agent oracle patterns.

**Plugin pattern reference:** v1.28.3 plugin skills model — skills bundled with MCP configs as a single installable unit — independently validates the ENGRAM plugin bundle pattern (Anthropic MCP Production Guide, Apr 23).

**Monitor architecture:** Cloudflare Tunnel + mobile-optimized session monitor = lightweight dispatch.py visibility layer without building a custom dashboard. Evaluate before investing in token-dashboard enhancements.

**Gap vs. skill-manager-mcp:** No semantic search, no write-gate, no agent_activation_allowed governance. skill-manager-mcp's FTS5+vector differentiation holds. This tool is complementary (discovery/install) not competitive (runtime governance).
