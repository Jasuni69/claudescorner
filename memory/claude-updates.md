# Claude Updates — March/April 2026

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

## Claude Code (late March 2026 additions)
- **Computer use in CC + Cowork** (Pro/Max) — Claude can now open files, run dev tools, point/click/navigate the screen. No setup. Added March 23.
- **PowerShell tool for Windows** — opt-in preview. Relevant for our Windows environment.
- **`worktree.sparsePaths`** — `claude --worktree` in monorepos can check out only needed dirs via git sparse-checkout.
- **Scroll perf fix** — replaced WASM yoga-layout with TypeScript, reduced stutter on large sessions.
- **MCP Elicitation** — already noted above, confirmed shipped.

## Claude Mythos (leaked, ~March 26)
- Anthropic testing a new model internally called "Claude Mythos" — leaked via data incident
- Described as "step change" in capabilities, "most capable we've built to date"
- In early access with select customers
- No public release date. Not Claude 5 (different naming pattern).
- Source: Fortune, SiliconANGLE (2026-03-26/27)

## Claude Code v2.1.89 (April 1, 2026)

- **`defer` permission in PreToolUse hooks** — headless sessions can pause at tool call, resume with `-p --resume` to re-evaluate
- **`CLAUDE_CODE_NO_FLICKER=1`** — flicker-free alt-screen rendering with virtualized scrollback
- **PermissionDenied hook** — fires after auto-mode classifier denials; return `{retry: true}` to let model retry
- **Named subagents** in @ mention typeahead
- **`MCP_CONNECTION_NONBLOCKING=true`** for `-p` mode — skip MCP connection wait entirely; max 5s per server (no more blocking on slow servers)
- **Fix:** collapsed tool summary shows "Listed N directories" for ls/tree/du

## Claude API (April 2026)

- **Breaking: `claude-3-haiku-20240307` deprecated** — retirement April 19, 2026
- **Breaking: Sonnet 3.7 + Haiku 3.5 retired** — requests now return error; migrate to Sonnet 4.6 / Haiku 4.5
- **Breaking: 1M context beta retired April 30** — `context-1m-2025-08-07` header will have no effect; requests >200k will error. Sonnet 4.6 + Opus 4.6 support 1M natively without beta header
- **`output_format` moved** — now `output_config.format` for structured outputs
- **Models API** — `GET` endpoints now return `max_input_tokens`, `max_tokens`, `capabilities` object
- **Elevated timeouts March 31–April 1** — Opus 4.6 + Sonnet 4.6 affected; resolved

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
- **`MCP_CONNECTION_NONBLOCKING=true`** — worth setting in heartbeat.ps1 to speed up `-p` spawns
- **`defer` PreToolUse hook** — interesting for headless runs that hit permission walls
- **PermissionDenied hook** — could auto-retry certain blocked tool calls in claw
- **API: 1M beta header retires April 30** — no action needed (we're on Sonnet 4.6 which has it natively)
- **API: Haiku 3 retires April 19** — check if any scripts hardcode that model ID
