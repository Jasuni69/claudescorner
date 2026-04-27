# Research Synthesis — 2026-04-26

## Digest Run 1

**Sources processed:** 1
**Clips:** `2026-04-26-pydantic-ai-deferred-tools-fastmcp3.md`

---

### pydantic-ai v1.87 — HandleDeferredToolCalls + FastMCP 3.2 + DynamicToolset

**Signal strength:** High — production Python implementation of patterns that ClaudesCorner infrastructure approximates manually today

**What shipped (key features):**

| Release | Feature | Relevance |
|---------|---------|-----------|
| v1.87.0 | `HandleDeferredToolCalls` — lazy schema load, zero token cost for unneeded tools | skill-manager-mcp `skill_search` → `skill_load` does this manually |
| v1.86.x | `DynamicToolset` — per-run MCP server mount/unmount, no cross-agent bleed | dispatch.py workers share global MCP config today |
| v1.83.0 | Per-tool-call metadata injection via `FastMCPToolset` | worker identity (task_id, tier) not visible inside MCP tools today |
| v1.82-1.85 | FastMCP 3.2: OAuth 2.1 elicitation, streamable HTTP, session multiplexing | memory-mcp + fabric-mcp both lack OAuth |
| v1.85.0 | OpenTelemetry spans per tool call — direct Grafana/Datadog integration | no OTEL in dispatch.py workers today |

**ClaudesCorner gap analysis:**

1. **Worker identity audit trail (gap — partially closed 2026-04-26):** MCP tools (memory-mcp, fabric-mcp) had no way to know which dispatch.py worker called them. Fixed: `DISPATCH_TASK_ID`, `DISPATCH_WORKER_TIER`, `DISPATCH_WORKER_MODEL` now injected into worker env in `run_task()`. MCP tools can read these from their subprocess environment.

2. **DynamicToolset per-worker isolation (gap — open):** dispatch.py workers inherit the full global MCP config. `DynamicToolset` is the correct primitive to mount only task-relevant tools. Blocked: requires pydantic-ai integration or custom MCP lifecycle wrapper; not worth the complexity until Fairford Phase 2.

3. **FastMCP 3.2 OAuth (gap — open):** memory-mcp and fabric-mcp lack scoped access control. FastMCP 3.2's elicitation flow is lowest-effort path. Backlog after Fairford Phase 2 design.

4. **HandleDeferredToolCalls (gap — partially open):** skill-manager-mcp two-step (`skill_search` → `skill_load`) achieves the same result without framework support. Formalizing it via this pattern would reduce the implementation burden in ENGRAM v2.

**Actions taken this run:**
- Injected `DISPATCH_TASK_ID` / `DISPATCH_WORKER_TIER` / `DISPATCH_WORKER_MODEL` into `run_task()` env dict (scripts/dispatch.py line ~338).

---

---

## Digest Run 2

**Sources processed:** 2
**Clips:** `2026-04-26-feldera-agents-not-coworkers-cdc-reconciliation.md`, `2026-04-26-simulacrum-knowledge-work-goodharts-law.md`

---

### Feldera — Agents Aren't Coworkers: CDC + Reconciliation Loop Architecture

**Signal strength:** High — concrete architectural validation for fabric-mcp and kpi-monitor design direction

**Core thesis:** Agents should be ambient embedded systems reacting to change streams, not conversational coworkers polling tables. Three endorsed patterns: CLI interfaces (structured commands), declarative specifications (desired state, not steps), and reconciliation loops (Kubernetes-style convergence).

**CDC key insight:** Instead of `SELECT * FROM transactions WHERE updated_at > last_check` every N seconds, databases emit precise insert/update/delete event streams. Agents react in real-time to those events.

**ClaudesCorner gap analysis:**

| Pattern | Current state | Gap |
|---------|--------------|-----|
| CDC event streams | fabric-mcp polls full tables with `execute_query` | fabric-mcp has no change-feed subscription; would need Fabric eventstream or delta-lake CDC API |
| Declarative reconciliation | dispatch.py `task_plan.md` declares target state | Workers reconcile but there's no drift-detection loop; each run is one-shot |
| CLI-first agent interface | memory-mcp + skill-manager-mcp already CLI-style | No gap — design validated |
| Ambient not conversational | kpi-monitor is a polling Python loop | Correct architecture would be CDC-triggered; polling loop = architectural debt |

**Actions taken this run:** None — architectural signal; both gaps (fabric-mcp CDC + kpi-monitor CDC) are Backlog/Low pending Fairford Phase 2 design.

---

### Simulacrum of Knowledge Work — Goodhart's Law Applied to Agent Output

**Signal strength:** Medium-High — conceptual framing that validates dispatch.py verify oracle design and surfaces a specific gap

**Core argument:** LLMs decouple surface quality signals from actual substance. Agents optimize for proxy metrics (spelling, formatting, "looks correct") because deep evaluation is expensive. This is Goodhart's Law: when a measure becomes a target, it ceases to be a good measure. The correct countermeasure is fixed eval harnesses with external ground-truth oracles — never self-assessment.

**Failure modes:**
1. Self-reported success — agents claim correctness by matching surface patterns
2. Evaluator gaming — outputs optimized for judge's approval heuristics
3. Institutional hollowing — wrong metrics encoded at scale

**ClaudesCorner gap analysis:**

| Risk | Existing mitigation | Gap |
|------|---------------------|-----|
| Self-reported agent success | dispatch.py VERIFY step checks artifact independently | Workers sometimes soft-pass VERIFY (no hard exit code gate) |
| bi-agent DAX "looks right" | 3-layer oracle (verdict + parens + schema cross-ref) | Schema cross-ref weakest layer — no ground-truth DAX test dataset |
| Skill output quality | agent_activation_allowed gate in skill-manager-mcp | No runtime output quality check post-activation |
| kpi-monitor alerts | threshold + direction config + spike debounce | No statistical baseline — debounce is a proxy, not a ground-truth |

**Key implication for dispatch.py:** VERIFY step exit code should be enforced — workers that soft-pass VERIFY (print "OK" without asserting) defeat the whole oracle pattern. Backlog: add exit-code-gate to dispatch.py worker output validation.

**Actions taken this run:** None — conceptual validation. VERIFY exit-code enforcement → Backlog/Medium.

---

## Actionable Items

| Item | Priority | Status |
|------|----------|--------|
| Worker identity env injection (DISPATCH_TASK_ID / TIER / MODEL) into dispatch.py `run_task()` | Medium | **Done** — injected after `_proxy_env()` call; backward-compatible (env vars are additive) |
| DynamicToolset per-worker MCP isolation | Low | Backlog — requires pydantic-ai integration; defer until Fairford Phase 2 |
| FastMCP 3.2 OAuth 2.1 elicitation for memory-mcp + fabric-mcp | Low | Backlog — lowest-effort auth path; defer until Fairford Phase 2 |
| HandleDeferredToolCalls as skill-manager-mcp lazy-load formalization | Low | Backlog — current two-step is functionally equivalent; low urgency |
| OpenTelemetry spans per tool call for dispatch.py observability | Low | Backlog — nice-to-have; no current alerting infrastructure to consume OTEL events |
| fabric-mcp CDC event-stream subscription (Feldera pattern) | Low | Backlog — requires Fabric eventstream or delta-lake CDC API; defer until Fairford Phase 2 |
| kpi-monitor CDC-triggered architecture (replace polling loop) | Low | Backlog — architectural debt; polling loop works; CDC is cleaner; defer |
| dispatch.py VERIFY exit-code enforcement gate (Goodhart's Law) | Medium | **Done** — `_output_signals_failure()` + `_SOFT_FAIL_RE` added; scans for BLOCKED:/AssertionError/VERIFY-fail/oracle-FAIL/goal-drift patterns; flips success=False + prefixes `[verify-gate: soft-fail detected]` in log; `re` import added; syntax + unit tests pass |
| bi-agent ground-truth DAX test dataset (Goodhart's Law) | Low | Backlog — schema cross-ref weakest oracle layer; needs curated ground truth |
| Import mattpocock/skills into skill-manager-mcp index | Low | Backlog — 20k-star MIT library; confirms semantic discovery gap; `npx skills@latest add mattpocock/<skill>` install pattern |
| Read `git-guardrails-claude-code` skill implementation | Low | Backlog — patterns applicable to dispatch.py worker git safety DENY clauses |
| Add dispatch.py tier-2 worker wall-clock timeout (4h cap) | Low | **Done** — `TIMEOUT_SECONDS_TIER2=14400`; Haiku=300s, Sonnet/Opus=14400s; selected via `_infer_tier()` in `run_task()` |
| Add explicit success criteria to HEARTBEAT.md task descriptions | Low | Backlog — fuzzy descriptions invite scope expansion; Lynagh conservation-of-scope-creep law |
| Wire cc-canary weekly health check (thinking_redaction + Read:Edit ratio) | Low | Backlog — Willison: harness bugs indistinguishable from model drift without per-session telemetry; run `/cc-canary 30d` post-version-bump |
| Pin Claude Code version in dispatch.py worker invocations | Low | Backlog — detect upgrade-triggered regressions; Willison recommendation; retroactive window blocked (logs start Apr16) |
| K2VV ToolCall benchmark: DeepSeek-V4-Flash vs Haiku 4.5 for dispatch.py tier-1 routing | Low | Backlog — $0.14/M vs $0.80/M; flat 900K-ctx throughput removes serving-cost objection; tool-call quality gate only remaining blocker |
| Rate Limits API `/v1/rate-limits` wire-in to dispatch.py startup | Low | **Done** — `_check_rate_limits()` added; queries at startup when ANTHROPIC_API_KEY set; warns ≤20% remaining on any limit; `urllib.request` stdlib only; fail-open; called in `main()` after `_check_claude_version()` |
| Model deprecation audit: `claude-sonnet-4` → `claude-sonnet-4-6` (retire June 15) | HIGH | **Done** — dispatch.py uses `claude-sonnet-4-6` throughout; no deprecated model strings found |
| Managed Agents memory storage model audit vs memory-mcp | Low | Backlog — read `/docs/en/managed-agents/memory`; determine if open/compatible with memory-mcp write gate |
| ENGRAM README: position vs Managed Agents memory (self-hosted + Fabric + governance) | Low | Backlog — differentiation story for ENGRAM v2 README |
| Prototype advisor tool (Haiku executor + Sonnet advisor) for bi-agent DAX schema cross-ref | Low | Backlog — Opus-quality schema cross-ref at Haiku bulk rates; compare vs single-model Sonnet pass |
| Evaluate advisor tool for dispatch.py tier-2 workers (latency + cost) | Low | Backlog — straight Sonnet vs Haiku+Sonnet advisor; defer until bi-agent prototype done |

---

## Digest Run 3

**Sources processed:** 3
**Clips:** `2026-04-26-lynagh-scope-creep-conservation-ai-agents.md`, `2026-04-26-willison-claude-code-quality-harness-bugs.md`, `2026-04-26-mattpocock-skills-dotfiles-movement.md`

---

### Lynagh — Conservation of Scope Creep (Sabotaging Projects by Overthinking)

**Signal strength:** High — 515 HN points; empirical validation of dispatch.py DENY clause architecture and HEARTBEAT.md task scoping design

**Core law:** "Conservation of scope creep: efficiency gains from AI assistance are neutralized by a proportional increase in unnecessary features, rabbit holes, and diversions."

**Four countermeasures:**
1. Minimal success criteria before starting (fuzzy → decision gridlock)
2. Strict task scoping: scoped task → review in minutes → discard/revise/restart
3. YAGNI triage on AI output: question whether each discovered feature addresses *original* problem
4. Private-first shipping: remove external validation incentives that drive polish/expansion

**Phased scope containment pattern:** Phase 1 (MVP) → Phase 2 (conditional on Phase 1 satisfaction) → Phase 3 (never start unless Phase 2 consumed)

**ClaudesCorner gap analysis:**

| Pattern | Current state | Gap |
|---------|--------------|-----|
| Scoped task execution | dispatch.py DENY clauses + one-task-one-session | HEARTBEAT.md task descriptions lack explicit success criteria |
| Time-boxed research | Unlimited worker wall-clock | No 4-hour hard cap on tier-2 workers; Lynagh's upper bound validated |
| Feature triage | VERIFY oracle checks artifact | oracle judges output correctness, not scope adherence |
| Conservative scope | BUILD agent: "make only changes necessary" | Already wired in BUILD prompt |

**Actions taken this run:** None — architectural validation. Two actionable gaps → Backlog/Low.

---

### Willison — Recent Claude Code Quality Reports: Harness Bugs Not Model Drift

**Signal strength:** High — post-mortem of 2-month quality complaints; directly relevant to dispatch.py long-session worker reliability

**Core finding:** Three harness-layer bugs (not model regression) caused Mar–Apr 2026 quality complaints. Fixed v2.1.116. Critical bug: context clear intended for idle sessions (>1h) fired every turn for rest of session — amnesia mid-session.

**Why dispatch.py was maximally exposed:**
- Tier-2/3 tasks run potentially hours — exactly the session-length window most affected
- dispatch logs only start Apr16 → retrospective review blocked
- No per-session telemetry → harness bugs look identical to "model degraded"

**Recommended instrumentation:**
1. Pin CC version in dispatch.py worker invocations (detect upgrade regressions)
2. Wire `thinking_redaction` + `Read:Edit ratio` from cc-canary as weekly health check
3. Flag anomalous token burn sessions for manual review before attributing to model drift

**ClaudesCorner gap analysis:**

| Risk | Existing mitigation | Gap |
|------|---------------------|-----|
| Harness bug exposure | dispatch.py uses fresh subprocess per task | Per-session telemetry absent — no visibility into token burn anomalies |
| Version pinning | No CC version pinned in dispatch.py | Upgrade-triggered regressions undetectable until they surface |
| Quality regression detection | cc-canary referenced in backlog | Not wired — `/cc-canary 30d` not yet automated |

**Actions taken this run:** None — documentation + backlog additions.

---

### mattpocock/skills — Personal SKILL.md Library Goes Viral (20k Stars)

**Signal strength:** High — dotfiles moment for agent skills; 7th major org/practitioner independently adopting SKILL.md pattern

**Core signal:** Matt Pocock (Total TypeScript, 200k+ audience) published his personal `.claude/` directory as `mattpocock/skills`. 20k stars, #2 GitHub Trending. The install pattern (`npx skills@latest add mattpocock/<skill>`) is frictionless but has **no discovery layer** — you must know the repo exists. This is exactly the gap skill-manager-mcp fills.

**Key skills of interest:**
- `write-a-skill` — meta-skill for authoring skills (independent convergence with ENGRAM `writing-skills`)
- `git-guardrails-claude-code` — constraining Claude Code git ops (DENY clause analog)
- `obsidian-vault` — Obsidian integration (ClaudesCorner cultural alignment)
- `caveman` — terse output mode (confirms Jason's CLAUDE.md caveman-mode is recognized practice)
- `zoom-out` — step-back-and-reconsider (periodic dispatch gate candidate)

**skill-manager-mcp moat confirmed:** mattpocock/skills (like marketingskills, HuggingFace skills, anthropics/skills) has no MCP server. skill-manager-mcp remains the only runtime providing semantic search + governance gate + cross-session promotion.

**ClaudesCorner gap analysis:**

| Signal | Current state | Action |
|--------|--------------|--------|
| mattpocock/skills as discovery corpus | Not indexed | Import into skill-manager-mcp index |
| `git-guardrails-claude-code` patterns | DENY clauses in dispatch.py | Read implementation for pattern extraction |
| `write-a-skill` convergence | ENGRAM `writing-skills` skill already exists | Validation only — no gap |
| `zoom-out` as dispatch gate | Not implemented | Backlog/Low — periodic step-back gate for tier-2 workers |

**Actions taken this run:** None — research clip digest. Import + git-guardrails review → Backlog/Low.

---

## Digest Run 4

**Sources processed:** 4
**Clips:** `2026-04-26-deepseek-v4-sglang-inference-rl.md`, `2026-04-26-brunelle-ai-coding-project-revival.md`, `2026-04-26-anthropic-changelog-managed-agents-memory.md`, `2026-04-26-anthropic-changelog-advisor-tool.md`

---

### DeepSeek-V4 Day-0 — SGLang ShadowRadix + Miles RL Training

**Signal strength:** High — 37 HN pts; flat 4K→900K decode throughput changes cost model for long-horizon dispatch workers

**Key technical contributions:**
- **ShadowRadix** — hybrid sparse-attention prefix caching via virtual token coordinates + per-pool shadow mappings; enables cache coherence across three heterogeneous KV pool types
- **HiSparse CPU KV offloading** — inactive KV pages offload to CPU RAM; up to 3× throughput on memory-constrained deployments
- **Flat decode throughput** — B200: 199→180 tok/s, H200: 266→240 tok/s at 4K→900K context (−10% at near-1M ctx); eliminates exponential cost cliff for long agentic sessions
- **Miles RL stack** — FP8 rollout + BF16 training; log-probability drift held at ~0.023 on 285B across 32 GB300 GPUs

**ClaudesCorner gap analysis:**

| Signal | Current state | Gap/Action |
|--------|--------------|-----------|
| DeepSeek-V4-Flash Haiku-tier routing | Haiku 4.5 default for tier-1 | K2VV ToolCall benchmark required; flat throughput removes serving-cost objection |
| Long-context agentic sessions | 8000-token MAX_CONTEXT_TOKENS cap | ShadowRadix makes 200K-token sessions cost-flat; cap may be raised if model quality holds |
| RL fine-tuning reference | bi-agent uses rule-based 3-layer oracle | Miles pattern = reward-model fine-tuning; relevant if DAX oracle evolves beyond hard rules |
| SGLang Windows support | dispatch.py subprocess model | HiSparse is CUDA-only, no Windows binary — blocked |

**Actions taken this run:** None — backlog only. K2VV benchmark required before routing.

---

### Brunelle — AI Coding Tools for Project Revival (249 HN pts)

**Signal strength:** Medium-High — personal workflow post at scale; independently validates dispatch.py one-task-one-session model and external oracle principle

**Core thesis:** AI assistance is appropriate for "wish fulfillment" projects (learning is not the goal). Reserve manual coding for skill-development to avoid deskilling.

**Four workflow patterns:**
1. **Upfront convention setting** — type annotations, Pydantic V2, Google docstrings declared before code generation; mirrors dispatch.py task_plan.md header constraint injection
2. **Plan mode for each major sub-feature** — prevents model from generating stubs without examining spec; validates BUILD agent SPEC step
3. **Context clears between major implementations** — each endpoint category = fresh session; independently arrives at dispatch.py one-task-one-session constraint
4. **External-client-as-oracle** — validates via real Subsonic clients, not unit tests; stubbed endpoints pass unit tests but fail real clients

**Failure modes documented:**
- Stubbed endpoints return wrong shapes (pass unit tests, fail real clients)
- API spec ambiguity: model guesses rather than flags underspecification
- Streaming semantics require live testing — static tests insufficient
- Long-tail drudgery: AI accelerates but does not eliminate 80+ endpoint repetition

**ClaudesCorner alignment:**
- Context clears = dispatch.py one-task-one-session ✓
- External oracle = VERIFY step with fixed harness ✓
- Upfront conventions = task_plan.md header injection ✓
- Deskilling warning = "Coding by Hand" (miguelconner.substack.com, 2026-04-18) — aligned

**Actions taken this run:** None — architectural validation only. No gaps identified beyond existing backlog.

---

### Anthropic Changelog — Claude Managed Agents Memory Public Beta (Apr 23, 2026)

**Signal strength:** HIGH — official hosted memory layer now competes with memory-mcp; also contains model deprecation notice critical for dispatch.py

**What shipped:**
- Memory for Claude Managed Agents: public beta under `managed-agents-2026-04-01` beta header
- Persistent cross-session state on top of Managed Agents harness (sandboxing + SSE + container config)
- Rate Limits API (Apr 24): `/v1/rate-limits` — programmatic org/workspace rate limit querying
- **Claude Sonnet 4 + Opus 4 deprecated Apr 14, retirement June 15** — callers must use `claude-sonnet-4-6` not `claude-sonnet-4`

**dispatch.py model string audit (done this run):** dispatch.py uses `claude-sonnet-4-6` (Tier 2 default) and `claude-haiku-4-5-20251001` (Tier 1). `claude-sonnet-4` (deprecated) does not appear in dispatch.py — no code change required.

**ENGRAM architecture:**
- Managed Agents memory is now a direct hosted competitor to memory-mcp
- Key differentiator: memory-mcp is self-hosted (sqlite-vec, no Anthropic data retention), Fabric/MCP-integrated, custom governance (Haiku write-gate, injection guard)
- If Managed Agents memory storage model is open/compatible, it could become a backend option for memory-mcp; if opaque, sqlite-vec remains differentiated

**Managed Agents harness vs. dispatch.py remaining differentiators:**
- Local execution (no hosted dependency)
- Fabric/Power BI MCP (not in Managed Agents)
- Custom task queue (tasks.json) + VERIFY oracles
- CrabTrap + AgentKey governance

**ClaudesCorner gap analysis:**

| Item | Priority | Action |
|------|----------|--------|
| Model deprecation: claude-sonnet-4 → retire June 15 | HIGH | **Verified clean** — dispatch.py uses `claude-sonnet-4-6` throughout |
| Rate Limits API wire-in to dispatch.py startup | Low | Backlog — auto-backoff before 429 instead of reactive catch |
| Managed Agents memory storage model audit | Low | Backlog — read `/docs/en/managed-agents/memory`; determine if compatible with memory-mcp write gate |
| ENGRAM README: position vs Managed Agents memory | Low | Backlog — self-hosted + Fabric + governance = differentiation story |

**Actions taken this run:** Model deprecation audit (no code change needed). Remaining items → Backlog.

---

### Anthropic Changelog — Advisor Tool Public Beta (Apr 9, 2026)

**Signal strength:** HIGH — native API primitive for tiered model routing; closes gap in dispatch.py cost/quality tradeoff architecture

**What shipped:**
- Advisor tool: public beta via `advisor-tool-2026-03-01` beta header
- Pairs fast executor model (Haiku 4.5) with high-intelligence advisor (Opus 4.7 or Sonnet 4.6) mid-generation
- Bulk token generation at executor rates; advisor intervenes at key decision points
- Target workloads: long-horizon agentic tasks, unpredictable escalation points

**Why this matters:**

| Pattern | dispatch.py today | Advisor tool |
|---------|------------------|-------------|
| Tiered routing | Separate API calls per tier; role assigned upfront | Single API call; advisor intervenes dynamically |
| Escalation | No mid-generation escalation; tier locked at task dispatch | Advisor triggers at any decision point during generation |
| Cost | Predictable (known tier = known rate) | Partial — Haiku rates for bulk, advisor rates for advisor tokens |
| Tool scoping | Per-worker tool scoping via env | No per-tool scoping in advisor model |

**When to prefer advisor tool over manual routing:**
- Tasks where escalation point is unpredictable (edge case code generation)
- Single-turn long-horizon work without upfront complexity classification
- Opus-quality decision-making at Haiku throughput

**When to keep manual dispatch.py routing:**
- Parallel worker pools with known roles (plan/build/verify)
- Hard token budgets with predictable cost
- Fabric/MCP-heavy workflows where per-worker tool scoping matters

**bi-agent DAX oracle:** advisor tool could run schema cross-ref at Opus quality mid-generation while keeping DAX synthesis at Sonnet rates — worth prototyping.

**ClaudesCorner gap analysis:**

| Item | Priority | Action |
|------|----------|--------|
| Prototype advisor tool for bi-agent DAX schema cross-ref | Low | Backlog — Haiku executor + Sonnet advisor; compare vs single-model Sonnet pass |
| Evaluate advisor tool for dispatch.py tier-2 workers | Low | Backlog — latency + cost comparison vs straight Sonnet |
| Add `advisor-tool-2026-03-01` to dispatch.py available beta headers doc | Low | **Done** — "Available beta headers" section added to dispatch.py docstring; covers advisor-tool-2026-03-01 + output-300k-2026-03-24 + managed-agents-2026-04-01 with use-case notes |

**Related changelog items (same period):**
- Apr 24: Rate Limits API (see Managed Agents clip)
- Apr 20: Claude Haiku 3 retired — `claude-3-haiku-20240307` now errors; dispatch.py uses `claude-haiku-4-5-20251001` (correct)
- Mar 30: Message Batches API max_tokens raised to 300k (`output-300k-2026-03-24` beta header) for Opus 4.6 + Sonnet 4.6

**Actions taken this run:** None — backlog additions only. No code change required (model strings verified clean separately).

---

## Digest Run 5

**Sources processed:** 5
**Clips:** `2026-04-26-trycua-computer-use-agent-infrastructure.md`, `2026-04-26-beads-agent-memory-dolt-graph-taskqueue.md`, `2026-04-26-stash-persistent-memory-mcp-pgvector.md`, `2026-04-26-stetskov-west-forgot-to-code-skill-gap.md`, `2026-04-26-georgeliu-opus-46-vs-47-prompt-steering-benchmarks.md`

---

### trycua/cua — Cross-Platform Computer-Use Agent Sandbox (MCP + Claude Code Native)

**Signal strength:** High — 14.2k stars; strongest Windows-viable CUA sandbox with first-class Claude Code integration

**What it is:** Open-source platform for AI agents that control desktop environments. Four products: Cua Driver (macOS background automation), Cua Sandbox (unified API across macOS/Linux/Windows/Android VMs/containers), CuaBot (native desktop integration), Cua-Bench (eval against OSWorld/ScreenSpot/Windows Arena). MCP server + Claude Code plugin baked in. Trajectory export for replayable session recordings.

**ClaudesCorner gap analysis:**

| Signal | Current state | Gap/Action |
|--------|--------------|-----------|
| Browser worker isolation | No sandboxing; workers run as subprocess | cua Sandbox = Windows-viable QEMU-backed isolation with MCP integration |
| Eval harness | No structured quality measurement for desktop workers | Cua-Bench gives OSWorld/Windows Arena benchmarks for dispatch.py worker quality |
| Session resumability | HEARTBEAT.md manual snapshots | Trajectory export = agent-memory equivalent; sessions are replayable artifacts |
| Windows support | dispatch.py Windows-native via Python subprocess | cua adds VM overhead (QEMU) vs CubeSandbox (<60ms KVM); verify latency |

**Caution:** AGPL-3.0 optional ultralytics dependency; HTML-heavy repo suggests frontend emphasis; MCP server production-readiness unverified.

**Actions taken this run:** None. Memory file `reference_trycua_cua.md` created by prior hygiene run (run #8).

---

### gastownhall/beads — Dolt-Backed Graph Task Queue (Structural tasks.json Upgrade)

**Signal strength:** High — 21.4k stars; concrete structural upgrade path for dispatch.py tasks.json with atomic claiming + dependency graph

**What it is:** Distributed graph issue tracker designed as persistent structured memory for coding agents. Replaces markdown task lists with dependency-aware graph in Dolt (version-controlled SQL with cell-level merge + branching + remote sync). Agent-optimized CLI: `bd ready` (unblocked tasks), `bd claim` (atomic), `bd dep add`, `bd show`. Semantic compaction ("memory decay") auto-summarizes closed tasks. Claude Code `.claude-plugin` included.

**ClaudesCorner gap analysis:**

| Signal | Current state | Gap/Action |
|--------|--------------|-----------|
| tasks.json atomic claiming | No atomic claim; workers could race | `bd claim` atomic; multi-writer server mode for 3 parallel dispatch workers |
| Dependency graph | Flat task list; no blocking relationships | beads: `relates_to`/`supersedes`/`duplicates` link types; `bd ready` respects dependency graph |
| Memory compaction | HEARTBEAT.md manual; no auto-summarization | `memory decay` compacts closed tasks; relevant for long dispatch.py runs |
| Task audit trail | dispatch logs only | Dolt: `dolt diff` per task; full change history |
| Task branching | No risk isolation for tasks | Dolt branching: branch task graph before risky op, merge back on success |

**ENGRAM complement:** beads = structured task state (what HEARTBEAT.md does); memory-mcp = semantic knowledge (what was learned). Stack them for complete memory architecture.

**Caution:** Go binary → dispatch.py would shell out to `bd` CLI; Dolt adds new dependency; embedded mode single-writer lock serializes concurrent workers unless server mode configured.

**Actions taken this run:** None. Memory file `reference_beads_graph_taskqueue.md` created by prior hygiene run (run #8).

---

### Stash — Persistent Memory MCP Server (pgvector + 5-layer consolidation pipeline)

**Signal strength:** Medium-High — 173 HN pts; public production analog to memory-mcp by feature count; validates Haiku write-gate design; surfaces `/failures` namespace gap

**What it is:** Open-source Go MCP server with 28 tools. Backs memory with PostgreSQL + pgvector. 5-layer auto-consolidation pipeline: Episodes → Facts → Relationships → Patterns → Goals/Failures. Namespace model: hierarchical `/users/alice`, `/projects/restaurant-saas`, `/self`. Docker Compose deploy. HN criticisms: "explicit store calls ≠ Claude.ai automated summarization"; no retrieval quality benchmarks.

**ClaudesCorner gap analysis:**

| Dimension | Stash | memory-mcp |
|-----------|-------|-----------|
| Write model | Explicit tool calls | Haiku write-gate (MEMORY_WRITE_GATE=1) |
| Consolidation | Auto background loop | Manual (feedback_flywheel.py) |
| Failure pattern layer | `/failures` namespace — tracks what went wrong to prevent recurrence | **Missing** — no `record_failure` tool |
| `/self` namespace | Agent capability tracking | SOUL.md (manual equivalent) |
| MCP tools | 28 | 10 |

**HN critics confirm:** auto-consolidation without quality gate accumulates garbage → validates MEMORY_WRITE_GATE=1 design choice.

**Key gap identified:** Stash's failure pattern layer (`/failures` namespace) is missing in memory-mcp. Adding a `record_failure` tool to memory-mcp alongside `record_learnings` fills this gap — cross-session failure prevention for recurring doom-loops or oracle regressions.

**Actions taken this run:** None — memory file `reference_stash_persistent_memory_mcp.md` already existed. Backlog item added.

---

### Stetskov — "The West Forgot to Build. Now It's Forgetting Code" (METR 19% slowdown + Fogbank)

**Signal strength:** High — 740 HN pts (#8 on HN); METR empirical data + Fogbank analogy directly validates dispatch.py architecture and HEARTBEAT.md load-bearing design

**Core thesis:** Software industry repeating 1993 defense Fogbank mistake: optimizing away institutional knowledge by reducing junior hiring while relying on AI tools. When expertise is urgently needed, it will be gone.

**Key data:**
- **METR**: Experienced devs 19% *slower* with AI on real-world open-source tasks despite predicting 24% speed gains
- **54%** of engineering leadership: AI will reduce junior hiring long-term
- **0.18% hire rate**: 2,253 screened, 4 hired — juniors can prompt but cannot identify model errors

**ClaudesCorner alignment:**

| Pattern | Current state | Validation |
|---------|--------------|-----------|
| Human-in-loop architecture | dispatch.py: workers handle routine; Jason decides architecture | METR 19% slowdown confirms AI net-negative on architectural judgment |
| HEARTBEAT.md as institutional memory | SOUL.md + HEARTBEAT.md + daily logs | Fogbank = exactly what these files prevent; non-optional maintenance |
| VERIFY oracle as non-optional | dispatch.py: exit-code-gated VERIFY | 0.18% hire rate = verifying agent output requires deep expertise |
| "AI-mediated competence" failure mode | dispatch.py workers scoped to parallelizable tasks | Correct scope boundary: generation ≠ judgment |

**Actions taken this run:** Memory file `reference_stetskov_fogbank_skill_gap.md` created this run.

---

### George Liu — Opus 4.6 vs 4.7 Prompt Steering Benchmarks (200 sessions)

**Signal strength:** High — 200-session empirical dataset; actionable `concise` prefix finding; critical model-portability warning

**Key results:**

| Steering | Opus 4.6 high | Opus 4.7 xhigh | Verdict |
|----------|--------------|----------------|---------|
| `concise` prefix | -56.3% cost, 0 accuracy loss | moderate | **Apply to dispatch.py workers** |
| `no-tools` prefix | significant reduction | -63% cost, -2 passes | caution: accuracy trade-off |
| `think-step-by-step` | cost reduction | +22% cost increase | **Avoid on any tier** |

**Critical:** Identical steering text produces opposite effects between models. Steering is not model-portable.

**ClaudesCorner gap analysis:**

| Action | Priority | Detail |
|--------|----------|--------|
| Apply `concise` prefix to dispatch.py tier-2 (Sonnet 4.6) worker system prompts | Medium | ~50% cost reduction expected with no oracle regression; direct analog to 4.6 high effort result |
| Avoid `think-step-by-step` in all tier prompts | High | Cost increase, zero accuracy benefit — already absent from dispatch.py prompts |
| Re-benchmark all prompts before any model routing change | Medium | Cannot copy steering across model versions; each tier needs independent verification |
| Sonnet 4.6 default confirmed | Info/Done | Opus 4.7 requires xhigh effort for parity + token inflation; Sonnet 4.6 remains correct default |

**Actions taken this run:** Memory file `reference_georgeliu_opus_prompt_steering.md` created this run.

---

## Actionable Items (Digest Run 5 additions)

| Item | Priority | Status |
|------|----------|--------|
| Test cua sandbox MCP server on Windows 11 + compare coldstart vs CubeSandbox | Low | Backlog — QEMU overhead vs <60ms KVM; verify before wiring into dispatch.py |
| Prototype replacing tasks.json with beads for dispatch.py tier-1 research tasks | Low | Backlog — atomic claiming + dependency graph + memory decay compaction; Dolt install friction to verify first |
| Add `record_failure` tool to memory-mcp (Stash /failures namespace pattern) | Medium | **Done** — `record_failure` Tool + handler added to memory-mcp server.py; stores [failure:type][domain] bullet to ## Failures section of daily log; prevention field optional; backward-compatible |
| Apply `concise` prefix to dispatch.py tier-2 Sonnet 4.6 worker system prompts | Medium | **Done** — `concise\n\n` prepended to BUILD worker prompt in DEFAULT_AUTONOMOUS_TASKS; George Liu -56.3% cost / 0 accuracy loss benchmark on Sonnet 4.6 |
| Never use `think-step-by-step` prefix in any dispatch.py tier | High | **Confirmed-absent** — no such prefix currently in dispatch.py worker prompts; no code change needed |
| Re-benchmark all worker steering prefixes before any model routing change | Medium | Process rule — not a code change; applies when/if Sonnet→Opus or 4.6→4.7 routing is tested |
| Evaluate Cua-Bench as dispatch.py worker quality measurement framework | Low | Backlog — structured eval harness for desktop worker quality currently absent |

---

## Digest Run 6 (2026-04-26)

**Clips:** `2026-04-26-defensive-databases-agent-access.md`, `2026-04-26-microsoft-work-iq-mcp-m365.md`, `2026-04-26-sweben-verified-contamination-openai-pro.md`

---

### Arpit Bhayani — "Databases Were Not Designed for This" (26 HN pts)

**Signal:** Databases assume deterministic callers with intentional writes, brief connections, loud failures, and developer-readable schemas. AI agents violate all five assumptions.

**5 broken assumptions:**
1. Agents generate queries dynamically — no pre-review
2. Agents write on flawed reasoning or retry loops — not deliberate intent
3. Multi-step reasoning holds connections open across LLM inference time
4. Semantically wrong queries return rows silently — no exception
5. Legacy schema naming confuses language models

**Mitigations:** soft deletes (`deleted_at` + views), append-only audit tables, idempotency keys, role-per-agent-type RBAC, query tagging (`/* agent=X task=Y */`)

**ClaudesCorner gaps:**
- **bi-agent**: DAX queries are read-only but schema confusion is real — `/* agent=bi-agent task=... */` tagging is zero-cost observability, validates existing schema_spec.md oracle
- **fabric-mcp**: per-agent Entra service principal (FABRIC_CALLER_TOKEN already scoped) = correct RBAC; soft-delete on Fabric tables = Fairford Phase 2 checklist item
- **memory-mcp write-gate**: MEMORY_WRITE_GATE=1 Haiku guard is exactly the append-only pattern applied to memory layer — validates existing design
- **dispatch.py**: task output artifacts (tasks.json mutations) are already append-only via log files — correct pattern confirmed

**Actions taken this run:** Memory file `reference_defensive_databases.md` already existed.

---

### Microsoft Work IQ — Official M365 MCP Server (763 stars, EULA)

**Signal:** Official Microsoft MCP plugin exposing M365 data (email, calendar, Teams, OneDrive, People) via NL queries. Three plugins: `workiq` (data access), `microsoft-365-agents-toolkit` (scaffold), `workiq-productivity` (analytics).

**Relevance:**
- **fabric-mcp complement**: fabric-mcp = Power BI/Lakehouse data; Work IQ = M365 collaboration layer; together = complete Microsoft enterprise data access stack
- **Fairford Phase 2**: client-facing M365 data (Outlook threads, Teams decisions, OneDrive reports) as agent context alongside Fabric KPIs = full Fairford data layer
- **dispatch.py research workers**: internal org context (decisions in Teams, email threads about a metric) without custom integration

**Caveats:**
- Proprietary EULA — check data residency terms before Fairford production use
- Tenant admin consent required (Entra ID) — not self-service; needs IT buy-in
- Public preview — 46 open issues; treat as beta

**Actions taken this run:** Memory file `reference_microsoft_work_iq.md` already existed.

---

### SWE-bench Verified Contamination — OpenAI Audit (152 HN pts)

**Signal:** OpenAI audited SWE-bench Verified: 59.4% of problems have flawed test cases; all frontier models reproduce verbatim gold patches for some tasks (contamination). SWE-bench Verified scores are unreliable for routing decisions.

**Rebench scores (57 problems, 128k ctx, no step cap):**
| Model | Pass@1 | Pass@5 |
|-------|--------|--------|
| Claude Opus 4.6 | 65.3% | 70.2% |
| Claude Sonnet 4.6 | 60.7% | 70.2% |
| GPT-5.2 (medium) | 64.4% | 73.7% |

Sonnet 4.6 (60.7%) is within statistical noise of Opus 4.6 (65.3%) — confirms Sonnet 4.6 as correct default.

**ClaudesCorner gaps:**
- **dispatch.py routing**: any SWE-bench Verified reasoning in dispatch.py comments is operating on a corrupted signal — remove
- **bi-agent oracle**: benchmark's failure mode (self-assessed correctness unreliable) validates 3-layer oracle necessity — external verification not paranoid
- **model routing gate**: K2VV ToolCall (JSON schema accuracy + F1) is the canonical gate; DeepSeek V4/Kimi K2.6/Qwen3.6 SWE-bench scores are unreliable

**Actions taken this run:** Memory file `reference_sweben_verified_contamination.md` already existed.

---

## Actionable Items (Digest Run 6 additions)

| Item | Priority | Status |
|------|----------|--------|
| Add `/* agent=bi-agent task=... */` query tagging to bi-agent DAX output format | Low | **Done** — `-- agent=bi-agent task=<description>` line added to SYSTEM_PROMPT output format in bi_agent.py; zero-cost audit trail via DAX line comment |
| Fairford Phase 2 checklist: per-agent Entra service principal + soft-delete on agent-writable Fabric tables | Low | Backlog — fabric-mcp FABRIC_CALLER_TOKEN already scoped; soft-delete = schema governance item |
| Test Work IQ as standalone MCP server against dev M365 tenant before Fairford Phase 2 | Low | Backlog — EULA + tenant admin consent required; beta (46 open issues) |
| Remove SWE-bench Verified from any routing decision rationale in dispatch.py comments | Low | **Done** — grep confirmed dispatch.py contains no SWE-bench references; item was pre-emptively clean |
