# Research Synthesis — 2026-04-23

## Digest Run 1

**Sources processed:** 2
**Files:** Microsoft Teams SDK BYOA (microsoft.github.io/teams-sdk, HN 4pts), pgrust — 17-agent Postgres Rust rewrite (malisper.me, HN 2pts)

---

### Microsoft Teams SDK BYOA — HTTP Adapter for Agent-to-Teams Deployment

**Source:** microsoft.github.io/teams-sdk, HN 4pts
**Signal strength:** Low-Medium — niche enterprise integration; early signal on fabric-mcp → Teams deployment path

**Key findings:**
- HTTP adapter pattern: wraps any LangChain/Azure Foundry agent into a Teams bot via `POST /api/messages` — zero code rewrite of existing agent logic
- Bot Framework SDK underneath; Teams = channel layer on top of existing agent API surface
- No MCP integration yet — adapter speaks HTTP, not MCP
- No agent-identity or credential governance layer — adapter is thin passthrough
- Microsoft Azure Foundry = preferred agent runtime (Azure-first, not Claude-first)

**ClaudesCorner impact:**
- **fabric-mcp → Teams deployment path:** Fairford Phase 2 end-users likely use Teams for internal comms. fabric-mcp exposes Fabric data via MCP; Teams SDK BYOA wraps any HTTP agent as a Teams bot. Potential Fairford Phase 2 enterprise UI path: `fabric-mcp → Claude dispatch worker → Teams bot` via BYOA adapter — zero Fabric UI build required.
- **teams-sdk-mcp bridge opportunity:** Current Teams SDK speaks HTTP, not MCP. A thin `teams-sdk-mcp` wrapper would let dispatch.py workers send Teams messages as MCP tool calls — same pattern as `fabric-mcp` wrapping Fabric REST API.
- **Low priority now:** HN 4pts = early signal. No MCP layer = integration friction. Only actionable if Fairford Phase 2 requires a Teams delivery channel (Jason's call, not actionable autonomously).
- **Backlog (Low):** Evaluate teams-sdk-mcp wrapper when Fairford Phase 2 scope includes Teams notifications or bot interactions. BYOA HTTP adapter = zero-code agent→Teams wire when needed.

---

### pgrust — 17-Agent Concurrent Postgres Rust Rewrite

**Source:** malisper.me, HN 2pts
**Signal strength:** Medium-High — empirical production case study; 3rd independent confirmation of oracle gap principle; validates dispatch.py concurrency ceiling

**Key findings:**
- 250k LOC Postgres Rust rewrite completed in 2 weeks using 17 concurrent AI agents (Conductor framework)
- Conductor: auto-managed git worktrees for each agent — each agent gets isolated branch, automatic merge on completion
- Test-driven commits: small, test-driven commits eliminated merge conflicts that full-file rewrites would cause
- **Oracle gap finding:** "Dumb code makes it through" — agents passed self-written tests but introduced subtle correctness errors only caught by independent cross-agent review. Self-reported test pass ≠ correctness.
- **CPU bottleneck:** At 17 agents, CPU became the bottleneck before LLM rate limits — suggests practical ceiling is hardware-bound, not API-bound
- **Human-in-loop pattern:** Humans reviewed at merge boundaries (not per-commit) — reduces review cost while maintaining correctness gate

**ClaudesCorner impact:**
- **Oracle gap: 3rd independent confirmation.** Timeline of oracle gap signals:
  1. Kilo.ai FlowGraph benchmark (2026-04-22): Claude 91/100, Kimi 68/100 — both models' *self-written tests* had 100% pass rate; independent validator found 6 Kimi bugs, 1 Claude bug
  2. Willison reference-repo prompting (2026-04-19/18): "bake validation oracle into prompt" — self-validate is insufficient
  3. **pgrust (today):** 250k LOC production rewrite — "dumb code makes it through" despite self-tests passing; human merge-boundary review caught correctness errors
  - Implication: dispatch.py verify oracle structural assertion (balanced parens, schema cross-ref, HEARTBEAT log check) is correctly designed. The principle — structural/independent check > self-reported success — is now confirmed by 3 independent production cases.
- **Dispatch.py 3-worker cap validated empirically:** pgrust CPU saturation at 17 agents (not LLM limits) confirms concurrency ceiling is hardware-bound. dispatch.py 3-worker limit is appropriate for a Windows laptop — scaling to 5-10 workers would hit CPU/RAM before API limits.
- **Conductor worktree pattern ≈ dispatch.py architecture:** Conductor auto-assigns git worktrees per agent and auto-merges on completion. dispatch.py workers currently operate on the shared `main` working tree — no worktree isolation. The `using-git-worktrees` skill exists but is not wired into dispatch.py automatically. Conductor's auto-assign is closer to the ideal pattern.
- **Small test-driven commits:** Conductor enforced small commits with passing tests before merge. dispatch.py BUILD worker prompt has SPEC→BUILD→VERIFY but no commit size constraint. The "surgical edits" instruction added 2026-04-23 is the dispatch.py equivalent.

**Actionable items from pgrust:**
1. **Info (already covered):** 3rd oracle gap confirmation — existing 3-layer oracle in bi-agent and VERIFY clause in BUILD worker already address this. No new code needed.
2. **Backlog (Medium):** Evaluate auto-worktree assignment in dispatch.py — `run_task()` could create a fresh git worktree per task (via `git worktree add`) and clean up on completion. This eliminates shared-tree conflicts when 2-3 workers touch overlapping files. Not urgent since current workers operate on separate files by domain (infra/research/memory).
3. **Backlog (Low):** Explore Conductor framework as dispatch.py v2 worktree orchestration layer.

---

---

## Digest Run 2

**Sources processed:** 2
**Files:** Fastmail MCP Server (fastmail.com/blog, HN newest), CubeSandbox (tencentcloud/CubeSandbox, HN newest)

---

### Fastmail MCP Server — MCP as First-Class API Protocol

**Source:** fastmail.com/blog, HN newest
**Signal strength:** Medium — first-party production SaaS treating MCP as a peer API protocol alongside IMAP/CalDAV; ecosystem maturation signal

**Key findings:**
- Official MCP endpoint at `api.fastmail.com/mcp` — not a wrapper, a distinct API surface
- Exposes email/calendar/contacts with OAuth tiered consent (read / write / send)
- "AI orchestration across services" framing — agent can see email, check calendar, draft reply in a single MCP session
- Production: live endpoint, not a prototype; Fastmail is a 25-year-old email provider making a deliberate architectural decision
- Pattern: established SaaS companies adding `/mcp` as a first-class protocol peer (same direction as Notion, Linear, GitHub)

**ClaudesCorner impact:**
- **Cloudflare Email (outbound) + Fastmail MCP (inbound read/write)** = complete agent email stack if combined with AgentKey for credential governance
- **Ecosystem signal:** Two independent email infrastructure providers (Cloudflare + Fastmail) now provide MCP endpoints. This accelerates the viability of dispatch.py workers that need email context for daily digest ingestion or alert notifications.
- **dispatch.py research worker:** Could authorize Fastmail MCP to read daily digest emails and surface them directly in the research pipeline — eliminating reddit_brief.py manual fetch for email-delivered newsletters.
- **Info/Backlog (Low):** No immediate code change. Monitor for SSE/streaming support (currently request-response only). Wire fastmail-mcp + AgentKey when dispatch.py needs inbox access for research.

---

### CubeSandbox — Windows-Friendly KVM Agent Sandbox (smolvm Alternative)

**Source:** github.com/tencentcloud/CubeSandbox, HN newest
**Signal strength:** High — addresses a specific gap (Windows-compatible agent sandbox) that smolvm cannot fill; E2B SDK compatibility = low migration friction

**Key findings:**
- TencentCloud RustVMM + KVM microVM sandbox; dedicated guest OS kernel (not shared-kernel Docker)
- **<60ms coldstart** (50 concurrent: <150ms), **<5MB memory overhead per instance** — denser and faster than smolvm
- **E2B SDK compatible**: one env var swap (`SANDBOX_URL=https://cubesandbox.tencent.com`) — zero code changes for any E2B consumer
- **REST gateway**: cross-platform HTTP API — no native VMM installation required; dispatch.py workers on Windows 11 can spin sandboxes via HTTP
- CubeVS (eBPF): per-sandbox network isolation prevents lateral movement between workers
- **License unknown**: TencentCloud OSS — verify Apache/MIT vs proprietary before Fairford use

**ClaudesCorner impact:**
- **smolvm gap filled:** smolvm (tracked since 2026-04-18) requires libkrun VMM — Mac/Linux only. CubeSandbox REST API works on Windows via HTTP calls. This makes isolated worker sandboxing viable in the current ClaudesCorner environment without waiting for Windows MLX or smolvm port.
- **dispatch.py worker isolation:** Current 3 workers share the same process/working directory. CubeSandbox could wrap each `claude.exe` subprocess invocation in an isolated VM — preventing one worker's file writes from conflicting with another. Medium priority since workers currently operate on separate file domains (infra/research/memory).
- **Governance stack completion:** CubeSandbox (execution isolation) + AgentKey (identity/credential) + CrabTrap (outbound proxy) + AgentRQ (human escalation) = complete dispatch.py worker governance stack. Each layer addresses a different attack surface.
- **E2B drop-in:** If dispatch.py ever integrates E2B SDK for remote code execution, migrating to CubeSandbox is one env var change.
- **License check required:** Cannot be used in Fairford Phase 2 production without verifying license is permissive. Check before any production wiring.

**Actionable items from CubeSandbox:**
1. **Backlog (Medium):** Add `reference_cubesandbox.md` to MEMORY.md — Windows-friendly sandbox option for dispatch.py worker isolation Phase 2; E2B-compatible REST gateway; license TBD.
2. **Backlog (Low):** Monitor CubeSandbox license and GitHub traction; evaluate REST API wrapper for dispatch.py `run_task()` sandbox option when Phase 2 isolation is needed.

---

## Digest Run 3

**Sources processed:** 3
**Files:** Anthropic MCP Production Guide (claude.com/blog, HN newest), MemReader (arxiv.org, HN 3pts), Preflight MCP Testing (m8ven.ai, HN 4pts)

---

### Anthropic MCP Production Guide — Intent-Grouped Tools + Tool Search + Vaults

**Source:** claude.com/blog, HN newest
**Signal strength:** High — first-party Anthropic production guidance; validates and extends existing architecture bets across skill-manager-mcp, fabric-mcp, and ENGRAM

**Key findings:**
- **Intent-grouped tools:** One `create_issue_from_thread` tool > 3 separate tools (fetch_thread + analyze_intent + create_issue). Composing intent into a single tool reduces orchestration overhead and token cost.
- **Tool search = 85% token reduction:** Deferred tool loading (fetch schema only when needed) cuts token cost by 85% vs loading all tool schemas upfront. This is the lazy-tool pattern operationalized with a number.
- **Elicitation URL mode for OAuth:** Live in Claude Code — instead of prompting the user for credentials mid-task, Claude Code opens an OAuth URL. Replaces the current manual `FABRIC_TENANT_ID`/`CLIENT_ID` env var flow for fabric-mcp.
- **Vaults for managed credential injection:** Anthropic-managed credential store; agents reference credentials by vault key, never see raw secrets. Fills the AgentKey credential governance gap natively if Vaults are accessible via API.
- **Skills + MCP bundled as plugin unit:** `plugin_manifest.json` bundles a skill + its MCP server dependencies as a single installable unit. This is exactly the ENGRAM plugin bundle pattern (SOUL/HEARTBEAT/memory-mcp/skills as one deployable).
- **Programmatic tool calling = 37% token reduction:** Calling tools via code blocks (structured) vs natural language reduces 37% tokens. Dispatch.py workers using `claude.exe --print` may benefit from structured output flags.

**ClaudesCorner impact:**
- **fabric-mcp intent-design validated:** The `run_dax_query` tool in fabric-mcp already bundles intent (run query + return results). The guide validates the existing design. Opportunity: replace multi-step workspace → dataset → query flows with single `query_dataset_by_name` intent-grouped tools.
- **skill-manager-mcp deferred-load already implemented:** `skill_search` as primary entry point with `skill_read` on-demand = lazy-tool pattern already in place. The 85% token reduction number is the first quantified justification for this architecture choice.
- **ENGRAM plugin bundle:** The Skills+MCP bundled plugin unit pattern = ENGRAM's natural distribution format. `engram_plugin.json` could declare: SOUL.md, HEARTBEAT.md, memory-mcp server, skill-manager-mcp server, skill library. One install command bootstraps the full identity+memory+skills stack.
- **OAuth elicitation for fabric-mcp:** When Fairford Phase 2 is unblocked, replace static MSAL device flow in fabric-mcp with Claude Code OAuth elicitation. Less user friction (URL-based auth vs terminal prompt), and matches Anthropic-recommended pattern.
- **Vaults vs AgentKey:** If Anthropic Vaults become API-accessible, they could replace AgentKey for credential governance in the ClaudesCorner stack. Monitor for API availability.

**Actionable items:**
1. **Done (memory):** Add reference_anthropic_mcp_production.md to MEMORY.md — 85% token reduction via tool search, intent-grouped tools, OAuth elicitation, Vaults credential layer, plugin bundle pattern.
2. **Backlog (Medium):** Add intent-grouped `query_dataset_by_name` tool to fabric-mcp — wraps workspace lookup + dataset resolve + DAX execute into one call; reduces Fairford Phase 2 orchestration steps.
3. **Backlog (Low):** Evaluate Anthropic Vaults as AgentKey replacement for dispatch.py credential governance when API availability confirmed.
4. **Backlog (Low):** Draft `engram_plugin.json` plugin manifest for ENGRAM distribution (SOUL.md + HEARTBEAT.md + memory-mcp + skill-manager-mcp + skills as single installable unit).

---

### MemReader — Active GRPO-Driven Memory Extraction (Write-Gate Pattern)

**Source:** arxiv.org, HN 3pts
**Signal strength:** Medium — novel memory extraction architecture; directly relevant to memory-mcp write authority problem

**Key findings:**
- 2-model architecture: 0.6B **passive** model screens all text for memory-worthiness; 4B **active** model extracts structured memories from passages that pass screening.
- Trained with GRPO (Group Relative Policy Optimization) — reinforcement learning, not supervised fine-tuning.
- SOTA on LOCOMO (long-context memory), LongMemEval, and HaluMem (hallucination-resistance) benchmarks.
- **Write-gate pre-filter pattern:** The passive/active split prevents low-signal content from flooding the memory store — only content that passes the 0.6B screening gate gets processed by the 4B extractor.
- Addresses the "what to write" problem: current memory-mcp `write_memory` is called explicitly by agents; MemReader would automate the decision.

**ClaudesCorner impact:**
- **memory-mcp write authority gap:** Currently only agents with explicit `write_memory` calls populate the vectordb. Most session content (research digests, code context, corrections) is not automatically extracted. MemReader's passive/active architecture is the missing automated write layer.
- **ENGRAM v2 write layer:** MemReader = the automated memory-extraction component that ENGRAM currently lacks. The passive screen + active extract pattern could be wrapped as a Claude Code `PostToolUse` hook: on every large Bash/Edit output, screen with a lightweight classifier, extract memories from high-signal outputs.
- **Practical constraint:** Models are arxiv-cited — weights may not be publicly released. The *pattern* (screen-then-extract) is reproducible with any instruction-following model.
- **Haiku as passive screener:** The 0.6B role = Haiku's role in dispatch.py Tier 1. A Haiku-based `should_memorize(text)` classifier + Sonnet-based `extract_memory(text)` function would approximate MemReader in the ClaudesCorner stack.

**Actionable items:**
1. **Backlog (Medium):** Implement write-gate in memory-mcp `write_memory` — Haiku-based `should_memorize()` pre-filter before storing; prevents noise accumulation in vectordb; reference MemReader passive/active pattern.
2. **Info:** MemReader weights TBD; monitor arxiv for code release (HKUDS lab — same org as RAG-Anything and DeepTutor, historically open-source).

---

### Preflight MCP Testing — Pre-Release Validator for MCP Servers

**Source:** m8ven.ai, HN 4pts
**Signal strength:** Medium — fills a gap (automated MCP server compliance check) that is currently manual; directly actionable before ENGRAM public release

**Key findings:**
- 15-second automated validator: runs 6 checks against any MCP server endpoint.
- Checks: OAuth 2.1 compliance, CORS headers, protocol handshake, domain/TLS, token refresh flow, anonymous fallback.
- Target use case: "run before releasing an MCP server to production or publishing to marketplace."
- CLI + CI integration: designed to run in a pipeline, not just interactively.

**ClaudesCorner impact:**
- **memory-mcp + skill-manager-mcp compliance:** Both servers are stdio MCP servers, not HTTP MCP servers — the OAuth/CORS/domain checks don't apply to stdio transport. Preflight targets HTTP/SSE MCP servers. Not immediately applicable.
- **ENGRAM public release gate:** When memory-mcp or skill-manager-mcp are exposed over HTTP (e.g. for company-wide skill vectordb via Azure), Preflight becomes a pre-release requirement. Adds a 15-second compliance gate before any ENGRAM component is made network-accessible.
- **fabric-mcp future HTTP exposure:** If fabric-mcp is moved from stdio to HTTP transport for Fairford Phase 2 multi-user access, Preflight should run as a CI step before deployment.
- **Low friction:** `pip install preflight-mcp` + one command = no maintenance burden.

**Actionable items:**
1. **Backlog (Low):** Wire `preflight-mcp` as a CI check for any MCP server that moves to HTTP transport (memory-mcp, skill-manager-mcp, fabric-mcp). Not applicable to current stdio deployments.
2. **Info:** Document pre-release checklist for ENGRAM: Preflight MCP validator + Sunglasses inbound scanner + AgentKey credential check = 3-tool compliance gate before any ENGRAM component goes network-accessible.

---

## Digest Run 4

**Sources processed:** 3
**Files:** Design Slop (adriankrebs.ch, HN 312pts), Microsoft Foundry Hosted Agents (devblogs.microsoft.com/foundry, public preview 2026-04-22), ppt-master (hugohe3/ppt-master, 7.4k stars, +1911 weekly)

---

### Design Slop — AI-Generated UI Pattern Analysis

**Source:** adriankrebs.ch, HN 312pts
**Signal strength:** High — empirical 500-submission study; 312 HN points = strong community validation; directly supports headless/MCP-first architecture decision

**Key findings:**
- Playwright DOM/CSS automated analysis of 500 Show HN submissions
- 67% exhibit AI-generated "design slop": Inter font + VibeCode Purple + shadcn/ui + glassmorphism
- Article concludes: design irrelevance is accelerating as AI agents become primary software consumers (not humans)
- Agent-facing APIs matter more than UI polish — users increasingly delegate UI interaction to agents

**ClaudesCorner impact:**
- **Headless/MCP-first validated empirically:** fabric-mcp exposes Fabric as MCP (not UI). ENGRAM memory-mcp is headless knowledge store. dispatch.py operates without a GUI. This study confirms that agent-native interfaces outperform UI-polished apps at reaching other agents.
- **Fairford Phase 2 framing:** If Fairford users increasingly query Fabric via agent delegation rather than dashboards, fabric-mcp + bi-agent NL→DAX pipeline is the correct long-term architecture over a Power BI report layer.
- **Info:** No code change needed. Confirms existing architecture. Good citation for Fairford pitch materials.

**Actionable items:**
1. **Info:** Architecture validated by empirical study — no code change. File as supporting evidence for Fairford headless-first framing.

---

### Microsoft Foundry Hosted Agents — Enterprise Agent Hosting on Azure

**Source:** devblogs.microsoft.com/foundry, public preview 2026-04-22
**Signal strength:** High — Microsoft official public preview announcement; direct Fairford Phase 2 deployment path on Azure

**Key findings:**
- **Claude Agent SDK support:** Foundry Hosted Agents runs Claude Agent SDK agents natively in Azure — not just OpenAI models
- **Hypervisor-isolated per-session VMs:** Each agent session gets an isolated VM (addresses dispatch.py worker isolation gap via Microsoft-managed infra)
- **Toolbox (MCP-any-client):** Foundry exposes a Toolbox layer that wraps any MCP server — fabric-mcp could plug in directly
- **Fabric IQ data access:** Foundry has native Fabric data connectors — agents can query OneLake/semantic models without separate auth
- **Enterprise controls:** Azure RBAC, audit logs, compliance — removes Fairford governance blockers

**ClaudesCorner impact:**
- **Fairford Phase 2 Option C:** Prior options were A (Microsoft official: Fabric MCP + Power BI Modeling MCP + VS Code Copilot) and B (Claude-native: fabric-mcp + dispatch.py). Foundry Hosted Agents = Option C: Claude Agent SDK on Azure, Fabric IQ native, enterprise isolation, MCP Toolbox for fabric-mcp drop-in.
- **Option C is likely the strongest Fairford pitch:** Azure-native (Numberskills Azure tenant), Claude-native (bi-agent + dispatch.py), enterprise governance (RBAC + audit), hypervisor isolation (per-session VMs), Fabric IQ (no custom fabric-mcp auth needed). Presents as enterprise Microsoft product, not a Claude Code experiment.
- **ENGRAM portability:** Claude Agent SDK compatibility confirms ENGRAM SOUL/HEARTBEAT/memory-mcp pattern would port to Foundry without re-architecture.
- **Blocked on Jason:** Fairford Phase 2 scope not yet defined — cannot act autonomously. Flag Option C when Jason unblocks.

**Actionable items:**
1. **Backlog (High, Jason-blocked):** Present Foundry Hosted Agents as Fairford Phase 2 Option C when Jason unblocks. Framing: Azure-native + Claude Agent SDK + Fabric IQ + enterprise isolation = lowest friction enterprise path.
2. **Info:** reference_microsoft_foundry_agents.md — add to MEMORY.md; validate ENGRAM portability via Claude Agent SDK docs.

---

### ppt-master — Claude Code Generates Real PPTX from Documents

**Source:** github.com/hugohe3/ppt-master, 7.4k stars, +1911 weekly
**Signal strength:** Medium — solid traction; practical tool; no MCP layer = integration opportunity

**Key findings:**
- Claude Code (Opus primary model) generates real editable .pptx files from PDF/DOCX/HTML source documents
- $0.08/deck at current Opus 4.7 pricing — economically viable for automated report generation
- AGENTS.md present — built for agentic use, not just interactive
- No MCP layer yet — runs as standalone Python tool

**ClaudesCorner impact:**
- **Fabric report → PPTX pipeline candidate:** Fairford Phase 2 deliverable could include auto-generated executive PPTX from Fabric semantic model DAX results. bi-agent generates DAX → Fabric query returns table → ppt-master converts to PPTX. markitdown-mcp is the reverse (PPTX/PDF → Markdown for ingestion); ppt-master is the forward direction (data → PPTX for export).
- **ppt-master-mcp opportunity:** Wrap as `generate_presentation(source_content, template, output_path)` MCP tool. Dispatch.py worker could generate weekly Fairford summary PPTX from kpi-monitor alerts. Low priority until Fairford Phase 2 unblocked.
- **Backlog (Low):** Monitor traction (currently 7.4k); evaluate ppt-master-mcp wrapper when Fairford Phase 2 reporting scope is confirmed.

**Actionable items:**
1. **Backlog (Low):** ppt-master-mcp: wrap as MCP tool for bi-agent → DAX → PPTX pipeline; blocked on Fairford Phase 2 scope.
2. **Info:** Add reference_ppt_master.md to MEMORY.md — $0.08/deck Claude Code PPTX generator; markitdown-mcp complement; Fairford report export path.

---

## Digest Run 5

**Sources processed:** 2
**Files:** ml-intern (huggingface/ml-intern, 1.8k stars, HN newest), Agent Skills Standardization (agensi.io)

---

### ml-intern — HuggingFace Autonomous ML Engineer Agent

**Source:** github.com/huggingface/ml-intern, 1.8k stars, +530 today
**Signal strength:** High — HuggingFace-official production agent harness; three specific patterns directly applicable to dispatch.py

**Key findings:**
- **300-iteration agentic loop cap:** ml-intern hard-stops after 300 tool invocations per task; prevents infinite agent loops consuming unbounded tokens
- **Doom-loop detector:** monitors last N tool invocations; if the same tool+arguments pattern repeats ≥3 times consecutively, injects a corrective prompt ("you seem stuck — change your approach") rather than hard-stopping; gives agent a recovery opportunity before termination
- **170k auto-compaction:** at 170k context tokens, ml-intern summarizes the session and continues from a compressed context — prevents context overflow without full termination
- **MCP config-driven integration:** agent capabilities declared via `.mcp.json` — same pattern as dispatch.py workers using settings.json MCP wiring
- **HF Hub session upload:** completed sessions uploaded to HuggingFace Hub for replay/analysis — analogous to dispatch.py result_file + HEARTBEAT log pattern

**ClaudesCorner impact:**
- **dispatch.py doom-loop guard:** dispatch.py single-shot `claude.exe -p` workers can doom-loop by invoking the same Bash/Read/Edit command repeatedly when stuck. Since the agent session is a single `claude.exe` process, the correct fix is a **prompt-level instruction** telling the agent to detect and self-interrupt doom loops. Adding a doom-loop clause to BUILD/PLAN/MEMORY worker prompts mirrors ml-intern's corrective injection pattern at zero infra cost.
- **Iteration cap context:** dispatch.py has `TIMEOUT_SECONDS=300` (5 min wall-clock cap), which implicitly bounds iterations. A prompt-level cap instruction ("if you have made the same tool call 3+ times without progress, output BLOCKED: doom-loop detected and halt") adds explicit cognitive constraint alongside the wall-clock timeout.
- **170k auto-compaction:** Claude Code's native compaction already handles context overflow. The ml-intern 170k threshold is consistent with CC's default — no code change needed.

**Actionable items:**
1. **Backlog (Medium):** Add doom-loop guard instruction to dispatch.py BUILD worker prompt — `if same tool call appears 3+ times without progress, output BLOCKED: doom-loop and halt`; matches ml-intern corrective injection; zero infra cost.
2. **Info:** ml-intern session upload to HF Hub = audit trail pattern; HEARTBEAT log + result_file already covers this for ClaudesCorner.

---

### Agent Skills Standardization — agensi.io SKILL.md Cross-Platform Standard

**Source:** agensi.io, HN newest
**Signal strength:** High — 6 major platforms (Anthropic/OpenAI/Google/GitHub/Cursor/OpenClaw) independently converged on SKILL.md format without coordination; validates skill-manager-mcp design bet

**Key findings:**
- SKILL.md + YAML frontmatter has become de facto cross-platform skill standard adopted by 6 major platforms **without any coordination** — organic convergence from independent pain (each platform needed structured skill metadata)
- **Ecosystem gaps identified:** discovery (no universal index), versioning (no semver), dependency management (no skill dep graph), security scanning (no injection/malware check before execution)
- **Agensi marketplace:** fills the security scanning gap via automated prompt injection heuristic on submitted skills; runs on upload not at install time
- **`agent_activation_allowed` governance:** agensi marketplace two-layer model (human-browse + agent-activate permissions) is identical to `agent_activation_allowed` flag added to skill-manager-mcp v2.4.0

**ClaudesCorner impact:**
- **skill-manager-mcp v2.4.0 already aligned:** `agent_activation_allowed` flag (added 2026-04-22) matches the agensi marketplace two-layer governance model. skill-manager-mcp is ahead of the gap identified in this article.
- **Security gap: prompt injection in skill bodies:** agensi scans for injection on upload; skill-manager-mcp `skill_create` currently stores skills without scanning. Adding a lightweight prompt injection heuristic to `skill_create` would close this gap before ENGRAM public release.
- **ENGRAM portability confirmed:** SKILL.md cross-platform convergence confirms skill-manager-mcp's agentskills.io format is the correct canonical format. ENGRAM skills will be portable to Anthropic, HuggingFace, GitHub, and Cursor without conversion.
- **Discovery gap:** agensi.io as external discovery index is the ENGRAM public marketplace entry point — monitor for API access.

**Actionable items:**
1. **Backlog (Medium):** Add prompt injection heuristic to `skill_create` in skill-manager-mcp — scan skill body for scope-redefinition patterns before storing; same Sunglasses pattern as dispatch.py inbound scan; prevents malicious skills entering the local vectordb.
2. **Info:** ENGRAM portability confirmed by 6-platform SKILL.md convergence — no format migration needed.
3. **Backlog (Low):** Monitor agensi.io for public API access — potential ENGRAM public marketplace discovery endpoint.

---

## Digest Run 6

**Sources processed:** 2
**Files:** context-mode (mksglu/context-mode, 9.2k stars, HN newest), Awesome Agent Skills (VoltAgent/awesome-agent-skills, 17.7k stars, MIT)

---

### context-mode — 98% Context Reduction via SQLite FTS5 + BM25 Retrieval

**Source:** github.com/mksglu/context-mode, 9.2k stars, +302 today
**Signal strength:** High — empirical 98% context reduction on a real task (58.9KB→1.1KB on 20 GitHub issues); directly applicable to dispatch.py MAX_CONTEXT_TOKENS budget; 12-platform support

**Key findings:**
- MCP server wrapping sandboxed subprocess execution + SQLite FTS5 + BM25 full-text retrieval
- **98% context reduction:** 20 GitHub issues compressed from 58.9KB to 1.1KB — preserves only BM25-ranked relevant chunks; avoids full-context loading that inflates dispatch.py token spend
- **Session continuity via SQLite event log:** SQLite persists the event log across Claude Code `/clear` and conversation compaction — session recovery without losing task context; complements HEARTBEAT.md
- **Sandboxed subprocess execution:** code execution in isolated subprocess — worker isolation without VM overhead
- **Elastic License 2.0:** fine for internal use (ClaudesCorner, Fairford PoC), blocks building SaaS on top; ENGRAM distribution not affected since ENGRAM is an installable kit, not a hosted service
- **12-platform support:** Claude Code, Cursor, Windsurf, Cline, Zed, Copilot — confirms MCP is the correct portability layer

**ClaudesCorner impact:**
- **dispatch.py MAX_CONTEXT_TOKENS=8000 complement:** Current workers use `MAX_CONTEXT_TOKENS=8000` as a hard cap signal — but the prompt assembly still loads full file contents. context-mode's BM25 retrieval approach would let dispatch.py workers query large files/logs at <100 tokens instead of loading 50KB. The `claude-context` MCP (zilliztech, 6.9k stars) achieves ~40% reduction via hybrid BM25+vector; context-mode achieves 98% via FTS5 alone on structured data (issue text, log lines).
- **Session continuity complement to HEARTBEAT.md:** context-mode's SQLite event log restores task context after `/clear`. HEARTBEAT.md is the durable narrative log; context-mode would be the ephemeral session event log. Together: HEARTBEAT = "what was decided", context-mode = "what tools were called this session". The dispatch.py `task_plan.md` file pattern already approximates this for tier ≥2 tasks.
- **Sandboxed subprocess pattern:** context-mode's subprocess isolation is lighter than CubeSandbox KVM — suitable for untrusted code execution (e.g. DAX test queries) without VM overhead. Fills a gap between "run in main process" and "full CubeSandbox VM".
- **Elastic License 2.0 is acceptable:** Internal use + ENGRAM installable kit both fall within EL2 scope. No blocking constraint for ClaudesCorner or Fairford PoC.

**Actionable items:**
1. **Backlog (Medium):** Evaluate context-mode MCP server as dispatch.py research worker supplement — BM25 retrieval over large synthesis files instead of loading full 2026-04-23-synthesis.md into context. Wire via settings.json when dispatch.py workers start hitting the 8000-token limit on large synthesis reads.
2. **Info:** context-mode SQLite event log as session continuity layer — complementary to HEARTBEAT.md; monitor for API that would let dispatch.py workers replay session context across runs.

---

### Awesome Agent Skills — 1100+ Curated Official Skills from 50+ Orgs

**Source:** github.com/VoltAgent/awesome-agent-skills, 17.7k stars, MIT
**Signal strength:** High — third major aggregate confirming SKILL.md de facto standard; 1100+ production skills from Microsoft (133), Sentry (40+), OpenAI (40+), Trail of Bits (security), Vercel, Stripe, Cloudflare, Anthropic; MIT license

**Key findings:**
- 1100+ curated official skills in SKILL.md format; 12-platform support (Claude Code, Cursor, Copilot, Windsurf, Cline, Zed, Roo, Augment, Kilo, Gemini, Codex, Aider)
- **Microsoft Azure skills (133 skills):** dedicated Azure SDK skills for resource management, storage, Cosmos DB, AI services — directly importable for Fairford Phase 2 if Fabric/Azure operations need skill-wrapped execution
- **Trail of Bits security skills:** professional security audit skills from a top-tier firm — applicable to dispatch.py worker review (code audit, vuln scan, secure design review patterns)
- **Stripe/Vercel/Cloudflare skills:** production-grade API skills from companies that have already codified their agent interfaces — skill-manager-mcp import candidates for infrastructure management
- **MIT license:** no commercial use restriction; Fairford production deployment is unblocked; ENGRAM distribution can include these skills by reference
- **Third confirmation of SKILL.md standard:** Anthropic (anthropics/skills, 120k stars) + HuggingFace (huggingface/skills, 10.3k stars) + Awesome Agent Skills (17.7k stars) — three independent aggregates all converging on SKILL.md format without coordination. Pattern is locked in.

**ClaudesCorner impact:**
- **skill-manager-mcp import candidates:** Trail of Bits security skills are the highest-value immediate import — wrap as local skills for dispatch.py worker security review gate. Microsoft Azure skills are the second target for Fairford Phase 2.
- **ENGRAM distribution format confirmed:** With Anthropic + HF + VoltAgent all using SKILL.md, ENGRAM's skill format is de facto standard. No conversion needed when sharing ENGRAM skills publicly.
- **Fairford Phase 2 Azure skills:** Microsoft's 133 Azure skills are production-ready skill wrappers for Azure resource management — directly applicable to Fairford Phase 2 Azure deployment (Foundry Hosted Agents, OneLake, Azure AI Search). These are importable as-is via `/plugin marketplace add VoltAgent/awesome-agent-skills`.
- **Trail of Bits security audit pattern:** Security skills from a firm that does professional audits = higher-quality security review patterns than ad-hoc Bash prompts. Worth importing for dispatch.py code review gate before any external push.

**Actionable items:**
1. **Backlog (Medium):** Import Trail of Bits security skills into skill-manager-mcp — wire as local skills for dispatch.py worker pre-merge security review. `/plugin marketplace add VoltAgent/awesome-agent-skills` + filter to security subset.
2. **Backlog (Medium):** Add reference_awesome_agent_skills.md to MEMORY.md — 1100+ SKILL.md format skills; MIT; Microsoft Azure skills for Fairford; Trail of Bits security for dispatch.py review gate; third SKILL.md standard confirmation.
3. **Info:** Fairford Phase 2 Azure skills ready to import when Phase 2 unblocked — 133 Microsoft Azure skills at VoltAgent/awesome-agent-skills.

---

## Digest Run 15

**Sources processed:** 1
**Files:** `2026-04-23-marketingskills-skill-library.md` (from sources.md digest log)

---

### marketingskills — 23.6k stars, MIT, 40+ SKILL.md Marketing Skills

**Signal strength:** Medium — 4th major production SKILL.md library; confirms de facto standard; one novel architectural pattern (foundational-context-first)
**Source:** coreyhaines31/marketingskills, HN (2026-04-23)

**Key findings:**
- 40+ SKILL.md marketing/growth/sales skills for Claude Code installable via `npx skills` or `.claude-plugin`
- `product-marketing-context` foundational skill pattern: loads shared context (ICP, brand voice, messaging pillars) once at session start, then all domain-specific skills draw from it without repeating the context block
- 4th production SKILL.md library confirming agentskills.io de facto standard (after Anthropic/HF/VoltAgent; this is the first domain-specialist library vs infra/security/general)
- No MCP layer yet = marketingskills-mcp opportunity; skills currently installed as file-based patterns only
- Install pattern: `npx skills install coreyhaines31/marketingskills` — same mechanism as `npx skills` for HF/Anthropic skills; validates skill-manager-mcp's install-from-registry design

**ClaudesCorner impact:**
- **Foundational-context-first pattern:** `product-marketing-context` = domain context loaded once → all skills in that domain become context-aware. This mirrors `task_plan.md` injection in dispatch.py (shared task context → all workers see it). Pattern applicable to any domain-specific skill set in skill-manager-mcp — e.g., a `fairford-context` skill loaded once could give all Fabric/BI skills shared client context without repeating it.
- **skill-manager-mcp import:** 40+ marketing/growth skills are not immediately relevant (no current marketing workload) but the install mechanism and foundational-context pattern are worth noting for ENGRAM documentation.
- **4th SKILL.md standard confirmation:** All 4 major production skill libraries now use SKILL.md format — agentskills.io is clearly the canonical format. No format migration risk for skill-manager-mcp or ENGRAM.
- **No code change required today** — all existing patterns already in place.

**Actionable items:**
1. **Info:** foundational-context-first pattern — consider a `fairford-context` or `numberskills-context` base skill that loads client context for all BI/Fabric skill sessions. Useful when Fairford Phase 2 unblocks.
2. **Backlog (Low):** marketingskills-mcp — wrap as MCP server for Claude Code if marketing/growth work emerges; no priority now.

---

## Actionable Items

| Priority | Action | Status |
|----------|--------|--------|
| Backlog (Low) | teams-sdk-mcp wrapper for Fairford Phase 2 Teams bot delivery; evaluate when Phase 2 scope confirmed | Open — Jason's call |
| Info | pgrust oracle gap: 3rd independent production confirmation of dispatch.py verify oracle principle; existing 3-layer oracle design validated; no code change needed | Open — info only |
| Backlog (Medium) | Evaluate auto-worktree assignment in dispatch.py run_task() — git worktree add per task, clean up on completion; eliminate shared-tree conflicts | Done — _worktree_create/_worktree_remove added; fail-open via DISPATCH_WORKTREES=1 env var |
| Backlog (Low) | Monitor Conductor framework (pgrust orchestration) as dispatch.py v2 worktree layer reference | Open — watch |
| Info | Fastmail MCP: inbound email/calendar/contacts MCP endpoint; Cloudflare Email + Fastmail MCP = complete agent email stack; monitor for SSE/streaming support | Open — info only |
| Backlog (Medium) | CubeSandbox: Windows-friendly REST KVM sandbox; smolvm alternative; E2B-compatible; add to reference memory; check license before Fairford use | Done — reference_cubesandbox.md added |
| Done (memory) | Anthropic MCP Production Guide: 85% token reduction via tool search, intent-grouped tools, OAuth elicitation, Vaults, plugin bundle pattern; add to MEMORY.md | Done — reference_anthropic_mcp_production.md added |
| Backlog (Medium) | fabric-mcp intent-grouped tool: add query_dataset_by_name wrapping workspace+dataset+DAX into one call; reduce Fairford Phase 2 orchestration overhead | Done — query_dataset_by_name added; case-insensitive name resolution; mock+MCP verified |
| Backlog (Low) | Anthropic Vaults as AgentKey replacement for dispatch.py credential governance; monitor for API availability | Open — watch |
| Backlog (Low) | ENGRAM plugin manifest: draft engram_plugin.json bundling SOUL.md + HEARTBEAT.md + memory-mcp + skill-manager-mcp + skills as single installable unit | Open |
| Backlog (Medium) | memory-mcp write-gate: Haiku-based should_memorize() pre-filter before write_memory; prevents noise accumulation; MemReader pattern | Done — _should_memorize() added; MEMORY_WRITE_GATE=1 opt-in; fail-open |
| Info | MemReader weights TBD; monitor HKUDS arxiv/GitHub for code release (same lab as RAG-Anything, DeepTutor) | Open — watch |
| Backlog (Low) | Wire preflight-mcp as CI check for any MCP server moving to HTTP transport; not applicable to current stdio deployments | Open |
| Info | ENGRAM pre-release checklist: Preflight MCP + Sunglasses + AgentKey = 3-tool compliance gate before any component goes network-accessible | Open — info only |
| Info | Design Slop study: 67% of 500 Show HN apps exhibit AI-generated design patterns; agent-facing APIs > UI polish; validates headless/MCP-first architecture for Fairford + ENGRAM | Info only |
| Backlog (High, Jason-blocked) | Fairford Phase 2 Option C: Microsoft Foundry Hosted Agents — Claude Agent SDK + Azure-native + Fabric IQ + hypervisor isolation; present when Jason unblocks Phase 2 | Open — Jason's call |
| Info | reference_microsoft_foundry_agents.md: Foundry Hosted Agents public preview; Claude Agent SDK native; Fabric IQ access; hypervisor-isolated per-session VMs; MCP Toolbox | Done — see below |
| Backlog (Low) | ppt-master-mcp: wrap hugohe3/ppt-master as MCP tool; bi-agent → DAX → PPTX pipeline; $0.08/deck; monitor for Fairford Phase 2 reporting scope | Open — watch |
| Info | reference_ppt_master.md: Claude Code PPTX generator; markitdown-mcp complement; Fairford report export path | Done — see below |
| Backlog (Medium) | dispatch.py BUILD worker: add doom-loop guard instruction — same tool call 3+ times without progress → BLOCKED: doom-loop and halt; ml-intern corrective injection pattern | Done — added to BUILD worker prompt |
| Backlog (Medium) | skill-manager-mcp skill_create: add prompt injection heuristic scan before storing; same Sunglasses pattern; closes pre-ENGRAM security gap | Done — _check_injection() added to skill_create + skill_edit; 11 patterns; fail-closed; v2.5.0 |
| Info | ENGRAM portability: 6-platform SKILL.md convergence confirms agentskills.io format is correct canonical format; no format migration needed | Info only |
| Backlog (Low) | Monitor agensi.io for public API — potential ENGRAM public marketplace discovery endpoint | Open — watch |
| Backlog (Medium) | context-mode MCP: BM25 retrieval over large synthesis/log files; dispatch.py research worker supplement; wire via settings.json when 8000-token budget hit | Open |
| Info | context-mode SQLite event log: session continuity across /clear; complements HEARTBEAT.md for ephemeral task context; monitor for dispatch.py handoff API | Open — watch |
| Backlog (Medium) | Import Trail of Bits security skills from VoltAgent/awesome-agent-skills into skill-manager-mcp — dispatch.py pre-merge security review gate | Open |
| Backlog (Medium) | reference_awesome_agent_skills.md: 1100+ MIT SKILL.md skills; Microsoft Azure (133) for Fairford; Trail of Bits security for dispatch.py; 3rd SKILL.md standard confirmation | Open |
| Info | Fairford Phase 2: Microsoft Azure skills (133) ready to import from VoltAgent/awesome-agent-skills when Phase 2 scope confirmed | Open — Jason's call |
| Info | marketingskills: foundational-context-first pattern (product-marketing-context skill) — applies to Fairford/BI domain context skill when Phase 2 unblocks; 4th SKILL.md library; no code change | Done — Digest Run 15 |
| Backlog (Low) | marketingskills-mcp: wrap as MCP server if marketing/growth workload emerges; low priority now | Open — watch |
