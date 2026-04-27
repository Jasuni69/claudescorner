---
name: session-handoff
description: >
  Document session state after any git push so the next session starts with full context.
  Always invoke as the final step after pushing to GitHub — whether via new-project, feature, or deploy.
---

# session-handoff

Run this after every `git push`. Takes 2 minutes. Makes the next session instant.

## Steps

1. **Update `CLAUDE.md`** in the project repo — add or update a `## Session State` section:
   ```markdown
   ## Session State
   **Last updated:** YYYY-MM-DD
   **Last commit:** <hash> — <message>
   **Phase:** <what phase/stage the project is in>
   **What was done:** <2–4 bullet points of what changed this session>
   **What's next:** <the concrete next task — specific enough to act on immediately>
   **Blockers:** <anything blocking progress, or "none">
   **Open questions:** <anything awaiting client/external input, or "none">
   ```

2. **Commit and push the updated `CLAUDE.md`**:
   ```bash
   git add CLAUDE.md
   git commit -m "docs: update session state"
   git push
   ```

3. **Done.** The next session reads `CLAUDE.md` first and knows exactly where to start.

## Rules

- **NEVER ask** "should I document this?" — always do it after a push
- Keep "What's next" concrete and actionable — not "continue work" but "implement `method4_llm()` in `src/llm/client.py`"
- If there are open questions for a client, list them explicitly — they may be answered by next session
- This step is non-negotiable: no session ends after a push without updating `CLAUDE.md`

## What good looks like

```markdown
## Session State
**Last updated:** 2026-04-27
**Last commit:** 4361aa9 — init: order-to-invoice matching PoW scaffold
**Phase:** Pre-sign-off preparation
**What was done:**
- Audited full codebase — documented 4 known bugs in CLAUDE.md
- Added .gitignore, .env.example, pre-signoff-plan.md
- Created GitHub repo (private)
**What's next:** Fix `agresso_idx=-1` bug in `match.py:135` + rewrite M1/M2 loops with `pd.merge()`
**Blockers:** Need real Netset/Agresso export to confirm column names and join key
**Open questions:** Is `order_number` the shared key across both systems? (ask Advania)
```
