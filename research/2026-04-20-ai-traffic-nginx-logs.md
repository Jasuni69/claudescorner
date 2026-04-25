---
title: "AI Traffic vs Referral Traffic in Nginx Logs"
date: 2026-04-20
source: https://surfacedby.com/blog/nginx-logs-ai-traffic-vs-referral-traffic
tags: [ai-agents, crawlers, discoverability, mcp, robots-txt, agent-identity]
hn_pts: 106
hn_comments: 18
relevance: medium-high
---

# I Prompted ChatGPT, Claude, Perplexity, and Gemini and Watched My Nginx Logs

**Source:** surfacedby.com | HN 106pts / 18 comments

## What the Author Found

After prompting four major AI assistants about their site content, they watched Nginx logs to see which providers actually fetched origin content vs answered from cached index.

## Agent Behavior Breakdown

### Clearly announced themselves:
| Agent | User-Agent | Behavior |
|---|---|---|
| **Claude** | `Claude-User/1.0` | Always checks `robots.txt` first; fetches from Anthropic IP space |
| ChatGPT | `ChatGPT-User/1.0` | Fetches from multiple Azure IP ranges |
| Perplexity | `Perplexity-User/1.0` | Direct fetches |
| Manus | Browser-style with explicit suffix | Full rendering |
| Meta AI | `meta-webindexer/1.1` | Retrieval behavior |

### Invisible or indistinguishable:
| Agent | Behavior |
|---|---|
| **Gemini** | **Zero requests** — answered entirely from cached Google index |
| Copilot | Arrives as plain Chrome browser, indistinguishable from humans |
| Grok | Appears as Safari/Chrome, no distinct identifier |

## Key Structural Finding

The asymmetry is not random — it's architectural:
- **Announced agents** (Claude, ChatGPT, Perplexity) give you control via `robots.txt` targeting `Claude-User` specifically
- **Ghost agents** (Gemini, Copilot, Grok) make log-based access measurement fundamentally unreliable
- Gemini's behavior means Google's AI has already indexed everything — real-time fetch is optional for them

## Relevance to ClaudesCorner

- **Claude-User/1.0 + robots.txt**: Claude respects robots.txt exclusions — any service restricting Claude access can do so surgically without blocking Google; flip side: ENGRAM public endpoints should *allow* Claude-User explicitly
- **MCP discoverability**: The `Is It Agent Ready?` pattern (already in MEMORY.md) maps directly — well-known agent discovery files (/.well-known/agent-skills.json) would show up in announced-agent logs but not ghost-agent logs
- **fabric-mcp + skill-manager-mcp**: Both are MCP servers behind auth — no crawl exposure risk; this analysis validates MCP-over-HTTP as the correct agent access layer (not public web pages)
- **ENGRAM positioning**: An ENGRAM-powered service that explicitly permits `Claude-User` in robots.txt and exposes `/.well-known/agent-skills.json` gets maximum announced-agent reach while Gemini free-rides from cache anyway

## Signal

Claude is the *most transparent* AI agent in web access patterns — always announces, always checks robots.txt. This is both a constraint (can be blocked) and a trust signal (can be audited). For Fairford Phase 2 web-facing endpoints, explicitly allowing `Claude-User` in robots.txt + exposing agent-ready discovery files maximizes Claude Code integration surface.
