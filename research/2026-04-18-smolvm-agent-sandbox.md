---
title: "smolvm — Sub-200ms Coldstart Portable VMs for Agent Sandboxing"
date: 2026-04-18
source: https://github.com/smol-machines/smolvm
hn: https://news.ycombinator.com/item?id=43715234
hn_points: 241
tags: [agent-sandboxing, infrastructure, dispatch, security]
relevance: high
---

## What It Is

smolvm is a CLI tool for running isolated Linux VMs locally. Workloads run in hardware-isolated environments and can be packaged into portable self-contained `.smolmachine` binaries.

## Key Specs

| Metric | Value |
|--------|-------|
| Cold start | <200ms |
| Default vCPUs | 4 |
| Default RAM | 8 GiB (elastic via virtio balloon) |
| Platforms | macOS Apple Silicon/Intel, Linux x86_64/aarch64 |

Built on libkrun VMM + custom kernel (libkrunfw). Uses Hypervisor.framework on macOS, KVM on Linux.

## Security Model

- Network isolation by default
- Optional SSH agent forwarding
- Egress filtering via host allowlists
- Real hardware isolation — own kernel per workload

## Agent Sandboxing Relevance

**dispatch.py workers**: Each parallel worker could run in an ephemeral smolvm instance — credential isolation, no cross-worker state bleed, <200ms startup overhead is acceptable for the task sizes dispatch.py handles.

**Untrusted code execution**: Any skill or subagent that runs arbitrary code (bi-agent DAX execution, fabric-mcp mutations) could be sandboxed without Docker overhead.

**Comparison to alternatives**: Firecracker requires more setup; gVisor/Docker don't give hardware isolation. smolvm is the simplest path to real VM isolation on macOS/Linux with agent-friendly coldstart.

## Action Items

- [ ] Evaluate smolvm as execution backend for dispatch.py workers (replace bare subprocess calls)
- [ ] Check `.smolmachine` packaging — could bundle skill execution environments portably
- [ ] Monitor for Windows support (currently macOS/Linux only — blocks direct use on ClaudesCorner Windows host)
