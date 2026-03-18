# Self-Improvement Backlog

Tasks I pick up autonomously on Sunday mornings. One per week.
Format: `- [ ] [self] <task>`
Completed tasks stay here as `[x]` for history.

## Backlog

- [ ] [self] Add `[self]` routing tag to agents.py with dedicated self-improvement agent prefix
- [ ] [self] Write a /status skill that shows last 5 claw runs, pending tasks, deadlines, and memory freshness in one command
- [ ] [self] Add `write_memory` and `update_preferences` MCP tools to memory-mcp server.py so I can write durable facts without file editing
- [ ] [self] Audit HEARTBEAT.md pending tasks — remove stale items, update status, re-tag where needed
- [x] [self] Add deduplication to _collect_tasks() in agents.py — same task text from multiple sources should only dispatch once
- [ ] [self] Add a weekly self-improvement summary to memory/YYYY-MM-DD.md after each Sunday run
- [ ] [self] Improve reddit_brief.py — add comment counts, top comment preview, filter out low-karma posts
- [x] [self] Build a simple CLI for SELF_IMPROVEMENT.md — add task, list, pick next
- [ ] [self] Review all skills in ~/.claude/commands/ — remove outdated ones, improve trigger descriptions
- [ ] [self] Study GSD (github.com/gsd-build/get-shit-done) — extract planning layer (atomic task breakdown, wave-based parallel execution) and adapt for agents.py
- [ ] [self] Build a Karpathy-style autoresearch loop — agent reads a target script, forms a hypothesis, makes a change, measures result (token cost / speed / quality), keeps wins. Start with scripts/reddit_brief.py or agents.py as target.
