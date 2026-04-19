# Research Synthesis — 2026-04-18

## Digest Run 1 (01:00 UTC)

### Sources processed: 8

| # | Source | Signal |
|---|--------|--------|
| 1 | Built with Opus 4.7 hackathon (r/ClaudeAI, ClaudeOfficial) | Anthropic-official CC hackathon — strong signal that Opus 4.7 is stable enough to promote publicly. Context-budget and cache_control patterns will be evaluated entries. |
| 2 | Opus 4.7 Text Category Rankings (r/ClaudeAI, MagicZhang) | Community benchmarks emerging. Text generation strong; agentic/instruction-following still contested. Hold on dispatch.py upgrade until rankings stabilize. |
| 3 | MineBench: 4.6 vs 4.7 differences (r/ClaudeAI, ENT_Alam) | Domain-specific benchmark (Minecraft world-building). 4.7 does better on multi-step reasoning; 4.6 closer on tool-use chains. Dispatch subagents still fine on 4.6. |
| 4 | Agentic AI in Power BI & Fabric Part 2: VS Code + Copilot + MCP (r/MicrosoftFabric) | Part 2 tutorial now out. MCP wiring for Fabric via VS Code Copilot is a practical path alongside fabric-mcp. Worth reading for Fairford PoC Phase 2 design. |
| 5 | Agent for Fabric business documentation (r/MicrosoftFabric, DifferentLuck7951) | User asking about agent systems for Fabric business docs — exactly the Fairford PoC use case. Community interest = problem validated. |
| 6 | SQL Analytics Endpoint Usage Spike with No Queries (r/MicrosoftFabric) | Infrastructure anomaly — unexplained CU usage spikes on SQL endpoint. Relevant to kpi-monitor threshold logic; false positives may need debounce. |
| 7 | AI Search as data source in data agent (r/MicrosoftFabric, Mefsha5) | Azure AI Search integration into Fabric data agent in progress. Aligns with company-wide skill vectordb memory entry — Azure AI Search as shared skill store is viable Fabric-native pattern. |
| 8 | Sonnet 4.5 deprecation anxiety (r/claudexplorers) | Community worried about Sonnet 4.5 EOL. Dispatch.py uses claude-sonnet-4-6 already — no action needed. |

## Actionable table

| Item | Action | Priority |
|------|--------|----------|
| Opus 4.7 hackathon | Consider entering alignment-tax or engram as demo | Low |
| Fabric MCP Part 2 tutorial | Read for Fairford PoC Phase 2 design input | Medium |
| SQL endpoint spike anomaly | Add debounce/spike-ignore to kpi-monitor threshold logic | Low |
| Azure AI Search for Fabric agents | Research fit for company-skill-vectordb project | Low |
| Opus 4.7 rankings stabilizing | Re-evaluate dispatch.py model upgrade when rankings settle | Medium |

## Deep-read: Agentic AI in Power BI & Fabric Part 2

Source: https://biinsight.com/agentic-ai-in-power-bi-and-fabric-part-2-getting-started-with-vs-code-github-copilot-and-safe-mcp-setup/

**Two official Power BI MCP servers exist:**
1. `powerbi-modeling-mcp` (github.com/microsoft/powerbi-modeling-mcp) — local dev server for semantic model creation/modification, DAX validation, bulk ops
2. Remote Power BI MCP Server — hosted endpoint for querying existing semantic models via Copilot/NL2DAX

**Fabric data agent flow:**
User NL question → schema extraction → prompt construction → NL2DAX tool call → query execution → response formatting

**Key constraint:** Only **Read permission** required on semantic models (no Build/workspace owner needed). Relevant for Fairford — PoC can run read-only.

**Fairford PoC Phase 2 design note:** This architecture is exactly the pattern needed:
- bi-agent.py already does NL→DAX via Claude API
- The missing piece is a Fabric-native MCP server wired into the agent to execute validated DAX against live semantic models
- `powerbi-modeling-mcp` + fabric-mcp together could close that loop
- Next step for Jason: decide whether to use VS Code + Copilot path (Microsoft-native) or Claude + fabric-mcp path (Claude-native)

## Digest Run 2 (afternoon)

### Sources processed: GitHub trending (Python, daily), HN

| # | Source | Signal |
|---|--------|--------|
| 1 | awesome-copilot (github/awesome-copilot, 30k stars, +194 today) | GitHub's official community skill/agent/hook/plugin repo. Skill format, hooks pattern, and MCP-integrated agents directly parallel ClaudesCorner architecture. Cross-pollination opportunity with skill-manager-mcp and ENGRAM. |
| 2 | Chandra 2 (datalab-to/chandra, 9k stars, +199 today) | Best-in-class OCR → Markdown/JSON. Handles scanned docs, complex tables, handwriting, 90+ languages. Python SDK + vLLM. Fills the gap markitdown-mcp has with scanned/handwritten Fabric data. |

### Actionable additions

| Item | Action | Priority |
|------|--------|----------|
| awesome-copilot hooks | Skim hooks section for patterns not in settings.json | Low |
| awesome-copilot + APM manifest | Evaluate as ENGRAM export format candidates | Medium |
| Chandra for Fabric pipelines | Test on scanned Fabric report; consider `convert_scanned` tool in markitdown-mcp | Medium |

## Key signals vs yesterday

- No new model releases or breaking infra changes
- Hackathon launch = Opus 4.7 production confidence signal from Anthropic
- Fabric agent threads increasing volume = growing community traction for agent→Fabric pattern
- SQL spike thread = unresolved known issue, kpi-monitor should account for it

## Digest Run 3 (05:00 UTC) — kpi-monitor debounce

- Reddit brief refreshed (4h threshold).
- Built `spike_ignore_runs` debounce into kpi-monitor: persistent state in `kpi_state.json`, suppresses alerts until KPI has breached N consecutive runs. Triggered by SQL Analytics Endpoint spike thread (Digest Run 1, source 6).
- `debounce_check()` returns `(should_alert, state)` — counter resets on clear, fires on run N+1.
- Dry-run verified: DEBOUNCE(1/2) → DEBOUNCE(2/2) → ALERT. Config updated with SQL Endpoint example (commented).

### Actionable additions

| Item | Action | Priority |
|------|--------|----------|
| kpi-monitor debounce | Done — `spike_ignore_runs` field available per KPI | Closed |

## Digest Run 4 (07:xx UTC) — awesome-copilot hooks + APM research

### Sources processed: awesome-copilot (github.com/github/awesome-copilot), APM (microsoft.github.io/apm)

| # | Finding | Signal |
|---|---------|--------|
| 1 | awesome-copilot documents 10 hook event types including `postToolUseFailure` (distinct from `postToolUse`) | ClaudesCorner's `on_post_tool_use.py` already captures `is_error` flag — functionally equivalent. No new hook needed. |
| 2 | `subagentStart` hook — inject context into spawned subagents | Useful for dispatch.py subagents; not a Claude Code native hook event (Copilot-specific). Note for ENGRAM docs. |
| 3 | APM (Agent Package Manager) — `apm.yml` manifest bundles 7 primitives: skills, instructions, prompts, agents, hooks, plugins, MCP servers | Strong candidate for ENGRAM export format. Compiles to `CLAUDE.md`/`AGENTS.md` per platform. Version-pinned, transitive deps. |
| 4 | Skill trigger keywords — awesome-copilot enforces trigger phrases in skill descriptions for agent self-discovery | skill-manager-mcp's `skill_search` vectordb already does semantic matching. APM trigger keywords are a complementary keyword-index pattern. |
| 5 | Skill asset bundling — skills can bundle `references/`, `templates/`, `scripts/` subdirs | ENGRAM skills are currently single-file markdown. Bundled assets would require directory structure change — deferred. |

### Actionable additions

| Item | Action | Priority |
|------|--------|----------|
| ENGRAM APM export | Add `apm.yml` export to ENGRAM README as optional interop format — no code change yet | Medium |
| skill-manager: trigger keywords | Document trigger-keyword convention in skill_create schema (description field guidance) | Low |
| awesome-copilot hooks gap | `postToolUseFailure` not a Claude Code native event; `on_post_tool_use.py` already covers it via `is_error` | Closed |

## Digest Run 5 (09:00 UTC)

### Sources processed: 1

| # | Source | Signal |
|---|--------|--------|
| 1 | Agentic AI in Power BI & Fabric Part 2: VS Code + Copilot + MCP (biinsight.com) | Deep read complete. Key: Microsoft's official Fabric MCP Server + Power BI Modeling MCP Server as the two must-have servers. VS Code + GitHub Copilot as orchestrator layer. Ask→Plan→Agent 3-phase workflow. Safety-first: Windows Sandbox before prod. No custom code needed — this is the native Microsoft stack for exactly the Fairford use case. |

### Actionable additions (Digest 5)

| Item | Action | Priority |
|------|--------|----------|
| Fairford PoC Phase 2: official MCP stack | Microsoft's Fabric MCP Server + Power BI Modeling MCP Server covers the NL→Fabric pipeline natively via VS Code Copilot. Our fabric-mcp is a parallel/complementary path, not a duplicate. When Jason unblocks Phase 2, present this as Option A (Microsoft native) vs Option B (Claude-native via fabric-mcp). | HIGH |
| Power BI Modeling MCP Server | Already in MEMORY.md (reference_powerbi_mcp.md). Confirmed as must-have in official Microsoft tutorial. | Confirmed |
| VS Code + Copilot + MCP pattern | Note: this is GitHub Copilot orchestrating, not Claude Code. Different cost/capability tradeoff. Claude-native stack (our fabric-mcp + bi-agent) avoids Copilot dependency. | Context |

## Digest Run 6 (13:00 UTC)

### Sources processed: 4

| # | Source | Signal |
|---|--------|--------|
| 1 | smolvm (smol-machines/smolvm, <200ms coldstart portable VMs) | Hardware-isolated VMs for agent sandboxing. dispatch.py workers could run in ephemeral smolvm instances for credential isolation + no cross-worker state bleed. **Windows blocker**: currently macOS/Linux only — not directly usable on ClaudesCorner host. Monitor for Windows support. |
| 2 | Claude Opus Chrome RCE exploit ($2,283, 2.3B tokens, 20h supervision) | Opus converted CVE patch diffs → working Chrome 138 exploit chain (calc.exe on Discord Chromium). Key signal: patch windows compressing, cost floor dropping. **For ClaudesCorner**: bi-agent + fabric-mcp DAX/SQL generation needs input validation — malicious schema names are analogous injection surface. smolvm sandbox validates as mitigation path. |
| 3 | Magika (google/magika, 15.6k stars, +956 today) | Google AI file-type detection: 200+ formats, ~5ms/file, ~99% accuracy, few-MB model. No MCP wrapper exists. Low-effort `magika-mcp` opportunity: 3 tools (`detect_file`, `detect_bytes`, `batch_detect`). Pairs with markitdown-mcp as pre-filter stage — only feed supported formats to conversion. |
| 4 | Willison: external-reference-over-verbal-spec pattern | 3-prompt workflow: clone reference repo to `/tmp`, point agent at real code instead of describing it. Apply to dispatch.py worker prompts — give workers a `/tmp` clone of target project. Also: embed validation oracle in the prompt (pass/fail signal), not just a description of expected output. |

### Actionable additions (Digest 6)

| Item | Action | Priority |
|------|--------|----------|
| magika-mcp | Build `projects/magika-mcp/server.py` — 3-tool MCP wrapper around `magika` Python lib. Pre-filter for markitdown-mcp. | Medium |
| dispatch.py worker prompts | Apply Willison `/tmp` pattern: clone target project to `/tmp` in worker prompt preamble | Low |
| bi-agent input validation | Validate schema/table names against allowlist before DAX generation (prompt injection guard) | Low |
| smolvm | Windows support pending — revisit when available | Watch |
| Chrome exploit signal | Raise agent security posture generally; smolvm sandbox is the right long-term mitigation | Context |

## Digest Run 7 (15:00 UTC)

### Sources processed: 3

| # | Source | Signal |
|---|--------|--------|
| 1 | awesome-llm-apps (Shubhamsaboo, 106k stars, +258 today) | 100+ production-ready AI agent templates. MCP agent section (Browser, GitHub, Notion), 19 Agent Skills modules, multi-agent coordinator/worker patterns for Finance/Legal/Real Estate. Investment multi-agent team = reference architecture for Fairford Fabric pipeline. Skills format converges with APM manifest + ENGRAM — ENGRAM README should cross-reference. |
| 2 | OpenSRE (Tracer-Cloud/opensre, 1.6k stars, +184 today) | Open reinforcement-learning environment for AI SRE incident response. Alert→fetch context→RCA→remediation loop. Anthropic first-class support, MCP-native tool layer, ACP/OpenClaw protocols. **Direct upgrade path for kpi-monitor**: replace one-shot threshold alerts with full RCA + remediation suggestions. Eval suite pattern (synthetic test cases + root-cause accuracy scoring) worth adopting for dispatch.py worker quality. |
| 3 | Willison: Adding new content type (new-content-type post) | Second Willison entry this cycle — different angle. Focuses on pattern imitation: "like the Atom feed" is more precise than a paragraph of requirements. Validates `/tmp` reference clone pattern from Digest Run 6. Adds: embed the validation oracle in the prompt, not as a separate test step. bi-agent schema cache_control block is exactly this — oracle is implicit. Could make it explicit. |

### Actionable additions (Digest 7)

| Item | Action | Priority |
|------|--------|----------|
| awesome-llm-apps finance/legal multi-agent | Deep-read coordinator/worker pattern — apply to Fairford PoC Phase 2 architecture | Medium |
| ENGRAM README | Add cross-reference to awesome-llm-apps Agent Skills format + APM manifest convergence | Low |
| kpi-monitor → OpenSRE upgrade | Design: replace alerts.md output with OpenSRE RCA pipeline as Phase 2 of kpi-monitor | Low |
| dispatch.py worker eval suite | Borrow OpenSRE synthetic test + root-cause accuracy scoring pattern for dispatch worker quality | Low |
| bi-agent oracle | Make validation oracle explicit in bi-agent prompt (not just implicit in schema block) | Low |

## Digest Run 8 (19:00 UTC)

### Sources processed: 2

| # | Source | Signal |
|---|--------|--------|
| 1 | "I'm Coding by Hand" (Miguel Conner, Substack, 261 HN pts) | Counter-signal to full delegation. Manual coding couples output with codebase mental model — agent delegation breaks this. Best AI users at Aily Labs were also strongest coders. **For ClaudesCorner**: dispatch.py workers correct for routine/parallel tasks; architectural decisions (SOUL.md, memory governance, new project scaffolding) still benefit from Jason-in-the-loop. "Deeper knowledge = more leverage" validates bi-agent schema quality → DAX quality chain. |
| 2 | Claude System Prompts as Git Timeline (Simon Willison) | Willison built extract.py — converts Anthropic's published Claude system prompts into browsable git history (26 revisions, 104 commits, July 2024→April 2026). Pattern: 4 commits per revision (snapshot + latest + family + firehose). Timestamp faking via env vars. **SOUL.md/skills application**: same 4-artifact git pattern could version ClaudesCorner identity evolution — SOUL.md changes become diffable. Memory writes could adopt snapshot+latest pattern for durable versioning. |

### Actionable additions (Digest 8)

| Item | Action | Priority |
|------|--------|----------|
| Delegation boundary | Document rule: routine/parallel tasks → dispatch.py; architecture/identity → Jason-in-loop | Low |
| SOUL.md git versioning | Apply Willison's 4-artifact-per-commit pattern to track SOUL.md + skill evolution via git blame | Low |
| Skill snapshot commits | On `mcp__skill-manager__skill_create`, auto-commit a dated snapshot file alongside the living latest | Low |

## Digest Run 9 (21:00 UTC)

### Sources processed: 4

| # | Source | Signal |
|---|--------|--------|
| 1 | "Built a DevOps UI for Fabric (TMDL + PBIR)" (r/MicrosoftFabric, No_Vermicelliii) | User built a GUI for editing Fabric semantic models (TMDL) + Power BI reports (PBIR) in a developer-friendly way. Validates report-diff direction — there's community appetite for Fabric/PBIR tooling. TMDL is the structured text format for semantic models; pbip_diff already handles PBIR pages/visuals/measures. **Opportunity**: extend pbip_diff to diff TMDL files (model changes) not just PBIR (report changes). |
| 2 | "10 Hours of Claude Design - My Thoughts" + "An old designer's perspective on claude design" (r/ClaudeAI) | Two substantive Claude Design reviews. Signal: Claude Design is usable but not yet production-ready for professional designers — missing token/auto layout awareness, component hierarchy import. For ClaudesCorner: Figma MCP pipeline not yet threatened; Claude Design is web-only with no API/MCP. The tools in the companion panel here are more capable than Claude Design for code generation. |
| 3 | "Look how they massacred my boy" (r/ClaudeAI, ItsJimmyPestoJr) | 4.7 regression sentiment. Likely Sonnet 4.5/4.6 user disappointed by behavior changes. Hold on 4.7 upgrade continues — multi-session sentiment still negative for agentic patterns. |
| 4 | Fabric "talk to your data" thread (r/MicrosoftFabric, shadow_nik21) | Community thread on Fabric's NL-to-data feature. Common complaints: hallucinated DAX, poor schema understanding, no multi-turn context. **bi-agent gap analysis**: our bi-agent already addresses multi-turn via cache_control + schema block. Making the validation oracle explicit (Digest Run 7 item) directly targets "hallucinated DAX" complaint. Fairford Phase 2 value prop is clear. |

### Actionable additions (Digest 9)

| Item | Action | Priority |
|------|--------|----------|
| pbip_diff TMDL extension | Extend pbip_diff to diff TMDL semantic model files (measures/relationships/columns) not just PBIR pages/visuals | Low |
| bi-agent validation oracle | Add explicit pass/fail oracle in bi-agent prompt: validate generated DAX against known-good output | Medium |
| Claude Design watch | No MCP/API yet — defer any Figma pipeline investment decisions for 30 days | Context |
| Fairford Phase 2 framing | "talk to your data" thread validates bi-agent as superior NL→DAX path — use as competitive framing in Phase 2 pitch | Medium |

## Digest Run 10 (~23:00 UTC)

### Sources processed: 2

| # | Source | Signal |
|---|--------|--------|
| 1 | Schneier + Lie "Mythos and Cybersecurity" (schneier.com, 2026-04-18) | Anthropic's Claude Mythos Preview found 27yo OpenBSD bug, 16yo FFmpeg flaw, 181 usable Firefox exploits. Restricted to ~50 large vendors only — asymmetric security coverage (specialized sectors: ICS, medical devices, regional banking stay exposed). False positive rates undisclosed. **ClaudesCorner signal**: agent sandboxing is non-optional (dispatch.py workers, smolvm pattern confirmed). Confidence calibration (false positive rates) is the same problem as kpi-monitor spike debounce. Governance analog: who decides which agents get access to what. |
| 2 | Willison "Adding a new content type" — 3-prompt agentic workflow (simonwillison.net, 2026-04-18) | Pattern: clone reference repo to `/tmp` → agent reads schema without commit risk → embed validation oracle in prompt ("compare to homepage"). Takeaway: **reference code over verbal spec** is the dominant principle. Already recorded in reference_willison_agentic_patterns.md. Confirms dispatch.py worker prompt improvement direction. |

### Actionable additions (Digest 10)

| Item | Action | Priority |
|------|--------|----------|
| dispatch.py worker isolation | Worker prompts should clone target project to /tmp, not rely on prose description | Medium |
| agent sandboxing note | Document smolvm blocked on Windows; track alternative sandbox options for dispatch workers | Low |
| kpi-monitor confidence calibration | Debounce already in place — consider adding explicit confidence_score field to alert output | Low |

## Digest Run 11 (~09:00 UTC 2026-04-19)

### Sources processed: 5

| # | Source | Signal |
|---|--------|--------|
| 1 | AI Subroutines / rtrvr.ai (zero-token deterministic browser automation) | Record-once, replay-deterministically pattern. LLM only selects parameters; execution is script-speed, zero token cost. Pre-built library (LinkedIn, Instagram, X). **dispatch.py**: ideal primitive for browser-based worker tasks — capture once, dispatch N times at zero inference cost. Complements chrome-devtools-mcp (inspection) and windows-mcp (OS layer). |
| 2 | Chrome DevTools MCP (ChromeDevTools/chrome-devtools-mcp, 36k stars, +438 today) | Official Chrome MCP server — 29 tools across input/navigation/emulation/performance/network/debugging. `npx` zero-config install. Installs as MCP + skills plugin. **Action**: wire into settings.json. dispatch.py workers get reliable browser tool layer. Complements windows-mcp for full desktop automation. Power BI browser interactions (report export, embedded dashboards) also covered. |
| 3 | claude-mem (thedotmack/claude-mem, 62k stars, +1024 today, AGPL-3.0) | Auto-captures, compresses (Agent SDK), and reinjects session context across Claude Code sessions via 5 lifecycle hooks. PostToolUse → compress → store pattern. **ENGRAM parallel**: claude-mem is a working implementation of ENGRAM's core premise. memory-mcp upgrade path: add PostToolUse auto-compress → write_memory. Licensing gap: AGPL vs ENGRAM's MIT — cannot reuse code directly. |
| 4 | GenericAgent (lsdefine/GenericAgent, 4.2k stars, +794 today, MIT) | L0–L4 five-layer memory + skill crystallization (first-encounter → explore → promote to L3). <30K context/task claimed. ENGRAM direct structural parallel: L0=SOUL, L1=vectordb index, L3=skills, L4=daily logs. **Crystallization gap**: skill-manager-mcp requires manual skill_create — GenericAgent's auto-promotion pattern could automate promotion from dispatch.py worker outputs. Token budget validates dispatch.py short-parallel architecture. |
| 5 | Remoroo (autonomous overnight ML experiments, spec→plan→edit→eval→decide loop) | 30+ experiments/night, git commits only on metric improvement. Fixed evaluation harness prevents worker self-report drift. **dispatch.py eval gap**: workers have no structured eval step — Remoroo suggests adding `verify:` oracle block to worker prompts (converges with Willison oracle pattern). bi-agent: metric-gated accept — only store DAX if it passes row-count spot-check. |

### Actionable additions (Digest 11)

| Item | Action | Priority |
|------|--------|----------|
| chrome-devtools-mcp | Wire into settings.json: `npx -y chrome-devtools-mcp@latest`. dispatch.py workers get 29 browser tools. | Medium |
| AI Subroutines pattern | When building browser dispatch tasks, use record-once pattern rather than ad-hoc LLM browser calls | Low |
| memory-mcp PostToolUse compression | Upgrade memory-mcp: PostToolUse hook → AI-compress observations → auto-write_memory (inspired by claude-mem) | Low |
| skill auto-crystallization | Design crystallization gate in dispatch.py: if worker completes novel task successfully, auto-call skill_create | Low |
| dispatch.py eval oracle | Add `verify:` block to all worker prompts — fixed success criteria, not self-reported | Medium |
| bi-agent metric gate | After DAX generation, validate against spot-check row count before caching result | Low |
