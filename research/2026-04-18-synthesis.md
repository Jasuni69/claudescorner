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
