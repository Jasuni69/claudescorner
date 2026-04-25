---
title: "SoK: Security of Autonomous LLM Agents in Agentic Commerce"
source: https://arxiv.org/abs/2604.15367
clipped: 2026-04-20
hn_points: 3
tags: [security, agents, mcp, autonomous, dispatch, agentkey]
---

# SoK: Security of Autonomous LLM Agents in Agentic Commerce

**Source:** https://arxiv.org/abs/2604.15367  
**HN:** https://news.ycombinator.com/newest (2026-04-20)

## Summary

Systematization of Knowledge paper mapping the security landscape for autonomous LLM agents operating in financial and commercial transactions — agents that independently negotiate, purchase services, manage assets, and execute on-chain/off-chain transactions.

## Key Finding

Securing agentic commerce is a **cross-layer problem**: emerging agent-payment protocols (ERC-8004, AP2, x402, ACP, ERC-8183, MPP) each introduce novel attack surfaces that individually seem contained but cascade catastrophically across layers.

The paper derives **12 cross-layer attack vectors** organized across five dimensions:

1. **Agent integrity** — prompt injection, jailbreaks, goal drift under long-horizon tasks
2. **Transaction authorization** — replay attacks, unsigned delegation, privilege escalation via tool chaining
3. **Inter-agent trust** — impersonation in multi-agent pipelines, unverified sub-agent spawning
4. **Market manipulation** — collusion between agents, synthetic demand signals
5. **Regulatory compliance** — jurisdictional ambiguity when agents act as legal entities

## Mitigations Proposed

Layered defense architecture spanning:
- Authorization gap coverage in agent-payment protocols
- Identity verification at each agent-to-agent handoff
- Audit trails for autonomous transaction chains

## Relevance to ClaudesCorner

- **dispatch.py workers**: inter-agent trust dimension maps directly to sub-agent spawning in dispatch; unverified worker identity = attack vector 3
- **AgentKey**: the paper's identity+authorization recommendations validate AgentKey's append-only audit + one-click revoke design; fills the "transaction authorization" gap
- **AgentRQ**: human-in-loop escalation covers the authorization gap for high-stakes tool calls
- **fabric-mcp**: any Fabric execution triggered by agents carries the "transaction authorization" risk; `verify:` step in worker prompts is the mitigation
- The 12 attack vectors map cleanly onto ENGRAM's memory-write authority governance model — cross-agent handoff protocol already addresses attack vector 3 partially
