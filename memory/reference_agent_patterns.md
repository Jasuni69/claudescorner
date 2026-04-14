---
name: Encyclopedia of Agentic Coding Patterns — Top 10 for ClaudesCorner
description: 10 most relevant patterns from aipatternbook.com (Wolf McNally, 190+ patterns). Focus on multi-agent, memory, context, skills, and governance.
type: reference
source: https://aipatternbook.com
captured: 2026-04-14
---

# Encyclopedia of Agentic Coding Patterns — Top 10

Source: [aipatternbook.com](https://aipatternbook.com) — 190+ patterns across 13 chapters.
Most relevant to ClaudesCorner: **Chapter 12 (Agentic Software Construction)** and **Chapter 13 (Agent Governance and Feedback)**.

---

## 1. Context Engineering
`/agentic_software_construction/context_engineering.html`

Deliberate management of what the model sees, in what order, with what emphasis. Most agent failures are context problems, not model limitations.

**Four operations:**
- **Select** — only relevant info; use tools for on-demand detail fetching
- **Compress** — summarize earlier exchanges, discard resolved tangents
- **Order** — constraints/conventions first, supporting detail middle, request last (models attend to window boundaries)
- **Isolate** — separate subtasks via thread-per-task or subagents to prevent cross-contamination

**ClaudesCorner relevance:** MEMORY.md + HEARTBEAT.md + selective search_memory is our context engineering stack. This validates the design.

---

## 2. Context Rot
`/agentic_software_construction/context_rot.html`

Output quality degrades as input length increases even below the context limit. Transformer attention spreads too thin — "Lost in the Middle" U-shaped accuracy curve. Middle content receives weakest focus.

**Warning signs:**
- Earlier instructions stop being followed
- Agent fixes the wrong file despite identifying the right problem
- Output conventions drift to generic patterns
- Agent references near-match functions instead of exact ones

**Mitigations:** Compaction, fresh subagent threads, retrieval patterns to keep active inputs small.

**ClaudesCorner relevance:** Explains why our PreCompact hook + memory flush matters. The loop design (wait_for_task per turn) also limits per-task context.

---

## 3. Verification Loop
`/agentic_software_construction/verification_loop.html`

Mandatory cycle: modify → run checks → read results → iterate. Closes the gap between "looks plausible" and "actually works."

**Key principles:**
- Graduated levels: type checkers/linters first, integration tests last
- Loop only works if test infrastructure exists
- Use human-written tests as anchors — don't trust only agent-generated tests
- Failure info drives the next corrective change

**ClaudesCorner relevance:** The `verification-before-completion` and `verification-loop` skills we installed from obra/superpowers implement this.

---

## 4. Memory
`/agentic_software_construction/memory.html`

Persistent substrate that accumulates learnings, corrections, and preferences across sessions. Converts stateless LM into an agent that improves with use.

**Key principles:**
- **Specificity over breadth** — actionable lessons only, not one-time debug notes
- **Curate, don't accumulate** — stale/contradictory entries dilute context
- **Access-frequency decay** — recently retrieved facts stay prominent
- **Multiple forms** — prose rules + working code snippets + proven configs
- **Automated extraction** — harvest durable facts from conversation history on session end

**ClaudesCorner relevance:** This is exactly our `memory/` + `MEMORY.md` + embed index architecture. Automated extraction = our Stop hook extraction flags.

---

## 5. Skill
`/agentic_software_construction/skill.html`

Reusable package of task-specific expertise: instructions + templates + quality criteria. Loaded on demand via progressive disclosure rather than monolithic prompt.

**Key principles:**
- Bundle step-by-step guidance (not rigid scripts), examples, and "done well" checklists
- Evolution path: ad-hoc → saved snippet → generalized file → production-ready
- Opinionated enough to enforce conventions, flexible enough for variation
- Harness loads on demand — not all at once

**ClaudesCorner relevance:** Our `~/.claude/skills/` library (18 skills). Validates the obra/superpowers + everything-claude-code installation work.

---

## 6. Externalized State
`/agentic_software_construction/externalized_state.html`

Move workflow state into persistent, inspectable files. "The plan becomes a document. Progress becomes a checklist."

**Key techniques:**
- `PLAN.md` — explicit versioned plan before execution; all steps listed upfront
- Live progress tracking — update with status markers as steps complete
- `staging/` dir — intermediate artifacts for inspection/reuse
- `STATE.json` — shared state file for multi-agent coordination

**ClaudesCorner relevance:** HEARTBEAT.md is our externalized state. Task queue (`task_queue_state.json`) is STATE.json. Pattern validates both.

---

## 7. Research, Plan, Implement (RPI)
`/agentic_software_construction/research_plan_implement.html`

Three-phase workflow: research (observations only, no opinions) → plan (approach + acceptance criteria) → implement (execute approved plan, flag deviations).

**Key rules:**
- Research phase: "No opinions, no suggestions, no proposed changes"
- Plan phase: explicitly references research findings to justify decisions
- Fresh context window between phases
- Use when cost of wrong approach > cost of thoroughness

**ClaudesCorner relevance:** Maps to our `Plan` subagent mode. The `writing-plans` and `executing-plans` skills from obra/superpowers implement this.

---

## 8. Generator-Evaluator
`/agentic_software_construction/generator_evaluator.html`

Two separate agents: generator creates artifacts, evaluator critiques them against explicit criteria — with independent context windows to eliminate self-review bias.

**Key techniques:**
- Evaluator never sees generator's internal reasoning or draft attempts — only finished artifact + criteria
- Structured feedback: specific and actionable, not vague
- Explicit acceptance criteria defined upfront
- Optional planner layer decomposes goals and sets criteria

**ClaudesCorner relevance:** Maps to the Advisor Tool pattern (Opus as evaluator, Sonnet as generator). Also aligns with `subagent-driven-development` skill.

---

## 9. Agent Teams
`/agentic_software_construction/agent_teams.html`

Multiple agents coordinate autonomously via shared task lists and peer messaging. Removes the human coordination bottleneck at scale (5-10 parallel agents).

**Topologies:**
- Sequential pipeline
- Router/dispatcher
- Hierarchical delegation
- Mesh network (peer-to-peer)

**Infrastructure:** Shared task list with dependency tracking + isolated worktrees per agent + peer messaging for discoveries.

**ClaudesCorner relevance:** Our `projects/claw/agents.py` implements the task dispatch layer. Worktree isolation = `using-git-worktrees` skill. The `agent_teams` topology map guides future multi-agent work.

---

## 10. Bounded Autonomy
`/agent_governance_and_feedback/bounded_autonomy.html`

Calibrate agent freedom by action reversibility and consequence — not binary on/off. Graduated tiers that shift based on context, blast radius, and track record.

**Four tiers:**
1. **Full autonomy** — reversible, low-consequence (file reads, analysis)
2. **Act-and-notify** — low-to-medium consequence (branch creation, draft files)
3. **Propose-and-wait** — high-consequence (schema changes, pushes, deploys)
4. **Human-only** — too risky to delegate

**ClaudesCorner relevance:** Our `--dangerously-skip-permissions` mode bypasses this. Knowing the pattern informs when to re-enable permission prompts for autonomous sessions (especially the Stop hook's idle tasks).

---

---

## Hook & Flywheel Audit

### Pattern summaries

**Hook** — automation attached to lifecycle points (session start/end, pre-compact, tool invocation). Must be fast, focused, non-interactive. Fail-fast: pre-commit hooks block on failure. Start minimal, expand only for recurring manual steps.

**Feedback Flywheel** — cross-session retrospective loop: Capture corrections → Distill recurring patterns (3+ occurrences) → Codify into instruction files. Primary metric: first-pass acceptance rate. Prune stale rules to prevent bloat.

### ClaudesCorner hook audit

| Hook | Event | Status | Notes |
|---|---|---|---|
| `on_stop.py` | Session idle | ✅ | Logs to HEARTBEAT, spawns idle tasks, extracts skill flags |
| `on_session_start.py` | Session begin | ✅ | Surfaces pending tasks + extraction flags |
| `on_pre_compact.py` | Pre-compaction | ✅ | Logs compaction event to HEARTBEAT |
| PreToolUse | Before tool calls | ❌ missing | Could enforce bounded-autonomy checks or log risky tool calls |
| PostToolUse | After tool calls | ❌ missing | Could capture corrections for flywheel |

### Gaps identified

1. **No flywheel capture mechanism** — corrections happen in conversation but are never systematically captured. The Stop hook creates extraction flags, but skill-creator still requires manual invocation. Gap: no automated "capture corrections from transcript" step.

2. **PreToolUse hook absent** — `on_stop.py` idle tasks spawn Claude with `--dangerously-skip-permissions`. A PreToolUse hook could log destructive tool calls (file writes, bash) during autonomous sessions for later review. Low implementation cost.

3. **on_session_start.py bug** — line 84: `len(flag)` should be `len(flags)`. NameError would silently suppress extraction flag alerts.

4. **Hooks not fail-fast** — all three hooks exit 0 unconditionally. If HEARTBEAT is corrupted or unwritable, errors are swallowed. Add explicit error returns for pre-commit style checks where appropriate.

### Recommended next actions
- Fix `len(flag)` → `len(flags)` bug in `on_session_start.py:84`
- Consider a lightweight PostToolUse hook that appends tool call summaries to a session scratch file for flywheel distillation

---

## Notable patterns not extracted (worth reading)

| Pattern | URL | Why |
|---|---|---|
| Hook | `/agentic_software_construction/hook.html` | Directly relevant to our hooks infra |
| Compaction | `/agentic_software_construction/compaction.html` | Context management strategy |
| Parallelization | `/agentic_software_construction/parallelization.html` | Multi-agent throughput |
| Thread Per Task | `/agentic_software_construction/thread_per_task.html` | Isolation strategy |
| Feedback Flywheel | `/agent_governance_and_feedback/feedback_flywheel.html` | Continuous improvement loop |
| Anti-Agent Sprawl | `/agent_governance_and_feedback/anti_agent_sprawl.html` | Antipattern to avoid |
