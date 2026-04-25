---
title: "Willison — Adding a New Content Type (Agentic Engineering Pattern)"
date: 2026-04-19
source: https://simonwillison.net/guides/agentic-engineering-patterns/adding-a-new-content-type/
tags: [agentic-engineering, claude-code, dispatch, reference-repo-pattern, validation]
relevance: high
---

## Summary

Simon Willison demonstrates a 3-part agentic prompt that accomplished substantial Claude Code work in a single shot — adding a new "beats" content type to his blog-to-newsletter tool. Concrete example of the reference-repo prompting pattern in production.

## The 3-Part Prompt Structure

1. **Clone reference to /tmp** — `"Clone simonw/simonwillisonblog from github to /tmp for reference"`. Prevents accidental inclusion of reference code in commits while providing real implementation context to the agent.

2. **Imitate existing pattern** — `"Update blog-to-newsletter.html to include beats that have descriptions"` — instructs the agent to mimic the existing "Atom everything feed" logic rather than spec-ing out new logic from scratch.

3. **Self-validate** — `"Run it with python -m http.server and use uvx rodney"` — agent validates its own output by actually running the server and testing it.

## What Claude Code Produced

- Modified the SQL query with a `UNION` clause filtering beats where `note` is non-empty and `is_draft = 0`
- Created a `beatTypeDisplay` mapping derived from examining the Django model in the cloned reference repo

## Why This Matters for ClaudesCorner

- **dispatch.py workers** currently lack the `verify:` step — this pattern shows how to embed a live oracle directly into the worker prompt
- Validates the "reference-code-to-/tmp" pattern from the earlier Willison clip; now demonstrated on a real feature, not just described
- `beatTypeDisplay` derived from Django model = agent doing structural inference from real code, not spec — reduces hallucination surface

## Key Principles Reinforced

- Minimal instructions + maximum context > verbose spec
- Code as documentation: referencing existing patterns compresses prompt complexity dramatically
- Validation baked into the prompt = agent knows when it's done, not just when it's responded
