---
title: "Mozilla Firefox 150: Claude Mythos Preview Finds 271 Vulnerabilities — Defenders Can Win"
date: 2026-04-22
source: https://blog.mozilla.org/en/privacy-security/ai-security-zero-day-vulnerabilities/
via: https://simonwillison.net/2026/Apr/22/bobby-holley/
tags: [ai-security, anthropic, claude-mythos, firefox, vulnerability-research, defensive-ai]
relevance: [dispatch.py worker isolation, smolvm sandbox, kpi-monitor, ENGRAM security posture]
---

# Mozilla Firefox 150: Claude Mythos Preview Finds 271 Vulnerabilities

**Source:** Bobby Holley (CTO, Firefox) — Mozilla Security Blog, 2026-04-21  
**Via:** Simon Willison, 2026-04-22  
**HN:** Not yet indexed at clip time

## Headline Finding

Firefox 150 shipped fixes for **271 vulnerabilities** discovered via AI-assisted security analysis using an early version of **Claude Mythos Preview** in collaboration with Anthropic. This follows an earlier run using Opus 4.6 that found 22 security-sensitive bugs in Firefox 148 — a **12× increase** in a single model generation.

## The "Defenders Can Win" Thesis

Holley's core argument: historically, security has been "offensively dominant" — attackers need only one exploitable vuln while defenders must patch everything. AI disrupts this asymmetry by making exhaustive vulnerability discovery cheap, eroding attackers' structural advantage.

> "Defenders finally have a chance to win, decisively."

Key qualifier: "We also haven't seen any bugs that couldn't have been found by an elite human researcher" — AI augments, not replaces, skilled security work.

## Process & Timeline

- Mozilla + Anthropic collaboration began ~February 2026
- Team worked "around the clock" applying frontier AI models to Firefox source
- Two confirmed rounds: Opus 4.6 → Firefox 148 (22 bugs), Mythos Preview → Firefox 150 (271 bugs)
- Comprehensive remediation completed before public release

## Relevance to ClaudesCorner

| Angle | Implication |
|-------|-------------|
| **smolvm / dispatch.py isolation** | 271 vulns found in major OSS browser validates that frontier models now find real bugs at scale — worker sandboxing is not paranoia |
| **kpi-monitor** | Confidence calibration: AI security tools produce high true-positive rates when scoped correctly (Firefox → narrow domain) |
| **dispatch.py worker prompts** | Scoped, well-defined targets (Firefox codebase) outperform open-ended scanning — narrow task sizing validated again |
| **ENGRAM security posture** | Complement to earlier Schneier/Mythos clip (governance/access) — this is the quantified offensive capability that justifies the governance debate |

## Signal Gradient vs Earlier Clips

- **2026-04-18 Schneier/Mythos clip**: DoD blacklist + governance critique, no patch numbers
- **2026-04-16 Glasswing clip**: Restricted release of Mythos, 181 Firefox exploits (different metric — exploits vs vulnerabilities)
- **This clip**: Concrete patch count (271), explicit defender-win framing, Mozilla as named partner, timeline confirmed

## Key Quote

> "Defenders finally have a chance to win, decisively." — Bobby Holley, CTO Firefox, April 2026
