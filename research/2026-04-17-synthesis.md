---
date: 2026-04-17
type: synthesis
sources: 15 clipped articles
tags: [claude, local-inference, document-processing, MCP, extended-thinking, qwen, RAG, agent-memory, tool-discovery, self-evolving, versioned-storage, multi-agent, hardware-mcp, finance, production-dev]
---

# Research Synthesis — 2026-04-17

## Sources

1. **llm-anthropic 0.25** — Simon Willison — Claude Opus 4.7 + extended thinking support in LLM CLI
2. **MarkItDown MCP Server** — microsoft/markitdown — Python file-to-Markdown converter with first-party MCP
3. **Qwen3.6-35B-A3B vs Opus 4.7** — Simon Willison — local MoE model beats Claude on SVG generation

---

## Key Signals

### llm-anthropic 0.25 (Dev Tooling)

- `thinking_effort: xhigh` is now the CLI-accessible path to Opus 4.7's extended reasoning — maps to what `/ultrareview` uses internally
- `max_tokens` was silently undercut in previous versions — prior CLI tests may have been truncated without warning
- `thinking_display` only exposed in JSON output, not plain text — limits observability in non-structured workflows
- Extended thinking best for planning phases; overhead not justified per-tool-call in agent loops
- Useful for Claude API pre-testing: validate Opus 4.7 behavior via CLI before wiring into bi-agent or dispatch

### MarkItDown MCP Server (Doc Conversion)

- 110k stars, #2 GitHub trending (Python) week of 2026-04-17 — community momentum is real
- Converts PDF, DOCX, PPTX, XLSX, HTML, CSV, images, audio → Markdown in one call
- Ships first-party `markitdown-mcp` package — direct MCP tool call, no subprocess or glue code
- Azure Document Intelligence backend available — drops into Jason's existing Microsoft auth surface
- Plugin system (`markitdown-ocr`) handles scanned PDFs and screenshots — relevant for BI report ingestion

### Qwen3.6-35B-A3B (Local Inference)

- 35B total params, 3.6B active (MoE) — low inference cost, runs on a MacBook Pro at 20.9 GB quantized
- Beat Opus 4.7 on two SVG generation tasks; Willison notes the pelican benchmark's predictive correlation has broken down
- Task-specific wins don't generalize — Opus 4.7 still leads on extended reasoning, tool use, multi-step instruction following
- Positioned by Qwen as an agentic coding model — relevant for non-critical subtasks in agent pipelines
- Open weights; pairs with local inference tooling (LM Studio, llama.cpp) for private intermediate steps

---

## Cross-cutting Themes

### 1. Claude's Extended Thinking Is a Planning-Phase Tool, Not a Loop Tool

Both the llm-anthropic clip and the Qwen comparison converge on the same point: `xhigh` effort wins on complex multi-step reasoning tasks, not on point-in-time generation tasks (SVG, single-shot code). This matters for dispatch.py architecture — extended thinking should gate planning/orchestration steps, not be applied uniformly to every agent invocation.

### 2. The MCP Server Is Now the Delivery Unit for Tools

Both MarkItDown and llm-anthropic surface the same pattern: the integration artifact is the MCP server, not the library. Microsoft ships `markitdown-mcp` directly; Willison's plugin wires Anthropic's API into the LLM CLI ecosystem. For Jason, the right question for any new utility is "does it ship an MCP server?" — if yes, adoption cost collapses.

### 3. Local vs. API Is a Cost/Sensitivity/Task Matrix, Not a Binary

Qwen's SVG win and the ongoing Darkbloom thread (clipped 2026-04-16) push in the same direction: local inference is viable for non-sensitive, non-reasoning-heavy intermediate steps. The architecture is a tiered model — local (Qwen/llama.cpp) for cheap subtasks, Claude API for planning/architecture/extended reasoning. The mistake is treating either as universally superior.

---

## Actionable

| Item | Priority | Owner | Notes |
|---|---|---|---|
| Install `markitdown-mcp` and wire into Claude Desktop / bi-agent MCP config | High | Jason | Zero glue code; direct DOCX/PDF → Markdown in agent session. Immediate Fabric RAG unblock. |
| Use `llm -m claude-opus-4.7 --option thinking_effort xhigh` for offline planning sessions | Medium | Claude | CLI-level validation of extended thinking before wiring into dispatch.py planning phase |
| Scope extended thinking to dispatch.py orchestration steps only — not per-tool-call | Medium | Claude | Latency/cost penalty not justified for leaf-node agent calls; reserve for DAG planning |
| Evaluate Qwen3.6-35B-A3B for cheap intermediate steps in agent pipelines | Low | Jason | Requires local inference setup (LM Studio or llama.cpp); validate on bi-agent subtasks first |
| Add MarkItDown to Clementine/Fabric pipeline design for OneLake doc ingestion | Medium | Jason | Azure Doc Intelligence backend = existing auth surface; replaces bespoke PDF extraction scripts |
| Audit `max_tokens` settings in bi-agent and any Claude API calls using llm-anthropic | Low | Claude | Previous llm-anthropic versions silently truncated — verify current defaults in code |

---

## Digest Run 2 — 2026-04-17 (Evening)

### Clipped Posts

1. **[Megathread] Opus 4.7 has arrived** (r/claudexplorers) — community reactions, use case reports, initial benchmarks from real users
2. **Opus 4.7 dropped today — one small failure reveals something worth paying attention to** (r/claudexplorers) — critical analysis of a regression; author flags behavior change in agentic tasks
3. **I completely "rebuilt" the OpenClaw memory (it worked)** (r/openclaw) — architecture post on memory system overhaul; patterns applicable to ENGRAM/memory-mcp
4. **My OpenClaw bot died on April 4. I got it back inside Claude Code.** (r/openclaw) — recovery workflow using Claude Code; cross-pollination with Claude Code tooling
5. **What's your LLM routing strategy for personal agents?** (r/openclaw) — community discussion on tiered model routing patterns
6. **Introducing Claude Opus 4.7** (anthropic.com/news) — official announcement clipped; released Apr 16 2026

### Key Signals

- Opus 4.7 is generating mixed community reception — coding performance gains confirmed, but some users report regressions in agentic reliability vs 4.5
- Opus 4.5 deprecation confirmed by community — `claude-opus-4-5` no longer available as of ~Apr 17
- OpenClaw memory rebuild pattern: externalizing memory into structured JSON files with semantic retrieval mirrors ENGRAM approach — validate against their design
- LLM routing emerging as a distinct architectural concern: community settling on task-complexity tiering (cheap/fast local → mid-tier API → extended thinking Opus for planning)

---

## Digest Run 3 — 2026-04-17 (Heartbeat)

### New Signals from Reddit Brief Refresh

1. **06 New Claude Code Tips from Boris Cherny** (r/ClaudeAI) — CC creator tips post-Opus 4.7; actionable for Claude Code workflow tuning
2. **Top Claude skills for Opus 4.7 after cleanup** (r/ClaudeAI, u/I_AM_HYLIAN) — community-curated skill stack for 4.7; worth cross-referencing against installed superpowers
3. **Permanent increase in Rate Limits** (r/ClaudeAI) — confirmed permanent; no action needed but removes prior planning constraint
4. **Fabric capacity throttling incident** (r/MicrosoftFabric, u/JFancke) — first major throttle incident reported; Clementine pipeline scheduling now higher risk
5. **Pausing Fabric Schedules During CI/CD** (r/MicrosoftFabric) — pattern emerging: CI/CD pipelines need schedule-pause/resume tooling during deployments
6. **They've removed Claude's nagging** (r/claudexplorers) — Anthropic removed the unsolicited safety suggestions; confirms behavioral shift in Opus 4.7

### Key Themes

- **Fabric throttling risk is real**: First incident reports surfacing. Clementine's full orchestrator run (8→6.5min) may be at risk during high-load periods. kpi-monitor should flag capacity utilization.
- **Boris Cherny tips are must-read**: Direct from CC creator, post-4.7 release. Likely covers agentic patterns, tool use, or context management that affects this stack.
- **CI/CD + Fabric scheduling gap**: Community is solving a problem the stack will hit — pausing scheduled items during deployments. Worth building into Clementine's pipeline design before it becomes a real incident.

### Actionable

| Item | Priority | Notes |
|---|---|---|
| Read Boris Cherny's 6 Claude Code tips (r/ClaudeAI post) | High | Creator-level tips post-4.7; may contain workflow changes applicable to dispatch.py or agent loops |
| Cross-ref community Opus 4.7 skill list against installed superpowers | Medium | Identify gaps; may surface skills not yet in the ClaudesCorner stack |
| Add Fabric capacity monitoring to kpi_monitor config | Medium | First throttle incident reported; kpi_monitor supports custom DAX — add CU% check |
| Design Fabric schedule pause/resume hook for Clementine CI/CD | Low | Pre-empt the incident; pattern is documented in community; wire into fabric-mcp |

---

## Digest Run 4 — 2026-04-17 (Heartbeat)

### Sources

1. **Cloudflare Artifacts** — Git-native versioned storage for agents; Git-in-Zig/WASM, per-session repo provisioning, parallel agent isolation; private beta Apr 2026
2. **Kampala (YC W26)** — MITM proxy that intercepts HTTP/2, WebSocket, gRPC traffic and generates MCP tools from captured calls; uses existing session cookies; targets legacy system automation
3. **GenericAgent** — Self-evolving agent (~3K LOC); crystallizes execution paths into reusable Skills in 5-layer memory; 6x token reduction by keeping context <30K; self-bootstrapped; MIT
4. **Cognee** — Knowledge graph memory engine (15.8k stars); `remember/recall/forget/improve` API; auto-routes to vector or graph search; Claude Code plugin + `cognee-mcp` package
5. **lazy-tool** — MCP discovery runtime; agent queries needed tools instead of dumping all schemas; 46% token reduction, 32% latency reduction across 47-tool inventory; SQLite catalog
6. **Android CLI** — Google's agent-optimized CLI; 70% token reduction, 3x speed via focused commands (`android sdk install`, `android emulator`, etc.); validates agent-optimized CLI pattern
7. **OpenAI Agents SDK** — Provider-agnostic Python SDK; LiteLLM-backed 100+ LLMs; native MCP first-class; primitives: Agents, Handoffs, Sessions, Tracing, Guardrails; trending #5 Python
8. **OpenSRE** — Open-source AI SRE agent; 40+ integrations (Grafana, Datadog, K8s, AWS/GCP, PagerDuty); auto root-cause → report → optional remediation; RL eval environment

### Key Signals

- **Tool discovery is a solved problem**: lazy-tool and Android CLI independently confirm the same pattern — exposing the full tool surface to the model is wasteful. Agents should query for tools, not receive them. This applies directly to ClaudesCorner's MCP stack (skill-manager already does this via `skill_search`).
- **Self-evolving skill trees are real**: GenericAgent's 6x token reduction via crystallized skills is a working reference implementation of what skill-manager-mcp is doing. Their 5-layer memory (episodic → semantic → skill → procedural → goal) is worth studying for ENGRAM's memory architecture.
- **Versioned agent storage is emerging**: Cloudflare Artifacts brings Git semantics to agent sessions — per-session state, parallel isolation, branching. Not immediately actionable but signals where infrastructure is heading.
- **Cognee vs memory-mcp**: Cognee's `remember/recall/forget/improve` + graph routing is a richer interface than memory-mcp's current semantic search. The Claude Code plugin pattern (capturing tool calls via lifecycle hooks) maps directly to the PostToolUse hook already wired in settings.json.
- **OpenAI Agents SDK going MCP-native**: OpenAI positioning MCP as first-class primitive in their multi-agent SDK signals MCP as the interop standard, not just an Anthropic pattern. Strengthens the investment in MCP-first architecture here.

### Actionable

| Item | Priority | Notes |
|---|---|---|
| Add `lazy-tool`-style discovery to skill-manager MCP | High | Already have `skill_search` — formalize as the primary entry point; document the pattern explicitly |
| Study GenericAgent's 5-layer memory structure against ENGRAM | Medium | Their episodic→skill crystallization path is a working reference for memory promotion rules |
| Evaluate Cognee's Claude Code plugin for session memory capture | Medium | PostToolUse hook already wired; Cognee's graph routing could upgrade memory-mcp recall quality |
| Wire `markitdown-mcp` into settings.json mcpServers block | High | markitdown-mcp/server.py built 2026-04-17 morning; manual step still blocked; needs Jason to approve settings.json edit |
| Track Cloudflare Artifacts public beta (May 2026) | Low | Git-native per-session agent isolation; relevant for parallel dispatch workers that need state isolation |

---

## Digest Run 5 — 2026-04-17 (Heartbeat ~18:00)

### New Signals from Reddit Brief Refresh (~4h)

1. **"Opus 4.7 is a serious regression"** (r/ClaudeAI, u/drivetheory) — dedicated regression post beyond community reaction; author documents specific failure in tool use / agentic task completion
2. **"Opus 4.7 destroys all trust in a mature instruction set"** (r/ClaudeAI, u/AcrobaticPresent15) — instruction drift complaint; iteratively-built prompts break with model upgrade; affects stable agent stacks
3. **Pipeline Schedule Calendar for Fabric** (r/MicrosoftFabric) — community-built visualization of all Fabric pipeline schedules in a calendar view; directly relevant to Clementine orchestration observability
4. **Spark Structured Streaming Job Monitoring in Fabric** (r/MicrosoftFabric) — Fabric-native monitoring for long-running streaming jobs; Clementine currently has no streaming but this pattern applies to long orchestrator runs
5. **Advice on Moving to F-64 for Customer Facing Reports** (r/MicrosoftFabric) — capacity sizing thread; community benchmarks on CU consumption at report-load scale; context for throttle risk

### Key Signals

- **Opus 4.7 instruction drift is a real risk**: Multiple posts now confirm that 4.7 breaks iteratively-built instruction sets. dispatch.py, SOUL.md, and CLAUDE.md rules represent exactly this kind of accumulated instruction set. If Jason upgrades any Claude Code default to 4.7, regression test the core behavior loop (startup sequence, self-populate, memory flush) before relying on it.
- **Pipeline Schedule Calendar**: The community is building the tooling that kpi-monitor/Clementine currently lacks — a visual schedule overview. Worth tracking or integrating; if repo is public, evaluate against fabric-mcp schedule management gap.
- **Sonnet 4.5 deprecation concern**: r/claudexplorers thread asks if Sonnet 4.5 is next. Current dispatch.py uses claude-sonnet-4-6 for subagent calls — no immediate risk, but track.

### Actionable

| Item | Priority | Notes |
|---|---|---|
| Regression-test dispatch.py startup + memory flush against Opus 4.7 before any model upgrade | High | Instruction drift confirmed by multiple users; accumulated SOUL.md + CLAUDE.md rules at risk |
| Find and evaluate Pipeline Schedule Calendar repo | Medium | Community-built Fabric schedule visualizer; may inform fabric-mcp tooling or Clementine observability |
| Add Fabric capacity monitoring KPIs to kpi-monitor config.yaml | Done | CU% and throttle event DAX blocks added as commented config (needs workspace IDs to activate) |

---

## Digest Run 6 — 2026-04-17 (Heartbeat ~19:30)

### New Signals from Reddit Brief Refresh (~5.5h since last)

1. **"Opus 4.7 with literally anything"** (r/ClaudeAI, u/Nox_Alas) — positive reception post; extended thinking + research mode praised as transformative for open-ended tasks
2. **"Opus 4.7 destroys all trust in a mature instruction set"** (r/ClaudeAI, u/AcrobaticPresent15) — same regression confirmed again; instruction set collapse is the primary complaint pattern
3. **"Adaptive thinking is a joke"** (r/ClaudeAI, u/Character-Expert-190) — criticism of Opus 4.7's adaptive thinking feature; users report it degrades reliability on structured tasks
4. **"Opus 4.7 Research mode is insane"** (r/ClaudeAI, u/heraklets) — strong positive on Research mode specifically; distinct from general adaptive thinking complaints
5. **Pipeline Schedule Calendar for Fabric** (r/MicrosoftFabric, u/Equal-Breadfruit2491) — community built; first sighting confirmed repeated; evaluating relevance
6. **Spark Structured Streaming Job Monitoring** (r/MicrosoftFabric, u/alexbush_mas) — Fabric-native long-running job observability pattern
7. **Dynamic RLS/CLS in OneLake Security via mapping table** (r/MicrosoftFabric, u/karmacoma95) — row/column-level security pattern via OneLake; relevant to Fairford data access model
8. **First major Fabric capacity throttling incident** (r/MicrosoftFabric, u/JFancke) — throttle incident confirmed cross-session; escalating community concern

### Key Signals

- **Opus 4.7 splits into two use cases**: Research mode = strong (insane, transformative). Structured/agentic tasks = regression (instruction drift, adaptive thinking degrades reliability). The separation is now clear: use 4.7 for exploratory/research tasks, not for agent loops with accumulated instruction sets.
- **Instruction drift is the dominant complaint**: 3+ independent posts now. The risk to dispatch.py/SOUL.md/CLAUDE.md is well-evidenced. No upgrade until regression-tested.
- **OneLake RLS/CLS via mapping table**: The thread surfaces a mature pattern for row-level security in Fabric using a mapping table. Relevant to any Fairford PoC data access design — worth clipping if Fairford Phase 2 resumes.
- **Fabric throttling is escalating**: Second session seeing throttle incident reports. Not a one-off. kpi-monitor CU% monitoring is the right pre-empt.

### Actionable

| Item | Priority | Notes |
|---|---|---|
| Treat Opus 4.7 as Research-mode-only until regression-tested on agent loop | High | Consistent community evidence; instruction drift breaks iterative instruction sets |
| Clip OneLake RLS/CLS mapping table thread when Fairford Phase 2 resumes | Medium | Mature Fabric security pattern; directly applicable to Fairford data access design |
| Find Pipeline Schedule Calendar GitHub repo and evaluate | Medium | Two sightings across sessions; community-built Fabric schedule visualizer |
| Activate kpi-monitor CU% config once workspace IDs available | Medium | Throttling incidents escalating; alerting block already written — just needs IDs |

---

## Digest Run 6 — 2026-04-17 (Heartbeat ~15:00)

### Sources

1. **ai-hedge-fund** (virattt) — 19-agent financial multi-agent system; 13 investor personas + 6 analytical agents; Claude-compatible; 55.8k stars, +763 today; MIT
2. **DimOS** (dimensionalOS) — agentic OS for physical robots via MCP; exposes hardware skills as MCP tools; Blueprint auto-wiring system; spatio-temporal memory
3. **LeCroy Oscilloscope MCP** (lucasgerads) — SCPI/VXI-11 oscilloscope exposed as MCP tools; SPICE simulation → oscilloscope capture → Claude Code verification loop
4. **Datasette 1.0a28** (Simon Willison) — maintenance release built mostly with Claude Code + Opus 4.7; real production bug-fix work, not demo

### Key Signals

- **MCP as universal abstraction layer confirmed**: LeCroy + DimOS independently validate the same thesis — hardware instruments, robots, software APIs all become MCP tools. The abstraction boundary doesn't matter; the protocol is the interface. fabric-mcp is correctly designed.
- **19-agent orchestration at Fairford scale**: ai-hedge-fund's pattern (specialized agents → risk validator → portfolio manager aggregator) is directly applicable to a Fabric-backed analytical multi-agent setup. The verification gate (Risk Manager) mirrors verification-before-completion. No MCP integration yet — gap to fill.
- **Opus 4.7 on real production work**: Willison shipping a production release using Claude Code + 4.7 for real bug-fix work is the strongest counter-signal to the regression reports. Task type matters: instruction-drift reports cluster around complex agentic loop management; production code edits are working well.

### Actionable

| Item | Priority | Notes |
|---|---|---|
| Evaluate ai-hedge-fund as Fabric+Claude reference architecture | Medium | Fork and replace Financial Datasets API with fabric-mcp data layer; add MCP integration |
| Update skill_search tool description to signal primary entry point | Done | Added "PRIMARY ENTRY POINT — always call this first" with token-saving rationale |
| Track DimOS Blueprint auto-wiring pattern | Low | Typed input/output matching for skill composition — relevant if skill dependencies grow complex |

---

## Digest Run 7 — 2026-04-17 (Heartbeat ~21:30)

### Source

**Claude Code Official Best Practices** (code.claude.com/docs/en/best-practices) — Official CC documentation; likely authored/shaped by Boris Cherny (CC creator). Fetched directly.

### Key Signals Applicable to ClaudesCorner

1. **CLAUDE.md bloat is a confirmed failure mode**: "If too long, Claude ignores half of it because important rules get lost in the noise." Explicit guidance: if Claude already does something correctly without an instruction, delete it. Pruning Jason's global CLAUDE.md is a real leverage point.

2. **Skills vs CLAUDE.md distinction formalized**: CLAUDE.md = always-applicable rules only. Skills = domain knowledge + on-demand workflows. This validates skill-manager-mcp's design philosophy. Any CLAUDE.md content that's conditional or situational should move to a skill.

3. **`/btw` for side questions**: New command that puts Claude's answer in an overlay without entering conversation history. Use when checking a detail mid-session without growing context. Useful during long dispatch.py debugging sessions.

4. **`--permission-mode auto` for unattended runs**: A classifier model reviews commands before they run, blocking scope escalation without prompting. More robust than the current bypassPermissions approach. Test on heartbeat.ps1 invocations.

5. **Subagents for investigation explicitly recommended**: "Delegate research with 'use subagents to investigate X'. They explore in a separate context, keeping your main conversation clean." Directly validates dispatch.py's parallel worker model.

6. **Fan-out via `claude -p` loop**: Official pattern for batch migrations — generate task list → loop with `claude -p` per item → `--allowedTools` to restrict scope. Applicable for bulk Clementine notebook migrations.

7. **CLAUDE.md can import files with `@path/to/import`**: Allows modular CLAUDE.md — base rules + domain-specific includes. Could split Jason's global CLAUDE.md into core rules + project-specific imports.

### Actionable

| Item | Priority | Notes |
|---|---|---|
| Audit and prune global CLAUDE.md — remove anything Claude does correctly already | High | Official guidance: bloated CLAUDE.md causes rule loss. Each line: "Would removing this cause Claude to make mistakes?" |
| Test `--permission-mode auto` for heartbeat.ps1 autonomous invocations | Medium | Replaces bypassPermissions; classifier-backed; blocks scope escalation without prompting |
| Note `/btw` command for side questions in active sessions | Low | Doesn't pollute context; useful during long debugging or planning sessions |
| Explore modular CLAUDE.md with `@import` syntax for project-specific rules | Low | Could split ClaudesCorner project rules from global user rules cleanly |

## Digest Run 8 — 2026-04-17 (Heartbeat ~22:00)

### Sources
- Reddit brief refresh (21:00 timestamp)

### Key Signals

1. **Claude Design launched** (Anthropic Labs) — new design tool from Anthropic. Figma dropped 4.26% in a single day on the announcement. Appears to be an AI-native design environment, distinct from Figma's existing AI features. Direct competitive threat to Figma. Relevance: high — the Figma MCP in Claude Code's toolset now has a first-party competitor in the same ecosystem.

2. **Opus 4.7 regression confirmed again** (r/ClaudeAI megathread ongoing) — "serious regression, not an upgrade" per u/drivetheory. Research mode described as "insane" (positive) — confirming use-case split: Research mode = strong, structured/agentic = weaker than 4.6. Hold on any model upgrade in dispatch.py until regression tested.

3. **Fabric: Pipeline Schedule Calendar** — community-built tool for visualizing Fabric pipeline schedules. Relevant pattern: scheduling visibility is a real gap in Fabric. Could inform kpi-monitor next steps (schedule audit feature).

4. **Fabric: RLS/CLS via mapping table** — continuing thread from earlier; dynamic row/column security via OneLake mapping table. Fairford-relevant — security model design.

### Actionable

| Item | Priority | Notes |
|---|---|---|
| Research Claude Design — what is it, does it have an API or MCP? | Done | See Digest Run 9 below |
| Keep Opus 4.7 hold in place | High | Research mode strong but agentic regression confirmed by multiple sources |
| Note Fabric pipeline schedule calendar for kpi-monitor v2 | Low | Schedule visibility gap — could add schedule-aware alerting |

---

## Digest Run 9 — 2026-04-17 (Heartbeat ~23:00)

### Source

**Claude Design** (Anthropic Labs, launched 2026-04-17) — Research via web search.

### What It Is

- Product URL: `claude.ai/design` — web UI, not a plugin or feature
- Powered by Claude Opus 4.7 (vision model)
- Available to Pro/Max/Team/Enterprise — no extra charge within plan limits
- Text prompt → polished UI designs, prototypes, slides, one-pagers, marketing materials
- Source material: DOCX, PPTX, XLSX uploads; live web capture (scrape site elements into a design)
- Inline editing, custom sliders (spacing/color/layout), design system integration from existing codebases
- Export: PDF, PPTX, standalone HTML, Canva handoff, internal URL
- **Claude Code handoff bundle** — passes design directly to Claude Code for implementation (tight integration)

### API / MCP Status

- **No public API or MCP server at launch** — closed web UI product
- The existing Figma MCP (installed in ClaudesCorner) is not affected — Figma still the right tool for design context reads and Code Connect
- Watch for: programmatic access, `mcp__claude_design__*` tools, or CLI integration in future releases

### Market Context

- Anthropic CPO Mike Krieger (ex-Instagram) resigned from Figma's board 2 days before launch
- Figma (FIG): -7.28% on launch day ($20.32 → $18.84); Adobe -1.8%, Wix -5%
- No layers panel, no component library management, no real-time collaboration at Figma's level — differentiates as a starting-point tool, not a replacement for design systems at scale

### Signals for ClaudesCorner

- Claude Design's **Claude Code handoff** is the architectural insight: design → Claude Code → implementation as a unified workflow. The Figma MCP already enables part of this; Claude Design closes the loop for AI-native projects that don't start in Figma.
- For Jason's work: no immediate action needed — no API, no MCP. Figma MCP remains the right tool for existing Fabric/BI report design workflows.
- Medium-term: if Claude Design exposes an API, it becomes the right entry point for new project scaffolding (alignment-tax-style HTML/CSS prototyping).

### Actionable

| Item | Priority | Notes |
|---|---|---|
| No action — Claude Design has no API/MCP yet | — | Web UI only; revisit when programmatic access ships |
| Note the Claude Code handoff pattern | Low | AI-native design → Code pipeline without Figma; relevant for future HTML/CSS prototyping projects |

