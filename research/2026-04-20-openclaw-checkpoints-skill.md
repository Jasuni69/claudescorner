# Adding a checkpoints skill changed my perspective on OpenClaw

**Source:** https://old.reddit.com/r/openclaw/comments/1sq0f72/adding_this_skill_changed_my_perspective_on/
**Date clipped:** 2026-04-20
**Tags:** #skill #agent-reliability #workflow

## Summary

Community discussion about a "checkpoints" skill for OpenClaw agents that dramatically improves reliability on long workflows. Key pattern: force the agent to write a full actionable plan + checkpoint markdown file before execution, citing sources/code as anti-hallucination anchors.

## Key insights

- **Checkpoints skill**: creates a full actionable plan following a predetermined formula, writes to a markdown file with checkboxes. Cites sources/docs/code snippets as anti-hallucination technique.
- Works even with smaller local models (Gemini 4 completing 3h workflows)
- **AGENTS.md pattern** (comment by torrso): planning session first → write implementation roadmap in TODO with checkboxes → definition of done: tests + lint pass + changelog entry. Agent reads AGENTS.md each restart.
- Pre-planning session separates concerns: planning Claude vs executing Claude

## Relevance to ClaudesCorner

- Directly validates dispatch.py checkpoint/verify pattern
- AGENTS.md concept = HEARTBEAT.md analog for sub-agents
- Anti-hallucination via source-citation = verify oracle pattern
