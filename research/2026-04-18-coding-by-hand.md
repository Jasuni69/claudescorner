---
title: "I'm Coding by Hand"
source: https://miguelconner.substack.com/p/im-coding-by-hand
author: Miguel Conner
date: 2026-04-15
clipped: 2026-04-18
tags: [ai-coding, craft, skill-atrophy, deliberate-practice, agents]
hn: https://news.ycombinator.com/item?id=47807583
hn_points: 261
relevance: counter-signal to full agent delegation; validates human-in-loop for complex design decisions
---

# I'm Coding by Hand

Miguel Conner, ex-Aily Labs (built web search agents in Barcelona), deliberately codes without AI for 3 months at Recurse Center in Brooklyn. 261 HN points.

## Main thesis

Manual coding does two things simultaneously: writes the code AND ingrains the codebase. Agent delegation breaks this coupling — you get output without the mental model.

> "When writing code by hand I was actually doing two things: writing what I wanted and learning the code base."

Cites Cal Newport: cognitive strain is the equivalent of a gym workout. Eliminating it eliminates the adaptation.

## Key observations

- The best AI users at Aily Labs were also the strongest coders — deeper knowledge = more leverage over the tool
- Agent-assisted dev works if you spec requirements precisely; if you can't, you don't understand the problem well enough yet
- Rapid terminal iteration (test syntax live, no docs) is a skill that compounds; agents bypass it

## Three RC goals

1. Train an LLM from scratch — Transformer arch, Stanford CS336 assignments
2. Improve Python proficiency — no doc/AI crutch
3. Build mental models across abstraction layers

## Techniques practiced

- FizzBuzz in BASIC on 1983 Apple IIe — historical abstraction layer grounding
- Bandit wargames — Unix/terminal fluency
- Vim-only neural network coding for GPU remote sessions
- Mob programming — Clojure workshop
- Pair programming with 10yr+ Python veterans

## Progress (6 weeks in)

- Completed CS336 Assignment 1: tokenizer + GPT-2 in PyTorch
- 17M param model on Tiny Stories, hyperparameter tuning
- Assignment 2: GPU profiling, FlashAttention2 in Triton

## Relevance to ClaudesCorner

Counter-signal worth holding: dispatch.py workers + bi-agent are correct for routine/parallel work. But complex architectural decisions (SOUL.md structure, memory governance rules, new project scaffolding) benefit from Jason-in-the-loop, not full delegation. Skill crystallization (GenericAgent L0-L4) is the bridge — agent output gets human validation before promotion.

The "deeper knowledge = more leverage" observation validates the bi-agent cache_control pattern: the better the schema block, the better the DAX output.
