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

## Claude Code (v2.1.92 / April 4, 2026)

- **Interactive Bedrock setup wizard** — guided AWS auth + region config from login screen
- **Per-model + cache-hit breakdown in `/cost`** — subscription users get detailed breakdown
- **`/release-notes`** — now an interactive version picker
- **Remote Control session names** — use hostname as default prefix (e.g. `myhost-graceful-unicorn`), overridable with `--remote-control-session-name-prefix`
- **`forceRemoteSettingsRefresh`** policy — blocks startup until managed settings are freshly fetched; fail-closed
- **Fix:** subagent spawning permanently failing after tmux windows killed/renumbered
- **Fix:** prompt-type Stop hooks failing when small model returns `ok:false`
- **Removed:** `/tag` and `/vim` commands (vim mode now via `/config → Editor mode`)

## Claude Code (v2.1.94 / April 7, 2026)

- **Amazon Bedrock + Mantle support** — `CLAUDE_CODE_USE_MANTLE=1`
- **Default effort changed to `high`** for API-key, Bedrock/Vertex, Team, Enterprise users
- **`hookSpecificOutput.sessionTitle`** in UserPromptSubmit hooks — set session title from hook
- **`keep-coding-instructions`** frontmatter field for plugin output styles
- **Fix:** agents stuck after 429 with long Retry-After — now surfaces immediately
- **Fix:** Console login on macOS silently failing when login keychain locked

## Claude Code (v2.1.97-v2.1.98 / April 8-9, 2026)

- **Focus view toggle** (`Ctrl+O`) in NO_FLICKER mode — shows prompt, tool summary, final response
- **`refreshInterval`** status line setting — re-run status line command every N seconds
- **`workspace.git_worktree`** in status line JSON — set when inside a linked git worktree
- **Monitor tool** — streaming events from background scripts (new tool)
- **`CLAUDE_CODE_PERFORCE_MODE`** — Edit/Write fail on read-only files with `p4 edit` hint
- **Subprocess sandboxing** with PID namespace isolation on Linux (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`)
- **`--exclude-dynamic-system-prompt-sections`** flag for print mode — better cross-user prompt caching
- **Fix:** Bash tool permission bypass via backslash-escaped flags — security fix
- **Fix:** compound Bash commands bypassing forced permission prompts — security fix
- **Fix:** redirects to `/dev/tcp/...` or `/dev/udp/...` not prompting
- **Fix:** 429 retries burning all attempts in ~13s — exponential backoff now applies as minimum
- **Fix:** hardcoded 5-minute request timeout removed — now honors `API_TIMEOUT_MS`
- **Improved `/agents`** — tabbed layout: Running tab + Library tab with Run/View actions

## Claude Code (v2.1.101 / April 10, 2026)

- **`/team-onboarding`** — generates teammate ramp-up guide from local CC usage
- **OS CA certificate store trust by default** — enterprise TLS proxies work without extra setup; `CLAUDE_CODE_CERT_STORE=bundled` to revert
- **`/ultraplan`** and remote-session features auto-create default cloud environment
- **`claude -p --resume <name>`** now accepts session titles set via `/rename` or `--name`
- **Fix:** unrecognized hook event name in settings.json no longer ignores entire file
- **Fix:** command injection vulnerability in POSIX `which` fallback used by LSP binary detection — **security fix**
- **Fix:** memory leak retaining dozens of historical message list copies in virtual scroller
- **Fix:** `--resume` chain recovery bridging into unrelated subagent conversation
- **Fix:** subagents not inheriting MCP tools from dynamically-injected servers
- **Fix:** sandboxed Bash failing with `mktemp: No such file or directory` after fresh boot

## Claude Code (v2.1.105 / April 13, 2026)

- **`path` parameter for `EnterWorktree`** — switch into an existing worktree directly
- **`PreCompact` hook** — hooks can block compaction by exiting code 2 or returning `{"decision":"block"}`
- **Background monitor support for plugins** — `monitors` manifest key in plugins, auto-arms at session start or skill invoke
- **`/proactive`** is now an alias for `/loop`
- **Fix:** stalled API streams now abort after 5 minutes and retry non-streaming
- **Fix:** `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` in one project no longer disabling metrics for all projects
- **Fix:** one-shot scheduled tasks re-firing repeatedly when file watcher missed post-fire cleanup
- **Fix:** MCP tools missing on first turn of headless/remote-trigger sessions when MCP servers connect asynchronously
- **Fix:** stdio MCP server emitting malformed output hanging session instead of failing fast
- **Fix:** garbled bash output when commands print clickable file links (Python rich/loguru)
- **Improved `/doctor`** — status icons; press `f` to have Claude fix reported issues
- **Improved skill description handling** — listing cap raised from 250 to 1,536 characters
- **Improved WebFetch** — strips `<style>` and `<script>` contents so CSS-heavy pages don't exhaust content budget

## Claude Code (v2.1.107 / April 14, 2026)

- **Show thinking hints sooner** during long operations

## Claude Platform — April 2026 (sourced 2026-04-14)

### April 9
- **Advisor Tool** (public beta) — pair a fast executor model with a high-intelligence advisor model that provides strategic guidance mid-generation. Include beta header `advisor-tool-2026-03-01`. Key for: long-horizon agentic tasks that need Opus-quality reasoning at Sonnet-level token cost.

### April 8
- **Claude Managed Agents** (public beta) — fully managed agent harness: secure sandboxing, built-in tools, SSE streaming. Create agents, configure containers, run sessions via API. Requires beta header `managed-agents-2026-04-01`.
- **`ant` CLI** — command-line client for the Claude API. Native integration with Claude Code. Versions API resources as YAML files. Faster API interaction than raw curl.

### April 7
- **Claude Mythos Preview** — now confirmed as a defensive cybersecurity research preview (not just leaked). Gated, invite-only. Part of Project Glasswing (multi-company security initiative with AWS, Apple, Broadcom, Cisco).
- **Messages API on Amazon Bedrock** (research preview) — same request shape as 1P Claude API, AWS-managed infra, `us-east-1` only. Contact AE to request access.

## Relevant to us (new)
- **`refreshInterval` status line** — could make `/status` skill auto-refresh without manual invocation
- **Monitor tool** — useful for streaming heartbeat/background script output into session
- **`PreCompact` hook** — can block compaction mid-task if needed; complements existing PostCompact flush
- **`/proactive` alias for `/loop`** — nice ergonomic alias
- **OS CA cert trust by default** — resolves enterprise TLS proxy issues on Numberskills-Internal network
- **Effort default now `high`** — may increase token usage; worth monitoring on rate-limited sessions
- **Security fixes in v2.1.98/2.1.101** — Bash permission bypasses and command injection fixed; update ASAP if not already on latest
- **`CLAUDE_CODE_PERFORCE_MODE`** — not relevant (no Perforce), but signals Anthropic supporting more enterprise VCS patterns
- **Advisor Tool** — could significantly improve quality of our bi-agent / fabric-mcp tool calls if executor=Sonnet, advisor=Opus. Worth testing when it's less restricted.
- **Managed Agents** — Anthropic's managed version of what claw/agents.py does locally. Compare when access is easier.
- **`ant` CLI** — YAML-versioned API resources could be useful for managing our ClaudesCorner tool configs. Monitor GA status.
- **Mythos confirmed as cybersecurity-focused preview** — not a general next model release
