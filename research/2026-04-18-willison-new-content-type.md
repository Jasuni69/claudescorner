---
title: "Adding a new content type to my blog-to-newsletter tool"
source: https://simonwillison.net/guides/agentic-engineering-patterns/adding-a-new-content-type/
author: Simon Willison
date: 2026-04-18
clipped: 2026-04-18
tags: [claude-code, agentic-patterns, reference-code, workflow]
relevance: dispatch.py worker prompts, bi-agent schema blocks, skill verify sections
---

## Summary

Willison demonstrates a 3-prompt agentic workflow for adding a new content type ("beats") to `blog-to-newsletter.html` using Claude Code. Core technique: clone a reference repo to `/tmp` so the agent can read schema/logic without any risk of accidentally committing it.

## The 3-prompt sequence

1. `Clone simonw/simonwillisonblog to /tmp for reference`
2. `Update blog-to-newsletter.html to include beats with descriptions, mimicking the Atom feed logic`
3. `Test locally using python -m http.server and uvx rodney, compare against the blog homepage`

Output: a SQL UNION clause + JavaScript beat-type mapping object — no verbal description of the schema needed.

## Takeaways for ClaudesCorner

- **External reference over verbal spec**: pointing agents at real code beats describing it. Apply to dispatch.py worker prompts — give workers a `/tmp` clone of the target project rather than a prose description.
- **`/tmp` isolation**: reference code that must not be committed goes to `/tmp`. Same pattern usable in skill `verify:` sections to test against a known-good reference.
- **Validation baked into prompt**: `compare output to homepage` gives the agent a concrete pass/fail signal. bi-agent's schema cache_control block is analogous — embed the oracle, don't leave it implicit.
- **Pattern imitation > spec writing**: "like the Atom feed" is more precise than a paragraph of requirements.
