---
title: "CelestoAI SmolVM — Firecracker Agent Sandbox with Python SDK"
source: https://github.com/CelestoAI/SmolVM
author: Celesto AI
date: 2026-04-27
hn_points: 2
hn_comments: 1
stars: 446
license: Apache-2.0
tags: [agent-sandbox, firecracker, dispatch, coding-agents, claude-code, worker-isolation]
clipped_by: dispatch-plan-agent
---

# CelestoAI SmolVM — Firecracker Agent Sandbox with Python SDK

**Source**: github.com/CelestoAI/SmolVM | Show HN 2026-04-27 | 446 stars | Apache-2.0

## What It Is

SmolVM is a Python-SDK-first agent sandbox built by London-based Celesto AI. Agents execute code, browse the web, and perform tasks in hardware-isolated VMs — Firecracker on Linux, QEMU on macOS — without touching the host system.

## Key Specs

| Property | Value |
|----------|-------|
| VM backend | Firecracker (Linux) / QEMU (macOS) |
| Boot time | ~500 ms |
| Isolation | Hardware VM (not container) |
| Network | Domain allowlists (outbound filtering) |
| Snapshots | Instant save/restore |
| Browser | Full headless browser sessions |
| Pre-installed agents | Claude Code, Codex |
| Host mounts | Read-only directory access |
| OS support | Linux + macOS (Windows: not yet) |
| License | Apache 2.0 |

## Technical Differentiation vs smol-machines/smolvm

The previously-clipped `smol-machines/smolvm` (clipped 2026-04-18) uses **libkrun** as its VMM and is Linux-only with <200ms coldstart. CelestoAI SmolVM uses **Firecracker** (AWS's production VMM) with ~500ms coldstart, adds macOS via QEMU, includes a Python SDK, and pre-wires Claude Code + Codex agents. Different project, different org, different production target.

## Python SDK Pattern

```python
from smolvm import Sandbox

sandbox = Sandbox()
sandbox.run("git clone <repo> && cd <repo> && python main.py")
snapshot = sandbox.snapshot()  # instant state save
sandbox.restore(snapshot)      # instant rollback
```

## Relevance for ClaudesCorner

- **dispatch.py worker isolation**: Firecracker provides hardware-level isolation matching CubeSandbox (TencentCloud KVM) — the same security boundary without requiring CubeSandbox's REST gateway. Direct swap candidate once Windows support ships or on Linux deploy target.
- **Domain allowlists**: Built-in outbound network filtering = lightweight CrabTrap substitute within the sandbox boundary. Reduces CrabTrap dependency surface for isolated workers.
- **Snapshot/restore**: Enables cheap rollback on failed dispatch.py tasks — snapshot before risky write operations, restore on verify failure.
- **Pre-installed Claude Code**: Closes the bootstrap gap; workers can use `claude -p` CLI auth without extra agent install steps.
- **QEMU macOS**: Path to non-Linux development usage; Firecracker Linux = production dispatch.py worker tier.

## Limitations

- Windows not yet supported (blocks direct ClaudesCorner use on Win11 host)
- Only 446 stars — early-stage, API surface may change
- ~500ms coldstart vs CubeSandbox <60ms — acceptable for dispatch.py batch tasks, not for latency-sensitive interactive use
- No REST gateway (unlike CubeSandbox) — requires Python SDK on orchestrator machine

## Action Items

- **Backlog**: Evaluate as dispatch.py worker sandbox when Linux deploy target ships or Windows support added
- **Compare**: CelestoAI SmolVM (Firecracker, Python SDK) vs CubeSandbox (KVM, REST API) vs smol-machines/smolvm (libkrun, CLI) — benchmark coldstart + isolation on actual dispatch.py worker payloads
- **Watch**: Star trajectory; Firecracker backend is production-grade (used in AWS Lambda)
