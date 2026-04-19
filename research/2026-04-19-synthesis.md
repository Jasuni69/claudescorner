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
| Add `spec:` artifact step to dispatch.py build worker prompts (OpenSpec pattern) | Medium | Backlog |
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
| OpenCode plan/build agent role convention for dispatch.py workers | Low | Backlog |
