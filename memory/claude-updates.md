# Claude Updates — March 2026

Sourced 2026-03-19

## Claude Code (v2.1.63 → v2.1.76)
- **Voice mode** — `/voice`, push-to-talk (spacebar). 10 new languages: Russian, Polish, Turkish, Dutch, Ukrainian, Greek, Czech, Danish, Swedish, Norwegian
- **`/loop`** — official recurring monitoring command (we built ours independently before this shipped)
- **`/effort`** — set model effort level, 3 tiers, "max" level removed
- **Opus 4.6 default** — 1M context window
- **Output tokens** — default 64k, upper bound 128k
- **`allowRead` sandbox setting** — new permission control for file access

## Claude Desktop
- **Customize section** — skills, plugins, connectors grouped in one place
- **Cowork** — create/schedule recurring + on-demand tasks, Pro plan, macOS only
- **Scheduled tasks** — recurring and one-time, via Cowork interface

## Claude Code (v2.1.77 → v2.1.79)
- **`--console` flag** on `claude auth login` — authenticate via Anthropic Console (API billing)
- **Show turn duration** toggle in `/config`
- **`/remote-control`** — bridge session to claude.ai/code for browser/phone continuation
- **AI session titles** in VS Code based on first message
- **Fix:** `claude -p` hanging when spawned as subprocess without stdin (relevant to our heartbeat.ps1)
- **Fix:** voice mode not activating on startup with `voiceEnabled: true`
- **Breaking:** `CLAUDE_CODE_PLUGIN_SEED_DIR` now supports multiple dirs (`:` on Unix, `;` on Windows)

## Relevant to us
- Official `/loop` is similar to our taskqueue loop but simpler (interval-based monitoring vs queue-based)
- Voice mode + Swedish support could be useful for Jason
- `allowRead` sandbox setting worth investigating for tighter permission control
