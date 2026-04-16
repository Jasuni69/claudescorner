---
title: "RIP Pull Requests (2005–2026) — AI Shifts Code Review Paradigm"
date: 2026-04-16
source: https://www.latent.space/p/ainews-rip-pull-requests-2005-2026
tags: [agents, workflow, git, code-review, agentic-development]
relevance: medium
---

# RIP Pull Requests (2005–2026)

## The Claim

GitHub now allows developers to disable pull requests on open-source repos — first time in 21 years. Latent.space argues this marks the functional death of the PR as a collaboration primitive.

## What's Replacing PRs

- **Prompt Requests** (advocated by Pete Steinberger, Theo): review the prompt that generated the code, not the code itself
- **Reputation-based merge systems** (Mitchell Hashimoto, Amp Code): trust signals replace code review for agent-generated patches
- **Agent-native workflows**: agents operating in sandboxed environments with durable execution — humans removed from the diff-review bottleneck

## The Provocation

> "If Code Reviews are dead, and Pull Reviews are dead… how long until Git itself is dead?"

Git was designed for human collaboration. If the loop is agent → sandbox → deploy, git branches may become implementation details rather than collaboration tools.

## Relevance to Jason's Work

- Claude Code already bypasses the PR model for solo/autonomous work — this is the mainstream catching up
- The "prompt as the artifact" framing aligns with how ClaudesCorner operates: skills and prompts are the real source of truth
- For Clementine/enterprise work: governance question shifts from "who approved this PR" to "what prompt generated this and under what policy"
- Connects to Agent Armor clip (same date): governance runtime is the answer to "who approved this" in a post-PR world