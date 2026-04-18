---
title: "Cloudflare Artifacts — Git-Native Versioned Storage for Agents"
date: 2026-04-17
source: https://blog.cloudflare.com/artifacts-git-for-agents-beta/
hn: https://news.ycombinator.com/item?id=47792374
hn_points: 152
tags: [agent-infrastructure, storage, cloudflare, git, versioning]
relevance: agent-workflows, session-state, parallel-agents
---

## Summary

Cloudflare Artifacts is a Git-compatible versioned storage system purpose-built for AI agents. Private beta April 2026; public beta early May 2026.

## Technical Architecture

- **Git implementation in Zig → WASM** (~100KB binary, no external deps): covers SHA-1, zlib, delta encoding, pack parsing, full git smart HTTP protocol (v1 + v2)
- **Storage**: Durable Objects (SQLite, 2MB row limit — large objects chunked), R2 for snapshots, KV for auth token tracking
- **Streaming**: fetch and push both streamed to stay within ~128MB memory constraint
- **git-notes support**: agent metadata attached without mutating objects

## What It Enables

- Per-session repo provisioning alongside agent sessions or sandboxes
- Fork repos into isolated copies for parallel agent work
- Session state persistence tied to file versioning (prompt + file history = time travel)
- Cross-team collaboration via shareable session URLs
- **ArtifactFS**: open-source lazy-hydration tool for mounting large repos fast

## Pricing

| Resource | Rate |
|---|---|
| Operations | $0.15 / 1k (first 10k/month free) |
| Storage | $0.50 / GB-month (first 1 GB free) |

Available to paid Workers plan first; Free plan rollout planned.

## Relevance to Jason's Work

- **Parallel dispatcher**: per-dispatch-worker isolated repo = clean audit trail per task run
- **ENGRAM**: Artifacts could back session-state versioning — each HEARTBEAT write becomes a commit
- **bi-agent / fabric-mcp**: agent-produced outputs (DAX queries, KPI reports) get full git history without instrumenting a real repo
- Agents "know Git" from training — no new protocol distribution needed; pairs naturally with Claude Code's file editing model
- No MCP integration announced yet, but the operational API is REST + git-over-HTTP — wrappable as an MCP tool

## Key Differentiators vs S3/R2

- Git semantics (branch, diff, merge) not just object storage
- Purpose-built for agent-scale ephemeral sessions
- Operational pricing model reflects agent call patterns (many small ops, not bulk storage)
