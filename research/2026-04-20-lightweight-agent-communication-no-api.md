---
title: "Lightweight Agent Communication Without API Costs"
source: https://juanpabloaj.com/2026/04/16/a-lightweight-way-to-make-agents-talk-without-paying-for-api-usage/
hn: https://news.ycombinator.com/item?id=lightweight-agent-comms
date: 2026-04-20
tags: [agents, multi-agent, cli, dispatch, cost-optimization]
stars: n/a
hn_points: 28
---

## Summary

CLI resume-mode pattern lets multiple agents (Claude, Codex, Gemini) critique each other's outputs using existing subscriptions, avoiding API costs entirely. Uses `codex exec resume --last "prompt"` and `gemini -r latest -p "prompt"` to continue prior sessions rather than spawning fresh API calls.

## Architecture

1. Agent A produces initial output (draft/code/spec)
2. Agent B critiques via `resume` command — reads prior session context, no new token billing
3. Orchestrating agent reads feedback, decides next step
4. Iterate until satisfied

Two variants:
- **Non-interactive**: simple CLI resumption, minimal deps
- **tmux variant**: separate panes per agent, socket-based session sharing, full visibility into cross-agent dialogue

Memory files on GitHub document inter-agent conventions — shared state without a database.

## Relevance to ClaudesCorner

- **dispatch.py alternative**: current parallel workers each spawn full API calls; for cross-agent review loops (e.g. plan→critique→revise), resume-mode could cut costs to zero using subscription credits
- **Cost floor**: sweet spot is review/critique tasks where a second opinion is wanted but doesn't justify a full API round-trip
- **Limitation flagged by author**: "when they start talking to each other, they can produce a lot of it" — polished hallucination risk; no verify oracle in the loop; aligns with the verify: gap already identified in dispatch.py workers
- **tmux pattern** is the visibility layer missing from current dispatch.py worker outputs — each worker is a black box; tmux panes = real-time audit

## Action

- Consider resume-mode as a zero-cost critique layer in dispatch.py for plan→review subtasks
- tmux socket pattern worth extracting for dispatch.py worker visibility (complement to dispatch logs)
- Embed a verify oracle before accepting cross-agent consensus — the hallucination risk is real
