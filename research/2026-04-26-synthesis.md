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
| Add dispatch.py tier-2 worker wall-clock timeout (4h cap) | Low | Backlog — Lynagh 4-hour time-box = validated upper bound; currently unlimited |
| Add explicit success criteria to HEARTBEAT.md task descriptions | Low | Backlog — fuzzy descriptions invite scope expansion; Lynagh conservation-of-scope-creep law |
| Wire cc-canary weekly health check (thinking_redaction + Read:Edit ratio) | Low | Backlog — Willison: harness bugs indistinguishable from model drift without per-session telemetry; run `/cc-canary 30d` post-version-bump |
| Pin Claude Code version in dispatch.py worker invocations | Low | Backlog — detect upgrade-triggered regressions; Willison recommendation; retroactive window blocked (logs start Apr16) |

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
