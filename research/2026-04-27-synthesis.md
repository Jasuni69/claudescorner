# Research Synthesis — 2026-04-27

## Digest Run 1

**Sources processed:** 2
**Clips:** `2026-04-27-davila7-claude-code-templates.md`, `2026-04-27-koshyjohn-ai-elevate-thinking-not-replace.md`

---

### davila7/claude-code-templates — CLI + analytics dashboard for Claude Code configuration discovery

**Signal strength:** High — 25.6k stars (+320 today, GitHub Trending Python); closest public analog to skill-manager-mcp as a discovery/install surface

**What it is:**

CLI tool + web dashboard (`aitmpl.com`) for discovering, installing, and monitoring Claude Code agents, commands, MCP configs, settings, hooks, and project templates.

| Component | Description | ClaudesCorner relevance |
|-----------|-------------|------------------------|
| Component library (100+ items) | Pre-built specialist agents, MCP server wiring configs, skill templates, hook templates | Potential import pool for dispatch.py worker prompts + skill-manager-mcp catalog |
| Analytics dashboard | Real-time session state, conversation monitor, health diagnostics | Fills dispatch.py real-time burn-rate gap that token-dashboard (batch, :5050) doesn't cover |
| Cloudflare Tunnel support | Remote monitoring via tunnel | Zero-infra remote dashboard for dispatch.py sessions |
| Plugin skills (v1.28.3) | Skills bundled with MCP configs as single installable unit | Independently validates ENGRAM plugin bundle pattern (Anthropic MCP Production Guide, Apr 23) |
| K-Dense AI scientific skills | 139 items under Apache 2.0 | Underexplored oracle pattern source for bi-agent |

**Gap vs. skill-manager-mcp:**

No semantic search (FTS5+vector), no write-gate, no `agent_activation_allowed` governance. skill-manager-mcp's runtime governance layer is differentiating — this tool is complementary (discovery/install) not competitive (runtime governance). The closest competitor pattern is CowAgent skill hub (43k-star, 2026-04-26).

**ClaudesCorner gap analysis:**

1. **Real-time session monitor (gap — open):** dispatch.py logs are post-hoc; token-dashboard reads heartbeat_run.log. davila7's live session state detection + Cloudflare Tunnel = lightweight path before building a custom streaming dashboard. Evaluate before next token-dashboard enhancement sprint.

2. **K-Dense AI scientific skills (gap — partially open):** 139 items not yet scanned for bi-agent oracle patterns or dispatch.py worker prompt improvements. Backlog/Low: scan K-Dense library for DAX/analytics specialist prompts.

3. **Plugin skills bundling (validated):** ENGRAM's skill+MCP co-bundle pattern is correct; davila7's v1.28.3 plugin model is independent convergence. No action needed — validation only.

**Actions taken this run:** None — research digest only. Actionable gaps → Backlog table below.

---

### Koshy John — "AI Should Elevate Your Thinking, Not Replace It"

**Signal strength:** High — 189 HN pts / 155 comments; empirical framing with direct calibration implications for dispatch.py worker scope boundaries

**Core argument:**

Two mutually exclusive paths in AI-assisted engineering:

| Path | AI Role | Human Role | System-level analog |
|------|---------|------------|---------------------|
| Leverage | Mechanical execution, boilerplate, scaffolding | Problem framing, tradeoffs, original judgment | dispatch.py workers execute; human (or verify oracle) owns decision layer |
| Dependency | Avoid understanding | Avoid ownership, avoid struggle | Automating the decision layer — the failure mode VERIFY oracle guards against |

Key warning: presenting AI-generated reasoning you don't understand as your own = dependency at individual scale. At system scale: automating the decision layer (not just execution) is the architectural dependency trap.

**Three analogies (signal extraction):**

1. **Test-copying** → surface fluency without foundational competence; maps to workers that pass VERIFY by pattern-matching the oracle output format without satisfying the underlying constraint
2. **Calculator** → informed tool vs. dependency; maps to skill scope: skills should compress mechanics, not judgment
3. **Self-driving** → automation fails in nonstandard conditions; maps to dispatch.py doom-loop + CrabTrap escalation: automated path fails → human must be able to take over

**Calibration for ClaudesCorner design:**

- **Skill scope rule (codified):** A skill that answers "what should I do?" = dependency. A skill that executes "what I've decided" = leverage. This is the correct test for skill-manager-mcp scope decisions — apply when writing new skills.
- **VERIFY oracle interpretation:** The 3-layer DAX oracle (bi-agent) is the system-level equivalent of "owning the tradeoff." It doesn't just check output format; it checks intent-correspondence.
- **dispatch.py DENY clauses:** Bounding worker scope is the architectural implementation of the leverage vs. dependency distinction. Workers that can reframe their own task are the dependency trap at agent scale.

**Actions taken this run:** None — architectural validation. Skill scope rule → codified as reference below.

---

## Backlog Table — Digest Run 1 (2026-04-27)

| Item | Priority | Status |
|------|----------|--------|
| Scan K-Dense AI scientific skills (139 items) for bi-agent DAX oracle patterns | Low | Backlog — check `aitmpl.com` or K-Dense repo for analytics/DAX specialist prompts |
| Evaluate davila7 Cloudflare Tunnel session monitor as dispatch.py live visibility layer | Low | Backlog — compare vs token-dashboard enhancement before next sprint |
| Skill scope rule: "executes what I've decided" vs "answers what should I do" | Reference | Codified — apply as acceptance criterion when writing new skills in skill-manager-mcp |
| Koshy John two-path framework: architecture validation only | Info/Done | Validates dispatch.py DENY clauses + one-task-one-session + human-in-loop escalation |
| davila7 plugin skill bundling pattern | Info/Done | Validates ENGRAM plugin bundle pattern; no code change needed |

---

## Digest Run 2

**Sources processed:** 2
**Clips:** `2026-04-27-celestoai-smolvm-agent-sandbox.md`, `2026-04-27-yourmemory-biological-decay-ai-memory.md`

---

### CelestoAI SmolVM — Firecracker Agent Sandbox with Python SDK

**Signal strength:** Medium — 446 stars, early-stage; Firecracker backend is production-grade (AWS Lambda); Windows not yet supported (direct blocker for ClaudesCorner Win11 host)

**What it is:** Python-SDK-first agent sandbox — Firecracker on Linux, QEMU on macOS — with hardware VM isolation, domain allowlists, snapshot/restore, headless browser, and pre-installed Claude Code + Codex. ~500ms coldstart.

**Differentiation vs prior sandbox options:**

| Sandbox | VMM | Coldstart | Windows | SDK |
|---------|-----|-----------|---------|-----|
| CelestoAI SmolVM | Firecracker/QEMU | ~500ms | No | Python |
| CubeSandbox (TencentCloud) | RustVMM+KVM | <60ms | No | REST |
| smol-machines/smolvm | libkrun | <200ms | No | CLI |

**ClaudesCorner gap analysis:**

| Feature | Relevance | Status |
|---------|-----------|--------|
| Hardware VM isolation | dispatch.py worker isolation (no container breakout) | Blocked — Windows host not supported |
| Domain allowlists | Built-in CrabTrap substitute inside sandbox boundary | Blocked — same reason |
| Snapshot/restore | Cheap rollback on failed dispatch.py tasks — snapshot pre-write, restore on VERIFY failure | Blocked — same reason |
| Pre-installed Claude Code | Closes dispatch.py worker bootstrap gap | Blocked — same reason |

**Actions taken this run:** None — Windows blocker. Backlog: evaluate when Windows support ships or Linux deploy target added.

---

### YourMemory — Ebbinghaus Forgetting Curve for AI Agent Memory

**Signal strength:** High — LoCoMo Recall@5 59% vs Zep Cloud 28% (2× improvement); directly addresses memory-mcp's weakest layer (stale entry expiry). License: CC-BY-NC-4.0 (blocks Fairford direct fork).

**Core concept:** Memories decay exponentially via `strength(t) = initial_strength × exp(-λ × t / (importance × category_weight))`. Auto-prune on 24h cycle when strength < 0.05. Category survival: strategy ~38d, failure ~11d.

**ClaudesCorner gap analysis:**

| Gap | Current state | YourMemory pattern |
|-----|--------------|-------------------|
| Stale entry expiry | stale-memory-scanner scores batch; no auto-prune | APScheduler 24h decay prune below 0.05 threshold |
| Failure memory half-life | All memory types retained equally | failure=11d, strategy=38d → `decay_category` field on write |
| Two-pass retrieval | brain-memory: 2-pass (N-pass) cosine similarity | vector→graph BFS validates approach; BFS adds entity-relation recall gap |
| Eval harness | memory-mcp: no quality benchmark | LoCoMo (1,534 QA pairs) is the correct target |
| Write-gate | MEMORY_WRITE_GATE=1 | YourMemory has no write-gate — validates memory-mcp design as differentiator |

**Specific gaps for memory-mcp:**
1. **`decay_category` field (gap — open):** Write schema has no category-specific retention hint. Adding `decay_category` (feedback=short, project=medium, reference=long) enables future decay-based pruning without a full rewrite.
2. **Auto-prune pass (gap — open):** No expiry mechanism today. APScheduler or cron-triggered prune pass against daily log entries is the lowest-effort implementation path.
3. **LoCoMo eval (gap — open):** memory-mcp has no benchmark; LoCoMo is the correct open dataset (1,534 long-history QA pairs).

**Actions taken this run:** None — research digest only. Three gaps → Backlog table below.

---

## Backlog Table — Digest Run 2 (2026-04-27)

| Item | Priority | Status |
|------|----------|--------|
| Evaluate CelestoAI SmolVM as dispatch.py worker sandbox (Windows support or Linux target) | Low | Backlog — blocked: Windows not supported; watch star trajectory + Windows roadmap |
| Add `decay_category` field to memory-mcp write schema (feedback=short, project=medium, reference=long) | Low | Backlog — enables future decay-based pruning; additive schema change |
| Add auto-prune pass to memory-mcp (APScheduler or cron, strength < threshold) | Low | Backlog — YourMemory pattern; requires decay scoring logic before prune |
| Evaluate LoCoMo as memory-mcp quality eval harness (1,534 long-history QA pairs) | Low | Backlog — correct benchmark; no action until decay scoring in place |
| YourMemory BFS graph-expansion layer for brain-memory retrieval | Low | Backlog — watch for license change (CC-BY-NC-4.0 blocks commercial fork) |

---

## Digest Run 3

**Sources processed:** 2
**Clips:** `2026-04-27-anthropic-project-deal-agent-commerce.md`, `2026-04-27-mcp-agent-mail-multi-agent-coordination.md`

---

### Anthropic Project Deal — Claude-Run Marketplace Experiment

**Signal strength:** High — Anthropic internal research (Dec 2025, published Apr 2026); 186 deals, $4,000 real goods; direct empirical evidence for model tier routing decisions

**What it is:** 69 Anthropic employees delegated full trade negotiations to Claude agents (Opus vs Haiku tier) in a classified Slack-based marketplace. Agents negotiated autonomously — no human intervention during deal-making.

**Key findings:**

| Finding | System-level implication |
|---------|--------------------------|
| Opus generated $3.64/item more than Haiku on negotiation tasks | Model tier is not fungible at decision-making tasks; Haiku-for-judgment = invisible underperformance |
| Humans with Haiku agents didn't perceive disadvantage vs Opus | No self-correction signal from operators using wrong tier — governance must be explicit |
| Agents coordinated via natural language (Slack) without formal protocol | dispatch.py workers can coordinate via shared markdown artifacts (HEARTBEAT.md / Agent Mail) without a dedicated protocol layer |
| Edge cases emerged (duplicate snowboard, "gift to itself") | Autonomous agents produce unexpected behavior at scale — verify oracle + CrabTrap boundary = correct mitigation |

**ClaudesCorner gap analysis:**

1. **Explicit model-tier enforcement (gap — open):** dispatch.py workers are routed by tier but nothing prevents task escalation from wrong tier. The $3.64 gap argues for hard model tier assertion in `run_task()` — not just cost routing.
2. **Asymmetric-awareness governance (gap — open):** Operators (Jason) can't see when workers are underperforming their tier. This is the invisible-underperformance gap. dispatch.py VERIFY oracle catches output failures but not quality-under-threshold.
3. **Agent-to-agent commerce (info):** Validates ENGRAM multi-agent scope. No immediate action needed.

**Actions taken this run:** Memory file created. Actionable gaps → Backlog table below.

---

### MCP Agent Mail — Asynchronous Coordination Layer for Multi-Agent Coding Workflows

**Signal strength:** High — 1.9k stars, MIT, FastMCP; directly addresses dispatch.py parallel worker race condition gap; git-as-audit-trail pattern aligns with HEARTBEAT.md

**What it is:** FastMCP HTTP server providing file reservations (exclusive/shared leases), agent identity registry, inbox/threading, and cross-project approval chains for parallel coding agents. Git + SQLite FTS5 dual persistence.

**Architecture summary:**

| Component | Role | ClaudesCorner analog |
|-----------|------|----------------------|
| File reservations | Advisory leases before editing | Fills dispatch.py parallel-worker race condition gap |
| Agent identity | Register with name/program/model | dispatch.py worker identity env vars (DISPATCH_WORKER_TIER etc.) |
| Inbox / threading | Mid-task status signals between workers | Currently impossible — workers are isolated subprocesses |
| Git-backed messages | Human-auditable markdown artifacts | Same pattern as HEARTBEAT.md + daily memory logs |
| Beads integration | Task prioritization complement | tasks.json analog |

**Key design decisions:**

- **Human Overseer:** Humans inject high-priority messages agents recognize and prioritize. Correct hierarchy model.
- **Plan-first recommendation:** README says "use Opus until granular markdown plan, then iterate." = dispatch.py task_plan.md pattern independently validated.
- **No semantic search** over message history (FTS5 only) — memory-mcp differentiator holds.

**ClaudesCorner gap analysis:**

1. **dispatch.py file race condition (gap — open):** Two workers editing overlapping files currently rely on git worktrees for isolation. Agent Mail advisory leases = lighter alternative for cooperative (non-risky) tasks.
2. **Mid-task worker signals (gap — open):** Workers currently can't signal "editing auth.py — hands off" to concurrent workers. Agent Mail inbox + file reservation closes this.
3. **dispatch.py v2 topology (backlog):** Beads (task prioritization) + Agent Mail (coordination) maps to tasks.json + Agent Mail as a v2 multi-worker upgrade path. Not immediate.

**Actions taken this run:** Memory file created. Actionable gaps → Backlog table below.

---

## Backlog Table — Digest Run 3 (2026-04-27)

| Item | Priority | Status |
|------|----------|--------|
| Hard model-tier assertion in dispatch.py `run_task()` — prevent task from running on wrong tier | Low | Backlog — Anthropic Project Deal $3.64 gap; add assert on `_infer_tier()` result vs task tag |
| Evaluate MCP Agent Mail file reservations as lightweight dispatch.py parallel-worker race condition mitigation | Low | Backlog — alternative to git worktrees for cooperative tasks; MIT, FastMCP, Python 3.14+ |
| Anthropic Project Deal — dispatch.py tier routing confirmation | Info/Done | $3.64/item Opus vs Haiku gap validates current tier routing; no code change |
| MCP Agent Mail plan-first pattern | Info/Done | Validates task_plan.md; no code change |
