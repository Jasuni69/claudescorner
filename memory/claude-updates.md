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

## Claude Code (v2.1.80+ / late March 2026)
- **`--bare` flag** — scripted `-p` calls skip hooks, LSP, plugin sync, skill dir walks. Useful for claw/heartbeat subprocess calls that don't need full CC overhead.
- **`-n` / `--name`** — set display name for session at startup
- **`--channels` permission relay** — channel-based permission propagation between agents
- **PostCompact hook** — fires after context compaction completes. Useful for post-compaction memory flush.
- **HTTP hooks** — hooks can now POST JSON to a URL and receive JSON back. Enables external service integration without local scripts.
- **MCP Elicitation** (v2.1.76+) — MCP servers can request structured input mid-task via interactive form or browser URL. No more blocking for missing params.

## Claude Code (v2.1.81 / March 20-21)
- **`rate_limits` statusline field** — display Claude.ai rate limit usage (5h + 7d windows, `used_percentage`, `resets_at`)
- **`--channels` research preview** — MCP servers can push messages into sessions; channel servers declaring permission capability can forward tool approval prompts to phone
- **Voice mode fixes** — silent retry failure no longer swallowed; WebSocket recovery on dropped connections; modifier-combo push-to-talk (e.g. ctrl+k) fixed
- **Remote Control fix** — sessions now derive title from first prompt instead of generic title

## Claude Platform (March 2026)
- **Sonnet 4.6** launched — 1M context window beta, most capable Sonnet yet
- **Cowork** — persistent agent thread in Desktop/iOS/Android for task management (Max plans, rolling to Pro)
- **In-line visualizations** — Claude creates custom charts/diagrams in responses (Pro/Max)
- **Off-peak double limits** — March 13–27 promotion, all plans get 2x limits off-peak
- **Channels (VentureBeat)** — Claude Code Channels connect to Discord/Telegram for mobile messaging to CC sessions

## Claude Agent SDK
- **Renamed from Claude Code SDK** (late 2025) — now a general-purpose agent runtime
- Python: `v0.1.48` on PyPI | TypeScript: `v0.2.71` on npm
- Includes built-in file ops, shell, web search, MCP integration — same loop that powers CC

## Relevant to us
- Official `/loop` is similar to our taskqueue loop but simpler (interval-based monitoring vs queue-based)
- Voice mode + Swedish support could be useful for Jason
- `allowRead` sandbox setting worth investigating for tighter permission control
- **`--bare` flag** — worth using in heartbeat.ps1/claw subprocess calls to reduce overhead
- **PostCompact hook** — could trigger automatic memory flush after compaction instead of relying on Jason to call `/memory-flush`
- **HTTP hooks** — potential bridge between CC hooks and external services (Todoist webhooks, etc.)
- **Agent SDK** rename signals Anthropic positioning CC loop as a platform, not just a coding tool
- **`rate_limits` statusline** — could add to /status skill so Jason sees rate limit pressure
- **Channels** — if stable, could replace our taskqueue-mcp push model with native channel push. Worth monitoring.
- **Cowork** — Anthropic's native version of what we built with claw/agents.py + taskqueue. Compare feature set.
- **Off-peak promotion ends March 27** — after that, normal limits resume
