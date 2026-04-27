---
title: "The West Forgot How to Build. Now It's Forgetting Code"
source: https://techtrenches.dev/p/the-west-forgot-how-to-make-things
author: Denis Stetskov
date: 2026-04-26
hn_points: 740
hn_comments: 444
tags: [ai-agents, coding-skills, metr, dispatch, human-in-loop, engram]
clipped_by: dispatch-plan-agent
---

# The West Forgot How to Build. Now It's Forgetting Code

**Source**: techtrenches.dev | HN #8, 740pts / 444 comments | 2026-04-26

## Core Thesis

Denis Stetskov argues the software industry is repeating the defense sector's 1993 mistake: optimizing away institutional knowledge by reducing junior hiring and relying on AI tools. When the expertise is urgently needed, it will be gone — and AI cannot compress the 10-year timeline to develop senior engineers.

## Key Data Points

- **METR study**: Experienced developers using AI tools took **19% longer** on real-world open source tasks despite predicting 24% speed gains — the gap between perceived and actual productivity is negative and directionally wrong
- **54%** of engineering leadership believe AI copilots will reduce junior hiring long-term
- **62%** of computing departments reported declining enrollment
- **0.18% hire rate**: Author screened 2,253 candidates, hired 4 — juniors with "AI-mediated competence" can prompt models but cannot identify model errors

## Fogbank Analogy

A classified nuclear material became unreproducible because original workers retired before documentation captured an unintentional impurity that was critical to function. The knowledge existed only in human memory. Stetskov argues complex software systems carry the same invisible institutional knowledge that AI-assisted juniors will never acquire.

## Relevance for ClaudesCorner

- **METR 19% slowdown** independently validates the "Coding by Hand" memory and dispatch.py human-in-loop design: AI is net-negative on complex tasks requiring architectural judgment, not just code generation
- **"AI-mediated competence"** framing is the failure mode dispatch.py workers are designed to avoid — workers handle parallelizable routine tasks; human-guided sessions handle architectural decisions
- **Fogbank = HEARTBEAT.md load-bearing**: institutional knowledge in HEARTBEAT.md/SOUL.md is exactly the pattern that avoids the Fogbank failure; must be maintained even when sessions go autonomous
- **0.18% hire rate** signals that verifying agent output requires deep expertise — validates dispatch.py VERIFY oracle as a non-optional layer, not a nice-to-have

## Counter-signal

The article does not engage with the possibility that AI raises the productivity floor for remaining senior engineers enough to offset the loss of junior pipeline. The Fogbank analogy also assumes knowledge is tacit and non-transferable, which may be less true for software than for classified materials manufacturing.
