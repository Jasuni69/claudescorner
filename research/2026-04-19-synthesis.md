# Research Synthesis — 2026-04-19

## Digest Run 1

**Sources processed:** 2  
**Files:** `2026-04-19-claude-token-inflation-4-7-vs-4-6.md`, `2026-04-19-willison-reference-repo-prompting.md`

---

### Claude Opus 4.7 Token Inflation — HN 381pts

**Signal strength:** High — corroborates 2026-04-17 clip with more data  
**Key numbers:**
- Input tokens +30–45% (tokenizer change)
- Output tokens down (fewer per task)
- Reasoning cost nearly halved
- Net: ~11% cheaper on one benchmark, but 3–5× higher in practice for context-heavy workloads
- Users hitting 5-hour Pro caps in ~2 hours

**ClaudesCorner impact:**
- dispatch.py: `--bare` flag already exists for self-contained workers — use it aggressively on 4.7
- bi-agent: `cache_control=ephemeral` on schema already in place — correct mitigation
- Session startup (SOUL.md + HEARTBEAT.md reads): startup cost rises significantly on 4.7
- **Hold on 4.7 upgrade confirmed** until workload profiling done

---

### Willison — Reference-Repo Prompting (Part 2)

**Signal strength:** High — directly actionable in dispatch.py  
**Pattern:** Clone ref to /tmp → imitate existing code → self-validate against oracle  
**Key principle:** Reference code > spec text; validation oracle in prompt catches silent failures

**ClaudesCorner impact:**
- dispatch.py workers: Missing `verify:` step — workers can report success without checking output
- Remoroo (2026-04-18) + Willison (2026-04-18) + now this: 3 independent sources pointing at same gap
- bi-agent: schema as ephemeral context block = same principle already applied
- Skills: `verify:` sections should embed assertion, not just description

---

## Digest Run 2

**Sources processed:** 2  
**Files:** `2026-04-19-finrl-trading-ai-native-quant.md`, `2026-04-19-willison-opus-system-prompt-changes.md`

---

### FinRL-Trading (FinRL-X) — 3k stars, AI-Native Quant Infrastructure

**Signal strength:** Medium-High — architectural reference for Fairford execution loop  
**Key facts:**
- 4-layer pipeline: stock selection (ML) → portfolio allocation (DRL/classical) → timing (regime) → risk overlay
- Backtest Jan 2018–Oct 2025: Sharpe 1.10 vs QQQ 0.81; paper trading Oct 2025–Mar 2026: +19.76%, Sharpe 1.96
- Weight-centric interface: MCP-compatible — agent outputs weight vector, plugs directly into Alpaca execution
- No built-in LLM layer yet — integration opportunity

**ClaudesCorner impact:**
- Fairford PoC Phase 2: Fabric as data backbone → FinRL-X as strategy layer → Alpaca execution = full signal→execution stack without rebuilding strategy engine
- Action: Wrap `allocate_portfolio(tickers, signals)` → weight vector → Alpaca as MCP tool
- bi-agent extension path: NL→DAX→portfolio signals if Fabric data piped in
- vs ai-hedge-fund (55k stars): FinRL-X wins on production backtesting + live execution; ai-hedge-fund wins on agent persona richness

---

### Willison — Claude 4.6→4.7 System Prompt Diff

**Signal strength:** High — directly informs 4.7 upgrade decision + dispatch.py design  
**Key changes in 4.7:**
- `tool_search` now baked into base behavior: Claude checks deferred tools before claiming capability gap — ClaudesCorner ToolSearch pattern is now the model's default posture
- `<acting_vs_clarifying>`: new section pushes "attempt now, not interviewed first" — aligns with CLAUDE.md no-confirmation rule
- Verbosity reduction: concise by default, filler phrases ("genuinely", "honestly", asterisk actions) removed
- Child safety hardening: critical new section + conversation-level caution after refusal
- Knowledge cutoff update: Jan 2026 (Trump-related sections removed)

**ClaudesCorner impact:**
- dispatch.py: 4.7 tighter base output = less post-processing noise in worker responses; fewer hedge tokens
- Deferred-tool pattern is now model-native — stop working around it, lean into it
- "Act first" default: less need to fight model inertia on ambiguous prompts in agentic chains
- Verbosity reduction + cache_control=ephemeral = lower effective token cost at agent output layer (partially offsets token inflation on input)

---

## Digest Run 3 (Reddit signals — 2026-04-19 05:00 brief)

**Sources:** reddit-brief.md headlines (direct fetch blocked)

**r/claudexplorers:**
- "Sonnet 4.6 is Falling Off" — community perception of Sonnet degradation; title implies recent quality drop. No body accessible. Monitor: if Sonnet 4.6 is regressing AND 4.7 is regressing on agentic tasks, there may be no good current model for dispatch workers. Hold on model decisions.
- "Caught Opus 4.7 talking to its summarizer in its CoT" — observable CoT behavior: 4.7 appears to have internal summarizer architecture that surfaces in extended thinking output. Suggests context compression mid-reasoning. Implication for dispatch: if workers use extended thinking, summarizer may truncate task state silently.
- "Finally joined the 5.2 vibe club on Opus 4.7" — extended thinking producing 5.2k+ token reasoning chains; community excited about deep CoT output.

**r/ClaudeAI:**
- Official Anthropic hackathon: "Built with Opus 4.7" — confirms 4.7 is production-pushed. Hackathon outputs will be a useful signal corpus in ~1 week.
- "Opus 4.7 thought Claude Design might be a prompt injection attack" — 4.7 has more aggressive prompt injection detection; may flag legitimate tool descriptions as threats in certain contexts. Relevant for dispatch.py worker prompts if they embed tool schemas inline.

**r/MicrosoftFabric:**
- "Passed DP-700 Today" thread active — monitor for exam tips; Jason's cert prep relevant.
- "Talk to your data" thread still active — no new signals vs yesterday.

---

## Digest Run 4

**Sources processed:** 2  
**Files:** `2026-04-19-agentrq-mcp-human-in-loop.md`, `2026-04-19-claude-design-code-native-shift.md`

---

### AgentRQ — MCP-Native Human-in-Loop Escalation (HN: 1pt, very new)

**Signal strength:** Medium-High — direct dispatch.py upgrade path  
**What it is:** Bidirectional agent↔human task layer over MCP notifications. 4 tools: createTask, reply, updateTaskStatus, getWorkspace. Apache-2.0, self-hostable, 60s Claude Code setup.

**Key pattern:** Worker hits uncertainty → `createTask` with full context → human replies async → worker resumes. Replaces fire-and-forget dead-ends in headless dispatch runs. Observable task board across all parallel workers — currently gap filled only by `logs/dispatch-*.txt`.

**ClaudesCorner impact:**
- dispatch.py: structured escalation channel for blocked workers vs current silence
- `/status` skill: `getWorkspace` natural fit to show blocked tasks alongside HEARTBEAT state
- Zero new auth surface: self-hostable + MCP-native
- Worth evaluating if Fairford Phase 2 workers need human approval gates (DAX generation before execution)

---

### Claude Design — Code-Native Design Paradigm (HN: 246pts, 161 comments)

**Signal strength:** Medium — validates existing stance, reinforces design-tooling direction  
**Core thesis:** LLMs trained on code not Figma format → Figma locked out of LLM training → code-native tools win in agentic era. Claude Design→Claude Code = zero handoff friction.

**ClaudesCorner impact:**
- Validates reference_claude_design.md hold decision
- Fairford / ENGRAM UI: prototype directly in Claude Code, not Figma-first
- Existing handoff bundle pattern (designer→structured instruction→Claude Code) remains correct bridge for team work
- Figma investment still not worth it — 246pt community resonance, not just author opinion

---

## Digest Run 5

**Sources processed:** 2  
**Files:** `2026-04-19-opencode-open-source-coding-agent.md`, `2026-04-19-openspec-spec-driven-development.md`

---

### OpenCode — Open-Source Coding Agent (145.6k stars, +525 today)

**Signal strength:** Medium — structural reference for dispatch.py agent architecture  
**What it is:** Provider-agnostic terminal coding agent (TypeScript). Plan agent (read-only) + Build agent (full access) split. MCP Registry integration. LSP support out-of-the-box.

**Key differentiators vs Claude Code:**
- Plan/Build agent split = formalized version of dispatch.py worker role separation
- LSP integration = language server quality signals on code edits (gap in current workers)
- Open codebase = extractable agent tool-use patterns
- MCP Registry = same semantic skill discovery pattern as skill-manager-mcp

**ClaudesCorner impact:**
- dispatch.py: plan/build role formalization is worth adding as a convention (research workers = plan agents, build workers = build agents)
- LSP gap noted — code-edit quality from dispatch workers could improve with language server validation
- Open codebase available as reference implementation for agentic tool-use patterns

---

### OpenSpec — Spec-Driven Development (41.1k stars, v1.3.0, MIT)

**Signal strength:** High — directly actionable for dispatch.py + bi-agent gaps  
**What it is:** Lightweight CLI for externalizing specs before implementation. `proposal.md + specs/ + design.md + tasks.md` folder per feature. `/opsx:verify` = validation oracle step. Provider-agnostic.

**Key pattern:** Spec artifacts are versioned, frozen before `/opsx:apply`, then validated with `/opsx:verify`. Drift detected by `/opsx:sync`.

**ClaudesCorner impact:**
- dispatch.py workers: go prompt→execute with no frozen spec or verify step (3rd independent source: Remoroo + Willison + OpenSpec). Structural gap confirmed.
- bi-agent: `schema_spec.md` + `/verify` step would close DAX correctness gap
- ENGRAM bootstrap: `proposal.md + design.md` pair = standardized project scoping for self-generated tasks
- writing-plans skill: OpenSpec formalizes exactly what writing-plans does informally; `tasks.md` = TodoWrite — strong alignment
- Comparable to AWS Kiro (tool-locked): OpenSpec is model-agnostic and directly applicable

---

## Actionable Items

| Item | Priority | Status |
|------|----------|--------|
| Add `verify:` validation oracle to dispatch.py worker prompt template | High | Done (2026-04-19 ~11:00) |
| Add `spec:` artifact step + plan/build role distinction to dispatch.py workers (OpenSpec + OpenCode) | Medium | Done (2026-04-19 ~21:00) |
| Wrap FinRL-X `allocate_portfolio` as MCP tool for Fairford Phase 2 | Medium | Backlog — needs Jason to unblock Phase 2 |
| Keep `--bare` flag as default for context-heavy dispatch workers | Medium | Documented |
| Hold 4.7 upgrade — profile token cost AND instruction adherence before switching | High | Standing hold |
| Monitor Sonnet 4.6 regression reports — no clear safe current model for agentic use | Medium | Watch |
| Check dispatch worker prompts don't embed tool schemas inline (4.7 prompt-injection detection) | Low | Backlog |
| Lean into deferred-tool pattern — now model-native in 4.7 | Low | Already done; confirmed |
| Skill `verify:` sections: embed concrete assertion over behavior description | Low | Backlog |
| Evaluate AgentRQ for dispatch.py worker escalation channel | Medium | Backlog |
| Integrate AgentRQ `getWorkspace` into /status skill for blocked task visibility | Low | Backlog |
| Fairford/ENGRAM UI: prototype in Claude Code directly, not Figma-first | Low | Standing policy |
| Evaluate Fuelgauge for ClaudesCorner Windows status line (no Node, PowerShell native) | Low | Backlog |
| Evaluate AgentKey for dispatch.py worker credential governance (self-hostable, MCP-native) | Medium | Backlog |
| Evaluate Evolver GEP pattern for ENGRAM skill crystallization (EvolutionEvents = daily log analog) | Medium | Backlog |
| Explore Craft Agents fabric-mcp integration as Fairford PoC Craft source | Low | Backlog — needs Jason to unblock Phase 2 |

---

## Digest Run 7

**Sources processed:** 2  
**Files:** `2026-04-19-evolver-gep-self-evolution-engine.md`, `2026-04-19-craft-agents-mcp-native-agent-desktop.md`

---

### Evolver — GEP-Powered Self-Evolution Engine (5.2k stars, +1131 today)

**Signal strength:** Medium-High — ENGRAM structural parallel with auditable evolution trail  
**What it is:** GPL-3.0 agent evolution engine. Prompts drive evolution, not code edits. Genes/Capsules = reusable evolution assets in `assets/gep/`. EvolutionEvents = immutable audit log. Claude Code hooks at `~/.claude/` out of box.

**Key pattern:** Signal extraction from `memory/` → selector matches existing Genes → protocol-bound prompt emitted → EvolutionEvent committed. Eliminates ad hoc SOUL.md edits with auditable trail.

**Four strategy modes:** innovation (80% new), optimization, hardening, emergency repair. Signal deduplication prevents repair loops. EvoMap Hub = shared Gene pool across agent workers (skill-manager-mcp analog for distributed case).

**ClaudesCorner impact:**
- ENGRAM: Gene/Capsule = skill-manager-mcp skills; EvolutionEvents = daily_log entries. Evolver formalizes what ENGRAM does informally — worth adopting GEP naming convention in skill metadata
- feedback_flywheel.py already does signal extraction from daily logs → this is the same pattern with an audit trail added
- dispatch.py: `--loop` daemon = continuous worker without restart; evolver-mcp (no MCP yet) could expose evolution events as readable dispatch signals
- Gap: GPL-3.0 vs MIT/Apache-2.0 — contamination risk if code is incorporated into ENGRAM. Study patterns only, don't fork

---

### Craft Agents OSS — MCP-Native Agent Desktop (4.4k stars, Apache 2.0)

**Signal strength:** Medium — architecture validation + Fairford integration opportunity  
**What it is:** Electron + craft-cli desktop built on Claude Agent SDK. Todo→Done session workflow. 32+ MCP tools. AES-256-GCM credentials. Multi-provider.

**Key pattern:** `craft run` = single-shot agent execution (headless) — equivalent to dispatch.py worker spawning claude.exe. VPS server mode + thin desktop client = persistent orchestration without per-session restart.

**ClaudesCorner impact:**
- dispatch.py: `craft run` is architecturally identical to current worker pattern — Craft is a production-hardened version of the same idea with credential governance + session persistence baked in. Not a replacement, but a reference implementation
- Obsidian vault access built in — same access pattern as mcp-obsidian; Craft does it via MCP tool, not separate server
- ENGRAM: Skills system per workspace = SOUL.md equivalent. Session persistence = HEARTBEAT analog. Documentation value for ENGRAM README
- Fairford PoC gap: no fabric-mcp integration — if Phase 2 uses Craft desktop, fabric-mcp source addition is a clear contribution opportunity
- Credential governance: AES-256-GCM at rest, same pattern as AgentKey; validates AgentKey approach without external dependency

---

## Digest Run 6

**Sources processed:** 2  
**Files:** `2026-04-19-fuelgauge-claude-code-status-line.md`, `2026-04-19-agentkey-access-governance.md`

---

### Fuelgauge — Claude Code Status Line (HN: 2pts, fresh)

**Signal strength:** Low-Medium — useful but low novelty vs existing token-dashboard  
**What it is:** Shell-script Claude Code plugin (Bash/PowerShell) showing context window + 5h + 7d usage in real-time. Reads local session data, no Node.js required.

**Key differentiator:** PowerShell native on Windows (no Node, no WSL shim). Three usage windows = covers daily dispatch.py rate awareness gap that token-dashboard only shows historically.

**ClaudesCorner impact:**
- token-dashboard covers historical view; Fuelgauge complements with live at-a-glance
- PowerShell path = works natively on Windows without environment changes
- Requires `jq` + Claude Code ≥ v1.2.80 — both likely satisfied
- Low install cost: add marketplace repo → `plugin install` → `setup`
- No urgency — token-dashboard is sufficient for current workflows; worth revisiting if dispatch workers start hitting 5h cap more frequently

---

### AgentKey — Centralized Credential Governance for AI Agents (HN: 2pts, fresh)

**Signal strength:** Medium-High — directly fills dispatch.py security gap  
**What it is:** SaaS/self-hostable access governance platform. Agents register identity → request tools → human approves → credentials served AES-256-GCM encrypted on demand. Full audit log, one-click revocation, Slack/Discord webhooks.

**Key patterns:**
- Self-growing catalog: agents declare what they need, unapproved requests trigger human suggestion flow — mirrors skill-manager-mcp discovery pattern
- Audit trail + revocation = currently missing primitive in ClaudesCorner
- Self-hostable on Vercel (Neon + Upstash + Clerk) → no secrets leave local infra

**ClaudesCorner impact:**
- dispatch.py workers: currently no credential governance (API keys hardcoded / .env); AgentKey fills this without SDK dependency
- Complements AgentRQ: AgentRQ = task escalation, AgentKey = access escalation — together they close the autonomous worker accountability loop
- ENGRAM: credential governance section could reference AgentKey pattern as optional module for teams
- Priority: Medium — current single-user setup has low blast radius, but worth wiring before Fairford Phase 2 multi-worker rollout

---

## Digest Run 8

**Sources processed:** 2  
**Files:** `2026-04-19-claude-code-rust-tui.md`, `2026-04-19-rigor-ai-agent-proxy.md`

---

### Claude Code Rust — Native Rust TUI (94 stars)

**Signal strength:** Low-Medium — premature for adoption but validates dispatch.py V8 OOM risk  
**What it is:** Drop-in Rust/Ratatui replacement for Claude Code's Node.js TUI. Communicates via TypeScript Agent SDK bridge over stdio JSON. Claims 200-400 MB → 20-50 MB memory reduction, <100 ms startup vs 2-5 s.

**Key architectural note:** Rust presentation layer + TypeScript bridge = same stdio JSON interface that dispatch.py workers already use. The bridge doesn't change the API — it's a TUI-only swap.

**ClaudesCorner impact:**
- dispatch.py runs headless (`--print` / `--bare`) — TUI performance is irrelevant for workers
- Monitor if V8 OOM becomes a real dispatch.py issue (long autonomous runs) — 94 stars is too early to commit
- Pattern: Agent SDK stdio bridge = viable headless primitive if we ever need to build a custom dispatch frontend
- No action needed now

---

### Rigor — Wire-Level MITM Proxy for AI Agents (MIT, Free tier)

**Signal strength:** High — directly closes the dispatch.py verify gap at the protocol level  
**What it is:** Local MITM proxy (`127.0.0.1:8787`) that intercepts LLM traffic via `HTTPS_PROXY` env var. Rego policies (Rust OPA subset) filter/warn/rewrite responses before they reach the agent. Optional LSP integration to detect hallucinated symbols. Append-only audit log. No telemetry.

**5-stage pipeline:** Daemon → traffic routing → codebase mapping (LSP) → claim evaluation (Rego) → enforcement (block/warn/rewrite)

**ClaudesCorner impact:**
- dispatch.py workers: set `HTTPS_PROXY=http://127.0.0.1:8787` → instant hallucination filtering without modifying any worker prompts. Complements the `verify:` oracle clauses added 2026-04-19 ~11:00
- bi-agent: protect DAX output from silent fabricated measure names — set proxy for all bi-agent calls
- Pairs well with AgentKey (credential governance) + AgentRQ (task escalation) — three-layer accountability stack
- Free MIT tier covers all current ClaudesCorner needs; $19 priority tier is low risk if waitlist becomes a blocker
- **Action: evaluate Rigor free tier on a dispatch.py test run** — high signal, low install cost

---

## Digest Run 9

**Sources processed:** 2  
**Files:** `2026-04-19-deer-flow-bytedance-superagent.md`, `2026-04-19-willison-agentic-new-content-type.md`

---

### DeerFlow — ByteDance Long-Horizon SuperAgent Harness (62.6k stars, +214 today, MIT)

**Signal strength:** High — production-hardened reference for dispatch.py v2 architecture  
**What it is:** Hierarchical coordinator → dynamic sub-agent spawning for multi-hour autonomous tasks. LangGraph runtime, persistent cross-run memory, 3-mode sandboxing (local/Docker/K8s), MCP native, Slack/Telegram routing. Claude, Gemini, DeepSeek all supported.

**Key differentiators:**
- Lead coordinator spawns workers dynamically based on task complexity (vs dispatch.py static 3 workers)
- Persistent memory across runs (vs tasks.json + logs only)
- Docker/K8s sandbox modes = fixes the "workers run in-process" security gap identified in earlier digest runs
- Slack gateway = natural escalation channel; no public IP needed

**ClaudesCorner impact:**
- dispatch.py v2 design: DeerFlow's coordinator pattern = what a proper dispatch.py upgrade looks like. Current design is flat 3-worker; DeerFlow shows dynamic spawning + proper isolation as the upgrade path
- ENGRAM: DeerFlow's persistent memory layer is structurally identical — stronger reference implementation than GenericAgent for ENGRAM README's architecture section
- fabric-mcp drop-in: DeerFlow has no Fabric/Power BI MCP integration — obvious contribution opportunity if DeerFlow gains traction in enterprise use
- smolvm vs Docker: DeerFlow validates Docker container isolation as the right model for dispatch workers at production scale (smolvm = experimental/Windows-blocked anyway)
- Action: Study DeerFlow's LangGraph worker-spawning pattern before designing dispatch.py v2

---

### Willison — Adding a New Content Type (3-Part Agentic Prompt Pattern)

**Signal strength:** High — 4th corroboration of reference-repo + verify pattern; now shows real production output  
**What it is:** Concrete demonstration of the 3-part agentic prompt: (1) clone ref to /tmp, (2) imitate existing code, (3) self-validate with live server test. Added a full "beats" content type to a Django blog-to-newsletter tool in a single shot.

**Key evidence:**
- Agent inferred `beatTypeDisplay` mapping from Django model in cloned repo — no spec written, real code as source
- Self-validation via `uvx rodney` = agent confirms correctness before returning, not just on return
- "Minimal instructions + maximum context" > verbose spec — pattern now shown on a real feature

**ClaudesCorner impact:**
- dispatch.py workers: `verify:` clauses added 2026-04-19 ~11:00 were correct; this clip shows what the validation oracle looks like in practice (actual run command, not assertion comment)
- Upgrade `verify:` from description to executable: worker prompts should include runnable check command, not just "verify output is correct"
- Skills: `verify:` sections that say "check that X happened" should include a concrete shell command where possible
- This is now 4th independent source (Remoroo, Willison 04-18, OpenSpec, Willison 04-19) on same pattern — lock this in as convention

---

## Actionable Items (updated)

| Item | Priority | Status |
|------|----------|--------|
| Add `verify:` validation oracle to dispatch.py worker prompt template | High | Done (2026-04-19 ~11:00) |
| **Upgrade `verify:` clauses from descriptions to runnable commands (4-source confirmation)** | High | Done (2026-04-19 ~20:00) |
| **Evaluate Rigor free tier on a dispatch.py test run** | High | Done (2026-04-20) — NO-GO: product unverifiable, verify oracle pattern already covers output correctness; see research/2026-04-20-rigor-evaluation.md |
| **Review DeerFlow LangGraph worker-spawning for dispatch.py v2 design** | Medium | Backlog |
| Add `spec:` artifact step + plan/build role distinction to dispatch.py workers (OpenSpec + OpenCode) | Medium | Done (2026-04-19 ~21:00) |
| Wrap FinRL-X `allocate_portfolio` as MCP tool for Fairford Phase 2 | Medium | Backlog — needs Jason |
| Keep `--bare` flag as default for context-heavy dispatch workers | Medium | Documented |
| Hold 4.7 upgrade — profile token cost AND instruction adherence before switching | High | Standing hold |
| Monitor Sonnet 4.6 regression reports — no clear safe current model for agentic use | Medium | Watch |
| Evaluate AgentRQ for dispatch.py worker escalation channel | Medium | Backlog |
| Evaluate AgentKey for dispatch.py worker credential governance | Medium | Backlog |
| Evaluate Fuelgauge for ClaudesCorner Windows status line | Low | Backlog |
| Monitor claude-code-rust TUI — flag if V8 OOM surfaces in dispatch.py long runs | Low | Watch |
| Evaluate Evolver GEP pattern for ENGRAM skill crystallization | Medium | Backlog |
| Explore DeerFlow Docker sandbox + Slack gateway as dispatch.py v2 primitives | Medium | Backlog |
| fabric-mcp contribution to DeerFlow ecosystem — no Fabric MCP in their stack | Low | Backlog |
| Explore Craft Agents fabric-mcp integration as Fairford PoC Craft source | Low | Backlog — needs Jason |
| Fairford/ENGRAM UI: prototype in Claude Code directly, not Figma-first | Low | Standing policy |
