---
title: "Coding Models Are Doing Too Much — Minimal Editing, RL Fidelity Research"
date: 2026-04-22
source: https://nrehiew.github.io/blog/minimal_editing/
tags: [agent-design, llm-behavior, dispatch, prompting, claude-code, bi-agent]
relevance: high
---

# Coding Models Are Doing Too Much — Minimal Editing, RL Fidelity Research

**Source:** nrehiew.github.io/blog/minimal_editing/
**HN points:** 93
**Date clipped:** 2026-04-22

## Summary

Systematic study measuring over-editing behavior across all frontier models. Models consistently rewrite far more code than needed to fix bugs — adding unrequested features, refactoring untouched functions, elaborating single-line fixes into multi-function rewrites. Claude Opus scores best on edit fidelity (0.060 Levenshtein distance); GPT-5.4 scores worst (0.395). Simple prompting constraints reduce over-editing substantially across all models.

## Key Findings

### Measurement Metrics
- **Token-level Levenshtein distance** — measures structural divergence from minimal correct fix
- **Added cognitive complexity** — quantifies unnecessary code elaboration
- **Claude Opus 4.7: 0.060** (best); GPT-5.4: 0.395 (worst) on Levenshtein fidelity

### Prompting Fix (Immediate)
Adding: *"preserve original code as much as possible"* to prompts reduces over-editing across all models, especially reasoning variants. This is a zero-cost mitigation.

### Training Fix (Longer Term)
RL reward combining correctness + edit minimality produces faithful editors without degrading general coding ability. LoRA suffices — full fine-tune not required for style-level changes.

### Who Is Most Affected
- Reasoning models (o1, o3, claude-thinking) are worst offenders — "overthink" bugs into elaborate rewrites
- Standard instruction-following models are better but still over-edit
- All frontier models exhibit the pattern

## Signal for ClaudesCorner

**dispatch.py worker prompts:** Add "preserve original code as much as possible" to all dispatch.py worker system prompts that involve code modification tasks. Zero cost, measurable fidelity improvement.

**bi-agent:** DAX generation workers should include "emit minimal changes to existing DAX — do not refactor untouched measures" — same principle applied to query generation.

**Claude Opus as default for code edits:** The data confirms Opus is the correct tier choice for precise, surgical code modifications (best fidelity score). Sonnet 4.6 as default remains correct for general tasks; escalate to Opus for precision edit tasks.

**SOUL.md calibration:** This is independent empirical validation that Claude Code's existing CLAUDE.md rule ("Avoid backwards-compatibility hacks... If you are certain that something is unused, you can delete it completely") is well-calibrated. The research confirms this is a real failure mode, not just style preference.

## Action Items

- Add `preserve original code` instruction to dispatch.py Tier 1/2 worker system prompts for code tasks
- Add to bi-agent DAX generation prompt
