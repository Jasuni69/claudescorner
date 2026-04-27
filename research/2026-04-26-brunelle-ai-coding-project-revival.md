---
title: "AI Coding Tools for Project Revival — Brunelle Workflow Patterns"
source: https://blog.matthewbrunelle.com/its-ok-to-use-coding-assistance-tools-to-revive-the-projects-you-never-were-going-to-finish/
clipped: 2026-04-26
tags: [claude-code, workflow, context-hygiene, one-task-one-session, deskilling, dispatch-py]
signal: medium-high
hn_pts: 249
---

# It's OK to Use Coding Assistance Tools to Revive the Projects You Never Were Going to Finish

**Source:** blog.matthewbrunelle.com — HN 249 pts, April 25 2026
**Tool used:** Claude Code with Opus 4.6
**Project:** YouTube Music → OpenSubsonic shim (ytmusicapi + yt-dlp)

## Main Thesis

AI coding assistance is appropriate for "wish fulfillment" projects — things you want working but where the learning journey is not the point. Reserve manual coding for skill-development work to avoid deskilling.

## Workflow Patterns Observed

### Upfront Convention Setting
Before generating any code, the author establishes explicit conventions in the prompt:
- Type annotations throughout
- Pydantic V2 for models
- Google-style docstrings
- Specific library choices (ytmusicapi, yt-dlp)

**Relevance:** Mirrors dispatch.py worker prompt structure — conventions injected at task_plan.md header, not discovered mid-session. Upfront constraints reduce correction loops.

### Plan Mode for Iterative Refinement
Uses Claude Code's plan mode to review approach before implementation, not just for initial design but for each major sub-feature. Prevents the model from optimistically generating stubs.

### Context Clears Between Major Implementations
Explicitly clears context window between major feature implementations. Each endpoint category = fresh session.

**Validates:** dispatch.py one-task-one-session model. Context carrying over from previous implementations causes the model to assume patterns from prior code without re-examining the spec.

### Post-Change Documentation Regeneration
After significant code changes, explicitly prompts to regenerate documentation. Prevents docs from describing the pre-refactor API.

### Validation via Real Clients
Doesn't trust unit tests alone for HTTP APIs — validates by running actual client software (Subsonic apps) against the endpoint. Streaming details in particular only surface through real client testing.

**Validates:** dispatch.py VERIFY oracle principle — self-assessment by the model is unreliable; external oracle (real client, real data, real assertion) is the correct verification layer.

## Failure Modes Identified

1. **Stubbed endpoints return wrong shapes** — model generates plausible-looking stubs that pass unit tests but fail with real clients
2. **API spec ambiguity not auto-resolved** — when the spec is underspecified, model picks a guess rather than flagging it
3. **Streaming requires live testing** — chunked/streaming semantics can't be verified by static unit tests
4. **Long-tail drudgery** — 80+ endpoints require persistent iteration; AI accelerates but does not eliminate repetition

## Key Takeaway for Dispatch Architecture

> "Clear context between major implementations" + explicit upfront conventions = one-task-one-session-one-PR at personal project scale, independently arriving at dispatch.py's core design constraint.

The author's external-client-as-oracle pattern (real Subsonic apps as verifier) is the correct analogue for dispatch.py VERIFY workers — fixed external eval harness beats self-reported success every time (cf. Remoroo, bi-agent 3-layer oracle).

## Deskilling Warning

Brunelle explicitly reserves AI for projects where the learning is not the goal. Doing otherwise atrophies the deeper knowledge that makes AI leverage possible in the first place — aligns with "Coding by Hand" (miguelconner.substack.com) clipped 2026-04-18.
