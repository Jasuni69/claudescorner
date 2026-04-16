---
title: "Anthropic Project Glasswing — Claude Mythos Restricted Security Access"
date: 2026-04-16
source: https://simonwillison.net/2026/Apr/7/project-glasswing/
tags: [anthropic, security, claude-mythos, exploit-development, ai-safety]
relevance: high
---

## Summary

Anthropic launched **Project Glasswing** — a restricted access program for **Claude Mythos**, a model with exceptional autonomous vulnerability discovery and exploit development capabilities. Access is limited to vetted security research partners; no public release planned.

## Key Facts

- Mythos significantly outperforms Opus 4.6 at autonomous exploit development
- Opus 4.6: ~0% success creating JavaScript exploits for Firefox vulnerabilities
- Mythos: **181 successful exploits** in equivalent testing
- Can chain multiple vulnerabilities: JIT heap spray, sandbox escapes, privilege escalation, multi-packet ROP chains

## Real-World Discoveries Already

- Thousands of high-severity CVEs across major OSes and browsers
- 27-year-old OpenBSD TCP SACK bug causing kernel crashes
- Linux privilege escalation requiring zero initial permissions

## Access Model

- Partners: AWS, Apple, Microsoft, Google, Linux Foundation
- Anthropic providing $100M in usage credits + $4M to open-source security orgs
- Goal: give industry time to patch before broader LLM capability proliferation

## Why This Matters for Jason

- **Mythos is the model behind the "cybersecurity is proof of work" thesis** — this is the capability inflection that makes that true
- Glasswing partners include Microsoft — potential Fabric/Azure security tooling implications
- Token-budget exploit discovery (from earlier clips) now has a named capability source
- The restricted access model is a template for how Anthropic plans to roll out future dangerous capabilities
