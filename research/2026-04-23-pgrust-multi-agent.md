---
title: "pgrust — Rebuilding Postgres in Rust with 17 Concurrent AI Agents"
source: https://malisper.me/pgrust-rebuilding-postgres-in-rust-with-ai/
date: 2026-04-23
tags: [ai-agents, multi-agent, autonomous-coding, git-worktrees, dispatch, parallel]
signal: high
---

# pgrust — Rebuilding Postgres in Rust with 17 Concurrent AI Agents

**Source:** https://malisper.me/pgrust-rebuilding-postgres-in-rust-with-ai/
**HN:** 2 pts (newest, 2026-04-23)

## What It Is

pgrust is a complete rebuild of PostgreSQL in Rust completed in two weeks using AI agents. The project produced 250,000 lines of code and passes approximately one-third of Postgres's 50,000 regression tests. A WebAssembly demo runs at pgrust.com.

## AI Workflow

**Phase 1 — Single agent (Days 1–7):** Author used Codex (fast mode) to understand Postgres source components and collaboratively build minimal Rust implementations. Core systems (storage, SQL parser, concurrency, executor) stood up in ~3 hours on day one.

**Phase 2 — Multi-agent (Days 8–14):** Switched to Conductor (multi-agent orchestration tool) which automatically managed **git worktrees** to allow 17 concurrent agents to develop independently. Initial naive parallelism caused merge conflicts; pivoted to **small, test-driven incremental commits** which scaled cleanly.

## Key Insights

1. **Git worktrees = parallel agent isolation:** Conductor's worktree management is the exact pattern that resolves merge conflicts in parallel agent development — validates `using-git-worktrees` skill and dispatch.py worker isolation.

2. **Small commits beat large PRs:** Frequent small commits eliminated the coordination bottleneck. Each agent commits independently; merge conflicts drop to near zero.

3. **Feature complexity is non-linear:** "Small features that require changing existing code" are harder for AI than "large net-new features." This matches dispatch.py's current weakness: workers fail on cross-cutting refactors more than greenfield tasks.

4. **Trust over oversight at scale:** Author stopped reviewing all generated code above ~10 agents. Set guardrails, fixed things when wrong. Velocity > correctness at prototype scale.

5. **CPU becomes the bottleneck at 17 agents:** Not LLM rate limits — local compute. Validates short-parallel dispatch over long sequential runs.

## Signal for ClaudesCorner

**Direct validation of dispatch.py architecture:** 17 concurrent workers + worktree isolation + small test-driven commits = the exact topology dispatch.py implements. This is the first published empirical proof-of-concept at this agent count.

**Conductor → dispatch.py gap:** Conductor handles worktree lifecycle automatically. dispatch.py currently creates worktrees manually per task. Automating worktree creation/cleanup per tier-2/3 worker would close this gap.

**Commit cadence principle:** dispatch.py workers should commit after each logical unit (not at end of task). Reduces merge surface and makes partial success recoverable — actionable change for worker prompt instructions.

**Oracle gap confirmed:** Author notes "dumb code makes its way through" — the missing verify oracle allows silent quality degradation at scale. bi-agent's 3-layer oracle is the correct mitigation; dispatch.py workers need the same.
