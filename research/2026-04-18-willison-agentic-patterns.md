---
title: "Agentic Engineering Patterns: Adding a New Content Type"
source: https://simonwillison.net/guides/agentic-engineering-patterns/adding-a-new-content-type/
author: Simon Willison
date: 2026-04-18
clipped: 2026-04-18
tags: [agentic-engineering, claude-code, patterns, dispatch, bi-agent]
relevance: high
---

## Summary

Willison walks through directing Claude Code to extend his blog-to-newsletter tool with a new "beats" content type. Core thesis: **writing code is cheap now — the skill is directing AI systems intelligently**.

## Key Patterns

### 1. Reference Code Strategy
Clone relevant repos to `/tmp` so the agent can study structure without accidentally incorporating reference code into the output. Keeps signal clean.

### 2. Pattern Imitation over Spec
Instead of writing detailed specs, point at an existing implementation: *"similar to how the Atom everything feed works."* Agent analyzes and replicates the pattern. Less prompt, better output.

### 3. Built-in Validation in the Prompt
Include explicit test steps in the initial prompt — `python -m http.server` + browser check via Rodney (uvx). Agent self-verifies rather than stopping at "done."

## Tools Used
- **Claude Code (web)** for agentic dev
- **Rodney** — browser automation via `uvx` for self-verification
- **Datasette** — SQL-backed data layer; UNION clause extension for new content types
- **GitHub repos as reference material** — cloned to /tmp

## Relevance to ClaudesCorner

| Pattern | Apply where |
|---|---|
| Reference-code-to-tmp | dispatch.py worker prompts — point workers at existing scripts as style guides |
| Pattern imitation | bi-agent schema blocks — reference existing DAX patterns instead of exhaustive specs |
| Built-in validation | skill prompts — append `verify:` section to every skill that includes a self-check step |
| Rodney for browser verify | alignment-tax playtesting — automate end-to-end game flow checks |
