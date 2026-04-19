---
title: "Willison — Reference-Repo Prompting: Clone to /tmp, Imitate, Validate"
source: https://simonwillison.net/guides/agentic-engineering-patterns/adding-a-new-content-type/
date: 2026-04-19
tags: [claude-code, agents, dispatch, prompting, patterns]
---

# Reference-Repo Prompting Pattern

**Source:** simonwillison.net — Agentic Engineering Patterns series  
**Related clip:** 2026-04-18-willison-new-content-type.md (earlier entry in same series)

## The Pattern

Three-part prompt structure for delegating substantial work in one shot:

1. **Clone reference repo to `/tmp`** — gives agent schema + patterns without verbal description
2. **Imitate existing logic** — "mirror the existing feed logic" conveys intent from code, not spec
3. **Self-validate** — compare output against live server / browser automation; agent verifies its own work

## What One Prompt Accomplished

- Modified SQL queries with UNION clauses to fetch new content type
- Filtered on non-draft + has-description criteria
- Created JS enum→display-name mapping from Django model source
- ~20 lines of SQL + a JS object — "exactly the right change"

## Key Principles

- **Reference code > spec text**: Agents read source directly, inferring schema and conventions without verbose description
- **Validation oracle in prompt**: Asking agent to compare against live output = self-verification loop, reduces hallucinated success
- **Standard scaffolding**: `python -m http.server` becomes muscle memory in dispatch worker prompts — consistent, reliable, self-contained

## Relevance to ClaudesCorner

- **dispatch.py workers**: Worker prompts currently lack a `verify:` step. Adding "compare output against X" as a validation oracle would catch silent failures. Flagged in 2026-04-18 Remoroo clip too.
- **bi-agent**: Schema block as `cache_control=ephemeral` is the ClaudesCorner analog of reference-repo — it pre-loads context once and amortizes it. Same principle: code as context, not prose.
- **skill verify: sections**: Each skill's `verify:` block should embed a validation oracle, not just describe expected behavior.

## Action

Add a `verify:` clause to dispatch.py worker prompt template that asks the worker to confirm output against a known fixture or expected structure before marking complete.
