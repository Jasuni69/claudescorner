---
title: "Broccoli: Linear Ticket → GitHub PR Agent, Self-Hosted on GCP, Claude + Codex"
date: 2026-04-22
source: https://github.com/besimple-oss/broccoli
tags: [agent-ci, claude-code, automation, github, linear, gcp, multi-model]
relevance: [dispatch.py external PR automation, multi-model routing, self-hosted agent infra]
stars: 100
hn_pts: ~32
---

# Broccoli — Linear Ticket to Shipped PR, Powered by Claude + Codex on GCP

**Source:** github.com/besimple-oss/broccoli (Show HN, 2026-04-22, ~32 pts)  
**Stars:** 100 (early, rising)

## What It Is

Broccoli is a self-hosted, webhook-driven CI agent that converts Linear tickets into merged GitHub pull requests with zero human intervention in the coding loop. It runs on Google Cloud Run and uses Claude and/or Codex (user-configurable) as the AI backbone.

## Architecture

```
Linear webhook → FastAPI (broccoli-oss-service)
                    ↓
              PostgreSQL (durable job state)
                    ↓
         Cloud Run runner (broccoli-oss-runner)
              ↙              ↘
        Claude CLI         Codex CLI
        (planning)       (generation)
                    ↓
         GitHub PR + AI code review comment
```

**Two Cloud Run workloads:**
- `broccoli-oss-service` — FastAPI, handles GitHub + Linear webhooks, signature verification, delivery deduplication
- `broccoli-oss-runner` — executes Claude/Codex against vendored prompt templates, opens PRs

**State:** PostgreSQL (jobs, webhooks, PRs, config)  
**Secrets:** Google Cloud Secret Manager (no secrets in code)

## Trigger Pattern

When a Linear issue is assigned to a designated bot user with a routing label → Broccoli auto-plans → auto-implements → opens GitHub PR → Claude performs AI code review with actionable comments.

## Key Differentiators

1. **Self-hosted / zero external control plane** — "Your infra. Your keys. Your data"
2. **Multi-model configurable** — Claude for planning, Codex for generation (or either for both)
3. **Webhook deduplication** — durable job state prevents double-execution
4. **Versioned prompt templates** — fork and co-locate prompts with codebase

## Relevance to ClaudesCorner

| Angle | Implication |
|-------|-------------|
| **dispatch.py** | Concrete production pattern for external PR submission from an agent — velocity cap lesson applies (see GitHub 500 PRs ban clip) |
| **Multi-model routing** | Claude (planning) + Codex (generation) split mirrors dispatch.py Sonnet/Haiku tier separation |
| **Self-hosted agent infra** | GCP Cloud Run + PostgreSQL = lightweight persistent agent infra alternative to k8s; Fairford PoC relevant |
| **Prompt templates versioned in repo** | Validates dispatch.py worker prompt-as-code approach |

## Caveats

- 100 stars at clip time — early project, unproven at scale
- No MCP integration — gap relative to dispatch.py worker architecture
- GCP-only deployment (not Azure) — friction for Fairford Azure-first stack
- No verify oracle — PRs merged without machine-readable correctness gate
