---
title: "Guardrails for Agentic Development — Two-Loop Security Architecture (Checkmarx, April 23, 2026)"
source: https://checkmarx.com/blog/guardrails-for-agentic-development/
date: 2026-04-24
clipped: 2026-04-24
tags: [security, ai-agents, guardrails, supply-chain, mcp, dispatch, agent-governance]
relevance: dispatch.py worker security, MCP server trust model, AgentKey+Sunglasses+CrabTrap stack, Fairford Phase 2 security checklist
---

# Guardrails for Agentic Development

**Source:** Checkmarx blog, April 23, 2026  
**Context:** Published one day after Checkmarx's own tools were backdoored — makes the advice more credible, not less.

## Core Thesis

AI generates code faster than security teams can review it. Traditional "gate at the end" models fail at agent velocity. The solution is **security embedded in the development loop**, not appended to it.

## Two-Loop Architecture

```
[Inner Loop — Prevention]
  Developer Assist → real-time analysis → catch before code propagates

[Outer Loop — Enforcement]
  Integration-stage scanning → Triage Assist + Remediation Assist
  → contextual exploitability → only surface actually reachable vulns
```

## Six Operational Controls

1. **Govern AI as first-class assets** — centralized inventory of coding tools, agents, model dependencies (= AgentKey pattern)
2. **Risk-based prioritization** — suppress non-exploitable findings; focus on contextual exploitability (= bi-agent 3-layer oracle)
3. **Centralize supply chain controls** — dependency provenance validation, SBOM/AI-BOM (= SHA-pinned actions, vendored deps)
4. **Establish agentic guardrails** — unique agent identities, permission boundaries, auditable action logs (= AgentKey + CrabTrap + Sunglasses)
5. **Standardize prompts** — approved templates, validation policies, activity logging (= dispatch.py worker prompt standards + task_plan.md injection)
6. **Measure via operational metrics** — time-to-fix, policy compliance, risk reduction (= kpi-monitor + HEARTBEAT log)

## Attack Vectors Explicitly Addressed

- **Supply chain compromise**: malicious dependencies substituted into execution environments
- **Prompt injection + sandbox bypass**: demonstrated via Cursor IDE attack; developer tools as attack surface
- **Automated exploitation at scale**: attackers using GenAI to generate custom exploits faster
- **Trust-based manipulation**: systems auto-executing untrusted external artifacts

## Signal for ClaudesCorner

The two-loop model maps cleanly onto the existing dispatch.py + governance stack:

| Checkmarx Layer | ClaudesCorner Equivalent |
|---|---|
| Developer Assist (inner loop) | Sunglasses inbound scanner at worker input boundary |
| Triage/Remediation Assist (outer loop) | CrabTrap outbound MITM + AgentKey audit log |
| Unique agent identities | AgentKey per-worker credential scoping |
| Auditable action logs | CrabTrap PostgreSQL audit trail |
| Approved prompt templates | dispatch.py worker system prompts + task_plan.md |

**Gap identified**: No equivalent of "SBOM/AI-BOM" for MCP server dependencies. Before Fairford Phase 2, enumerate all transitive deps of fabric-mcp, memory-mcp, skill-manager-mcp and lock them.

**Immediate action**: Add `deny: external_tool_auto_execute` to dispatch.py worker frontmatter — prevents workers from auto-running downloaded artifacts without a verify oracle step.
