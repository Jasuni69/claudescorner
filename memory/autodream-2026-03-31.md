# AutoDream Consolidation — 2026-03-31

## Files Scanned
19 files in memory/: daily logs (2026-03-12 through 2026-03-31), plus claude-updates.md, dax-notes.md, fabric-news.md, loop-test.md, openclaw-study.md, reddit-brief.md, reddit-feed-notes.md, research-notes.md, x-brief.md

---

## Stale / Superseded Entries

### loop-test.md (DELETE)
- Content: single line "Loop mechanic confirmed working 2026-03-19"
- Superseded by: loop infrastructure is live and well-documented in MEMORY.md
- Action: safe to delete

### reddit-brief.md (ARCHIVE — keep, low priority)
- Content: 2026-03-18 Reddit snapshot in raw format (title + URL)
- Superseded by: reddit-feed-notes.md which has structured notes with analysis
- Action: keep for historical reference, but reddit-brief.py output is no longer the primary format

### openclaw-study.md
- Content: detailed notes on OpenClaw framework from 2026-03-18
- Status: still relevant — OpenClaw patterns inform ClaudesCorner architecture
- Keep as-is

---

## Duplicate / Overlapping Information

### Chrome-in-Chrome patch location
- MEMORY.md had stale path (`Desktop\claude-ext-patched\`) — **fixed this session** to `~/claude-in-chrome-patched`
- SOUL.md references not checked (assumed correct via SOUL.md update this session)

### OAuth token expiry pattern
- Mentioned in: MEMORY.md, HEARTBEAT.md, 2026-03-18 log, 2026-03-31 log
- Not duplicate — each is a different instance/context
- **Current status**: expired again as of 2026-03-18 scheduled run. Needs `claude auth login`.

---

## Gaps — Things That Happened But Weren't Fully Captured

### 1. Clementine v4 scrapped
- `Silver_Gold_ExecutionBook_v4.py` (BatchDims approach) was attempted and scrapped
- MEMORY.md only mentions v3. Should note v4 was tried and abandoned.
- Added to MEMORY.md below.

### 2. patch-claude-in-chrome.py is now the canonical patch tool
- Captured in MEMORY.md and HEARTBEAT this session. No gap.

### 3. Autonomy research synthesis
- Done this session — written to research-notes.md (2026-03-31 section)
- Priority actions identified: stop hook, AutoDream task, typed routing, Telegram bridge

### 4. MOOD.md
- No entry written today. mood_log idle task should handle this.

---

## New Durable Facts for MEMORY.md

1. `Silver_Gold_ExecutionBook_v4.py` (BatchDims) was built and scrapped — no perf benefit over v3. v3 (merged Silver+Gold DAG, concurrency 16) remains production approach.
2. `scripts/patch-claude-in-chrome.py` is the canonical tool for re-patching Claude-in-Chrome after extension updates.
3. Scheduled heartbeat (ClaudeHeartbeat task) has been failing with 401 since 2026-03-18 due to expired OAuth token. Requires `claude auth login` to fix.

---

## Summary
- 1 file safe to delete: `loop-test.md`
- 1 file to monitor for staleness: `reddit-brief.md` (old format)
- 3 new facts captured in MEMORY.md
- Memory files otherwise healthy, no major gaps
