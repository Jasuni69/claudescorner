---
title: "Sabotaging Projects by Overthinking, Scope Creep, and Structural Diffing"
source: https://kevinlynagh.com/newsletter/2026_04_overthinking/
author: Kevin Lynagh
date: 2026-04-26
clipped: 2026-04-26
hn_points: 515
hn_comments: 132
tags: [ai-agents, scope-creep, dispatch, claude-code, workflow, yagni]
relevance: dispatch.py worker prompts, DENY clauses, one-task-one-session model
---

# Sabotaging Projects by Overthinking, Scope Creep, and Structural Diffing

**Source:** kevinlynagh.com newsletter, Apr 2026 | 515 HN points, 132 comments

## Core Thesis

"Conservation of scope creep" law: efficiency gains from AI assistance are neutralized by a proportional increase in unnecessary features, rabbit holes, and diversions. The author empirically discovered this while building an Emacs fuzzy-search tool with LLM help — the AI found a library with anchor functionality, implemented it, and the wrapper code went straight to trash because anchoring was never actually needed.

## Key Framework

**1. Minimal success criteria before starting**
Fuzzy objectives → decision gridlock. Shelf project succeeded because goal was "make a shelf for my exact kitchen," not "replace my commercial tool." Complex AI-assisted projects fail when the question "am I trying to replace my own usage of X?" remains open.

**2. Conservation of scope creep (central law)**
> "Any increases in programming speed will be offset by a corresponding increase in unnecessary features, rabbit holes, and diversions."
AI doesn't eliminate scope creep — it accelerates it. Feature discovery outpaces feature need.

**3. Strict task scoping for AI agents**
The author's working model: give agents "scoped tasks," review output in minutes, manually revise / discard / restart. No open-ended exploration. This containment prevents agents from generating thousands of lines with tangential features.

**4. YAGNI as the only countermeasure**
Ruthless feature triage: question whether each discovered feature addresses the *original* problem. Discard aggressively. Three concrete guardrails:
- Time-box research phases (4 hours research → 4 hours implementation, hard cap)
- Ruthless feature triage on AI output
- Private-first shipping (remove external validation incentives that drive polish/expansion)

## Phased Scope Containment (structural diffing example)

Phase 1 (MVP): treesitter entity extraction + simple greedy matching + CLI output  
Phase 2 (conditional): Emacs integration, multi-language support — *only if Phase 1 satisfies actual needs*  
Phase 3 (speculative): score-based matching — never start unless Phase 2 fully consumed

## Implications for ClaudesCorner

- **dispatch.py DENY clauses** are the architectural response to conservation of scope creep: hard bounds prevent workers from discovering and implementing features outside task scope.
- **One-task-one-session-one-PR** (Affirm pattern, 2026-04-24) is independently validated here: scoped task + review + discard/restart.
- **HEARTBEAT.md task descriptions** must include explicit success criteria, not just task names — fuzzy descriptions invite scope expansion.
- **bi-agent DAX generation**: scope conservation law applies — oracle must test original requirements, not judge "completeness" of generated DAX.
- The 4-hour time-box pattern is a direct candidate for dispatch.py tier-2 worker wall-clock timeout (currently unlimited).
