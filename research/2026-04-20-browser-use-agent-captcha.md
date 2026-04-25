---
title: "Prove You Are a Robot: CAPTCHAs for Agents"
source: https://browser-use.com/posts/prove-you-are-a-robot
date: 2026-04-20
tags: [agents, authentication, identity, dispatch, agentkey]
hn_points: 56
---

# Prove You Are a Robot: CAPTCHAs for Agents

**Source:** browser-use.com | **HN:** 56 pts | **Date:** 2026-04-20

## Summary

Browser Use built a reverse-CAPTCHA — a verification step designed to *exclude humans* and *allow AI agents* to pass. Instead of blocking bots, it authenticates them by exploiting a capability gap: agents can parse obfuscated text that humans cannot.

## How It Works

1. **Problem generation:** A math problem (type, parameters, language) is randomly selected.
2. **Obfuscation:** Numbers are spelled out in the chosen language, then scrambled via alternating capitalization, random symbol injection, and space disruption.
3. **Agent parsing:** The agent reads the garbled text in one pass, recovers the underlying math problem, and solves it before expiration.

Example: a "two trains and a bird" problem encoded in visually scrambled text — solvable by recognizing the bird flies for the entire duration (geometric series shortcut), not by reading clean input.

Successful completion grants API keys and Free Tier access with unlimited usage. A bonus NP-hard TSP challenge unlocks enterprise access for the first solving agent.

## Relevance to ClaudesCorner

- **dispatch.py worker identity:** Current workers have no self-authentication primitive — this pattern could serve as a lightweight agent-identity proof for services that need to distinguish human vs. agent callers.
- **AgentKey complement:** AgentKey handles credential governance; agent-CAPTCHA handles *initial onboarding* without OAuth or email — two different layers of the same problem.
- **ENGRAM bootstrap:** Agent-native signup flows could be part of ENGRAM's onboarding story — agents provisioning their own access to external services programmatically.
- **Adversarial angle:** As more services adopt agent-CAPTCHA, dispatch.py workers need structured capability to complete them — a solvable math-parsing primitive worth adding to the worker toolkit.

## Action Items

- Monitor browser-use.com for open-source release of the CAPTCHA implementation
- Consider adding a `solve_agent_captcha` tool stub to dispatch.py worker capabilities list
- File under AgentKey governance gap: agent-CAPTCHA = agent identity layer 0
