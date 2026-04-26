---
title: "Tensorlake — Starting 1000 Sandboxes in Parallel via Command Outbox"
date: 2026-04-25
source: https://www.tensorlake.ai/blog/starting-1000-sandboxes-in-parallel
stars: N/A
license: Proprietary (blog post, no OSS repo)
tags: [sandboxing, parallel-execution, dispatch-py, architecture, agent-infra]
signal: high
---

# Tensorlake — Starting 1000 Sandboxes in Parallel

**Source:** tensorlake.ai engineering blog · 2026-04-25  
**HN:** Newest (surfaced 2026-04-25)  
**Pattern:** Command Outbox + RocksDB + Long-polling Dataplane

## Problem

Standard distributed schedulers use reconciliation loops: every N seconds, compare desired vs actual state and issue corrective actions. When 1,000 sandbox requests arrive simultaneously, the scheduler processes them in batches on fixed ticks — the final sandbox in the queue may wait 10+ seconds before a start command is even issued.

For AI agent workloads (parallel eval benchmarks, multi-worker dispatch, RL environments), this tick-interval latency is unacceptable.

## Solution: Command Outbox Pattern

Replace reconciliation with a durable command outbox:

```
Request arrives
    ↓
Scheduler writes AddSandbox command to RocksDB outbox (transactional)
    ↓
Dataplane processes (4+ hosts) long-poll for new commands
    ↓
Commands retrieved within milliseconds of write
    ↓
Sandbox starts immediately — no tick wait
```

**Key invariant:** latency is now bounded by network RTT, not by scheduler tick interval.

## Architecture components

| Component | Role |
|---|---|
| Scheduler | Writes `AddSandbox` / `RemoveSandbox` commands transactionally to outbox |
| RocksDB | Persistent command store; sequence numbers enable durability tracking |
| Dataplane (4+ hosts) | Long-poll via gRPC; retrieve command batches; heartbeat back |
| Sequence numbers | Crashed scheduler recovers from RocksDB; regression triggers full sync |

## Performance

- **1,000 sandboxes** drain in **340ms** across 4 dataplane hosts
- Previous reconciliation approach: last sandbox waited 10+ seconds
- Observability improvement: direct metrics (backlog depth, drain rate) vs inferring state from reconciliation diffs

## Failure handling

- Scheduler crash: recover from RocksDB outbox (durable, no lost commands)
- Sequence number regression on reconnect: trigger full state sync
- Dataplane host loss: remaining hosts continue long-polling; no thundering herd

## Trade-offs

- Requires disciplined command-type management (add/remove/update as distinct types) — reconciliation's idempotency is simpler
- RocksDB dependency vs simpler in-memory state
- Long-poll connections must be managed (timeouts, reconnect logic)

## Relevance to ClaudesCorner

**dispatch.py v2 architecture reference:** Current dispatch.py uses a polling loop against `tasks.json`. The outbox pattern is the production-grade upgrade: write task commands transactionally, have worker processes long-poll rather than tick-check. This eliminates the N-second polling gap that creates latency between task creation and worker pickup.

**CubeSandbox integration:** Tensorlake's pattern maps directly to CubeSandbox (TencentCloud KVM, <60ms coldstart, E2B-SDK-compatible). The outbox scheduler + CubeSandbox REST gateway = complete parallel worker pool without spin-up serialization.

**dispatch.py doom-loop guard:** The sequence-number recovery pattern is a durable analog to the current `doom_loop_guard` in dispatch.py — instead of checking repeated tool patterns in-session, the outbox tracks command state persistently across crashes.

**Worker pool scaling:** Current 3-worker ceiling is a pragmatic CPU cap (per pgrust/Conductor findings). If that ceiling rises (e.g., moving to cloud workers), the outbox pattern handles 1000+ simultaneous submissions without architectural changes.

## Gaps / caveats

- No OSS repo; this is a Tensorlake proprietary implementation described in a blog post
- Pattern is well-known in distributed systems (Outbox Pattern, Transactional Outbox) — the innovation is applying it specifically to AI sandbox scheduling
- RocksDB dependency adds operational overhead vs simple SQLite queue

## Action items

- Evaluate replacing `tasks.json` polling with a SQLite-backed command outbox for dispatch.py v2
- Wire CubeSandbox REST gateway behind outbox scheduler as worker isolation layer
- Reference arXiv 2512.24601 (RLM) alongside this post — both address parallel agent execution at different layers (inference vs infrastructure)
