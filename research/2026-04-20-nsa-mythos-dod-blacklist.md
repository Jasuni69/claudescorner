---
title: NSA Using Anthropic Mythos Despite DoD Blacklist
date: 2026-04-20
source: reuters.com (via HN item 47832222)
tags: [anthropic, mythos, governance, security, nsa, dod, restricted-access]
hn_points: 137
hn_comments: 100
---

# NSA Using Anthropic Mythos Despite DoD Blacklist

**Source:** Reuters / Axios, 2026-04-19  
**HN:** 137 points, 100 comments  
**URL:** reuters.com/business/us-security-agency-is-using-anthropics-mythos-despite-blacklist-axios-reports-2026-04-19/

## Key Facts

- The **Department of Defense** designated Anthropic as a **"supply chain risk"**, effectively blacklisting the company from defense contractor business — attributed to Anthropic's safety guardrails around model usage.
- Despite this designation, the **NSA is actively using Mythos** — Anthropic's most capable model, optimized for coding and agentic tasks, particularly cybersecurity vulnerability identification and exploit creation.
- Reveals a direct contradiction between stated DoD policy and operational practice at the agency level.

## What is Mythos

- Anthropic's most advanced model (beyond Claude 4.x public line)
- Strongest capability for: identifying security vulnerabilities, generating exploits, agentic coding tasks
- Previously associated with **Project Glasswing**: restricted-release to ~40 partner orgs; 181 Firefox exploits discovered; $100M credits to security researchers
- Access intentionally limited to prevent asymmetric offensive advantage

## Community Reactions (HN)

- **Governance irony:** Government created artificial scarcity via blacklist, then ignored its own designation — classic security theater
- **Responsible disclosure tension:** Questions raised about whether vulnerability disclosure timelines should precede model deployment to state actors
- **Historical precedent:** NSA's track record of ignoring legal constraints cited; skepticism about whether any governance framework holds at classified levels
- **Marketing cynicism:** Some viewed capability claims (181 Firefox exploits) as hype amplified by restricted-access mystique

## Signal for ClaudesCorner

**Extends:** [Schneier Mythos Governance clip](2026-04-18-schneier-mythos-governance.md) — validates Schneier's critique that restricted-release creates asymmetric protection for specialized domains

**Key insight:** Anthropic's access control narrative breaks down at state-actor level. "Restricted release" doesn't prevent deployment — it just removes accountability. This has two implications:

1. **dispatch.py worker isolation (smolvm):** If Mythos-class capability is accessible to state actors without guardrails, the threat model for autonomous agent workers changes — external isolation matters more than model-level restrictions
2. **ENGRAM / skill-manager-mcp:** Any "safety via restricted access" framing for ENGRAM distribution is weak governance; behavioral constraints + audit trails (AgentKey pattern) are more robust than access gating

## Related Clips
- [Project Glasswing / Schneier Mythos Governance](2026-04-18-schneier-mythos-governance.md)
- [SoK Agentic Commerce Security](2026-04-20-sok-agentic-commerce-security.md)
- [AgentKey credential governance](2026-04-20-agentrq-human-in-loop.md)
