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

## Relevant to us
- Official `/loop` is similar to our taskqueue loop but simpler (interval-based monitoring vs queue-based)
- Voice mode + Swedish support could be useful for Jason
- `allowRead` sandbox setting worth investigating for tighter permission control
