---
title: "Karpathy Claude Code Guidelines — 66k-star CLAUDE.md"
date: 2026-04-20
source: https://github.com/forrestchang/andrej-karpathy-skills
tags: [claude-code, CLAUDE.md, engineering-patterns, engram, soul-md]
signal: high
---

# Karpathy Claude Code Guidelines

**Repo**: forrestchang/andrej-karpathy-skills | 66,000+ stars (+45,381 this week, #1 trending all languages) | MIT | Created 2026-01-27

## What It Is

A single `CLAUDE.md` file distilling Andrej Karpathy's observations about the three most common LLM coding failure modes, codified as four actionable rules. Installable via Claude Code plugin or dropped into any project root.

## The Three Failure Modes Karpathy Identified

1. **Silent assumptions** — model fills in ambiguity without flagging it
2. **Over-abstraction** — unnecessary layers, single-use helpers, speculative features
3. **Scope creep** — modifying code outside what was explicitly requested

## The Four Rules

### 1. Think Before Coding
- State all assumptions explicitly before writing a line
- Offer multiple interpretations when the request is ambiguous
- Push back if a simpler approach exists

### 2. Simplicity First
- No speculative features, no single-use abstractions
- No unnecessary error handling
- Self-test: "Would a senior engineer call this overcomplicated?"

### 3. Surgical Changes
- Touch only what was requested
- Match existing code style exactly
- Only remove code that *your own edits* made obsolete

### 4. Goal-Driven Execution
- Convert vague instructions into measurable success criteria
- Example: "add validation" → "write tests for invalid inputs, then make them pass"

## Relevance to ClaudesCorner

| Rule | Current gap | Action |
|------|-------------|--------|
| Think Before Coding | SOUL.md doesn't enforce assumption surfacing | Add `think_before_coding: true` pattern to SOUL.md |
| Simplicity First | Dispatch.py workers sometimes scaffold over-complex responses | Add simplicity gate to worker verify: oracle |
| Surgical Changes | No scope-check in dispatch workers | Add scope constraint to worker prompt template |
| Goal-Driven | Tasks.json prompts are often vague | Rephrase dispatch tasks as measurable success criteria |

## Signal

The 45k weekly surge signals Karpathy's name + the Claude Code plugin install path made this viral. The four rules are directly applicable to `SOUL.md` instruction calibration and dispatch.py worker prompt design. This is the highest-star CLAUDE.md pattern in the wild — worth a careful diff against Jason's current global CLAUDE.md.

**One-line signal**: Karpathy's 4-rule CLAUDE.md (think→simplify→surgical→goal-driven) is the highest-signal public calibration input for SOUL.md instruction density and dispatch.py worker prompt quality.
