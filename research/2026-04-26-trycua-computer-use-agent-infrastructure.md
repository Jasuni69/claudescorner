---
title: "trycua/cua — Computer-Use Agent Infrastructure with MCP + Claude Code Native"
date: 2026-04-26
source: https://github.com/trycua/cua
tags: [ai-agents, computer-use, sandbox, mcp, claude-code, dispatch]
stars: 14209
stars_today: 204
license: MIT
relevance: high
---

# trycua/cua — Computer-Use Agent Infrastructure

**14,209 stars | +204 today | MIT | HTML/Python/Swift/TypeScript**

## What It Is

Open-source platform for building, benchmarking, and deploying AI agents that control full desktop environments. Four products: Cua Driver (background macOS automation without stealing cursor/focus), Cua Sandbox (unified API for VMs/containers across macOS/Linux/Windows/Android), CuaBot (native desktop integration with H.265 compression), and Cua-Bench (evaluation against OSWorld/ScreenSpot/Windows Arena).

## Architecture

- **Sandbox layer**: Provisions and controls VMs/containers via identical interface (shell, screenshot, mouse/keyboard, gestures)
- **Local backend**: QEMU-based VMs supporting .qcow2/.iso BYOI; Lume for Apple Silicon via Virtualization.Framework
- **Cloud backend**: Linux containers, macOS, Windows, Android VMs
- **MCP server**: Included; Claude Code and Cursor integration confirmed
- **Claude Code plugin** baked in via CuaBot (`npx cuabot`)
- **Trajectory export**: Session recording as replayable trajectories for training/eval

## Install

```bash
pip install cua          # SDK
npx cuabot               # CuaBot desktop integration
```

## Signal for Jason's Stack

**dispatch.py worker isolation**: cua is the most complete cross-platform Computer-Use Agent sandbox with explicit Claude Code support. Compared to smolvm (Apple Silicon only, no Windows) and CubeSandbox (TencentCloud REST), cua runs natively on Windows via QEMU/cloud VM backends and ships an MCP server. It's the strongest candidate for dispatch.py browser worker isolation that actually works on Jason's Windows 11 machine without a REST gateway dependency.

**Key gap filled**: CubeSandbox (<60ms coldstart) remains faster for pure isolation, but cua's MCP-native + Claude Code integration means browser workers can be wired in without custom adapter code. `Cua Sandbox` unified API = one interface across all OS targets.

**ENGRAM parallel**: trajectory export (replayable session recordings) is the agent-memory equivalent of HEARTBEAT.md snapshots — sessions are resumable artifacts, not ephemeral.

**Evaluation**: Cua-Bench against OSWorld/Windows Arena gives a structured harness for measuring dispatch.py worker quality on desktop tasks — the eval pattern missing from current workers.

## Caution

- HTML-heavy repo (67.5% HTML) suggests frontend-heavy; Python core is 20.2%
- AGPL-3.0 dependency (ultralytics, optional) — check before Fairford use
- Windows support via QEMU adds VM overhead vs CubeSandbox's 5MB/instance KVM
- Verify MCP server is production-ready vs prototype before wiring into dispatch.py

## Action Items

- [ ] Test `pip install cua` + MCP server on Windows 11 dev machine
- [ ] Compare Cua Sandbox coldstart vs CubeSandbox (<60ms) for dispatch.py worker init latency
- [ ] Check if trajectory export format is compatible with HEARTBEAT.md session state
- [ ] Evaluate Cua-Bench harness as dispatch.py worker quality measurement framework
