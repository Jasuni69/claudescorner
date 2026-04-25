# Research Synthesis — 2026-04-24

## Digest Run 1

**Sources processed:** 2  
**Files:** `2026-04-24-claude-code-quality-postmortem.md`, `2026-04-24-gpt-55-competitive-signal.md`

---

### Anthropic Claude Code Quality Postmortem — HN 489pts

**Signal strength:** High — directly actionable for dispatch.py audit  
**Three bugs, all now fixed in v2.1.116:**

| Bug | Window | Impact |
|-----|--------|--------|
| Reasoning effort silently downgraded high→medium | Mar 4 – Apr 7 | Tier 2/3 workers may have produced lower-quality plans/code |
| Thinking cache cleared every turn (not once after idle) | Mar 26 – Apr 10 | Long sessions 2-3× token burn + repetitive/forgetful outputs |
| Verbosity cap ≤25/100 words between/after tools | Apr 16 – Apr 20 | 3% coding regression; truncated DAX or incomplete code blocks |

**Key finding:** Bug 2 (`clear_thinking_20251015` with `keep:1`) is the most dangerous pattern for autonomous agentic sessions — survived code review, unit tests, and e2e tests because it was masked by an unrelated server-side experiment. This is a class of failure (server-side parameter shadowing client settings) that local test suites cannot catch.

**ClaudesCorner impact:**
- dispatch.py: verify workers run `claude --version` ≥ v2.1.116 before Fairford Phase 2 deployment
- Session logs from Mar 26–Apr 10 are suspect for token anomalies — anomalous `logs/dispatch-*.txt` files from that window may reflect bug 2, not actual worker regressions
- Long-session monitoring: add session-length or token-burn proxy signal to health_check.py as leading indicator for thinking-cache class failures
- Transparency signal: Anthropic disclosed 3 bugs with precise dates and root causes — this is the correct governance model; validates keeping dispatch.py workers on Anthropic stack vs opaque competitors

---

### GPT-5.5 — Competitive Signal vs Claude Sonnet 4.6 — HN 932pts

**Signal strength:** Medium — competitive landscape, no routing change warranted yet  
**What's known:** Gradual Pro/Enterprise rollout; described as "fast, effective, highly capable" (Willison); no confirmed MCP-native support; benchmarks not yet public.

**HN discussion signals:**
- Community prefers Claude's coding behavior and refusal style over GPT
- Vendor lock-in discussion cuts both ways — Claude is equally non-deterministic
- Open-weight alternatives (Kimi K2.6, Qwen, DeepSeek) mentioned as hedges

**Routing implications:**
- Hold Sonnet 4.6 as dispatch.py default — no tool-call accuracy or DAX benchmark data yet
- If GPT-5.5 ships MCP-native, re-evaluate as Haiku-tier research fallback
- K2VV ToolCall benchmark gates any routing change before Fairford use
- Claude's postmortem transparency (same day as this clip) is a credibility differentiator vs OpenAI's opaque degradation track record

**Watch signals:**
- Willison benchmark post (expected within days — has Codex access)
- Pricing announcement
- MCP support declaration

---

---

## Digest Run 2

**Sources processed:** 2  
**Clips:** `Agent Vault (Infisical)`, `MCP Gateways Aren't Enough (Diagrid)`

---

### Agent Vault — Infisical HTTP Credential Proxy — HN 61pts

**Signal strength:** Medium — fills dispatch.py credential governance gap  
**What it does:** Open-source HTTP credential proxy (MIT); injects secrets at the network layer via HTTP_PROXY; AES-256-GCM at rest; full audit log; zero code changes for any HTTP-based agent.

**Stack fit:**
- Completes the three-layer governance stack: AgentKey (identity) + CrabTrap (outbound filtering) + Agent Vault (secret injection) = no secrets in worker env vars or prompts
- Current dispatch.py gap: API keys are passed as environment variables; Agent Vault would abstract them out of the process env entirely
- Priority: Medium-Low — CrabTrap already wired; AgentKey not yet deployed; Agent Vault is the third layer, not the first

**Action:** Add to pre-Fairford Phase 2 governance checklist alongside AgentKey + CrabTrap. No code change today.

---

### MCP Gateways Aren't Enough — Diagrid Security Analysis

**Signal strength:** Medium — actionable for fabric-mcp before Fairford Phase 2  
**Argument:** MCP gateways lack three things: (1) agent identity (SPIFFE X.509), (2) zero-trust per-tool authorization (OPA), (3) tamper-evident signed execution history. Proposes cryptographically verifiable workflow chain where downstream tools verify prior approval steps occurred.

**Immediate action identified:** Add per-caller scoping to fabric-mcp  
- Currently fabric-mcp has no caller identity — any MCP client that connects gets full workspace access
- Pre-Fairford Phase 2 requirement: scope DAX execution tools to caller identity (even a simple shared secret or bearer token check would eliminate the "any agent can run any DAX query" gap)
- Full SPIFFE/OPA implementation is over-engineering for Phase 2; a `FABRIC_CALLER_TOKEN` env var check is the minimal correct mitigation

**Action:** Add `FABRIC_CALLER_TOKEN` bearer check to fabric-mcp as pre-Phase 2 step. Medium priority.

---

---

## Digest Run 3

**Sources processed:** 3  
**Clips:** `Checkmarx supply chain compromise`, `Checkmarx agentic guardrails`, `DeepSeek V4 Pro`

---

### Checkmarx Supply Chain Compromise — HN 666pts

**Signal strength:** High — direct CI/CD action required  
**What happened:** Checkmarx's own GitHub Action (`ast-github-action@v2.3.35`), DockerHub KICS image, and two VS Code extensions were backdoored on April 22, 2026. Only newly published versions were malicious; prior safe versions were preserved.

**Key finding:** `uses: action@tag` is unsafe — tag can be silently overwritten post-publication. Only SHA pinning is safe.

**ClaudesCorner impact:**
- dispatch.py workers: any GitHub Actions in CI pipelines should be pinned to commit SHA
- MCP server CI (fabric-mcp, memory-mcp, skill-manager-mcp): audit GitHub Action versions in any build configs
- CrabTrap validation: outbound `checkmarx.cx` calls would have been blocked — confirms MITM proxy value
- Fairford Phase 2: add supply chain audit (SHA-pinned actions + SBOM) to pre-deployment checklist

---

### Checkmarx Agentic Guardrails — Two-Loop Security Architecture

**Signal strength:** Medium — validates existing stack, adds SBOM gap  
**Core model:** Inner loop (prevention at input) + outer loop (enforcement at integration stage). Maps directly to Sunglasses (inner) + CrabTrap/AgentKey (outer).

**Six controls vs ClaudesCorner:**

| Control | Equivalent |
|---|---|
| Govern AI assets (inventory) | AgentKey per-worker credential scoping |
| Risk-based prioritization | bi-agent 3-layer oracle |
| Supply chain controls (SBOM) | **Gap** — no AI-BOM for MCP server deps yet |
| Agentic guardrails (identity + audit) | AgentKey + CrabTrap + Sunglasses |
| Standardize prompts | dispatch.py system prompts + task_plan.md |
| Operational metrics | kpi-monitor + HEARTBEAT log |

**Gap identified:** No SBOM/AI-BOM for MCP server transitive dependencies. Before Fairford Phase 2: enumerate and lock deps for fabric-mcp, memory-mcp, skill-manager-mcp.

---

### DeepSeek V4 Pro — Open-Weight Frontier Model

**Signal strength:** High — changes dispatch.py routing options and Fairford cost model  
**Architecture:** 1.6T total / 49B activated (MoE + CSA), MIT license, 1M context window, 27% inference FLOPs vs V3.2.

**Benchmark highlights (V4-Pro-Max):**
- LiveCodeBench 93.5% (vs Claude Opus 4.6 91.7%)
- Terminal-Bench 2.0 67.9% (stronger than Kimi K2.6 66.7%)
- MCPAtlas Pass@1 73.6% — first-class MCP tool-use benchmark included
- IMOAnswerBench 89.8%

**Routing implications:**
- MIT license + lower inference cost = viable Sonnet 4.6 fallback when Anthropic rate limits hit
- MCPAtlas validates tool-use; still needs K2VV ToolCall F1 before any Fairford routing
- Fairford Phase 2: MIT enables self-hosted on Foundry VMs — changes cost model significantly
- bi-agent: evaluate V4-Pro for DAX generation scaffold tier (stronger coding benchmark)
- ENGRAM: 1M context fits full SOUL.md + HEARTBEAT.md + session history in one pass
- SimpleQA-Verified 57.9% — factual recall gap; not suitable for research workers without oracle

**Hold on Sonnet 4.6 default** — K2VV ToolCall F1 test required before any routing change.

---

---

## Digest Run 4

**Sources processed:** 1
**Clips:** `OpenAI Agent Skills (openai/skills)`

---

### OpenAI Agent Skills — 5th Major SKILL.md Org — #8 Python Trending

**Signal strength:** Medium — ecosystem confirmation, no code change needed  
**What it is:** OpenAI's official public skills repo (`openai/skills`, 17.4k stars, #8 Python trending). Uses the same SKILL.md folder format as Anthropic, HuggingFace, VoltAgent, and marketingskills — without coordination between any of them.

**Key finding:** SKILL.md is now confirmed as the de facto cross-platform agent skill standard, adopted independently by 5 major orgs:

| Org | Repo | Stars | Notes |
|-----|------|-------|-------|
| Anthropic | anthropics/skills | 120k | First-party canonical |
| HuggingFace | huggingface/skills | 10.3k | governance gap found + fixed in skill-manager-mcp v2.5.0 |
| VoltAgent | awesome-agent-skills | 17.7k | 1100+ curated skills, 50 orgs |
| marketingskills | coreyhaines31/marketingskills | 23.6k | foundational-context-first pattern |
| **OpenAI** | **openai/skills** | **17.4k** | `$skill-installer` install pattern |

**Confirmed gap — skill-manager-mcp is the runtime neither OpenAI nor Anthropic has:** All five repos publish skills but none ships a cross-platform semantic-search runtime. skill-manager-mcp v2.5.0 (FTS5 + vector + `agent_activation_allowed` + injection guard) is the only existing runtime that can install and activate skills from any of these sources.

**ENGRAM portability:** Claude Code + Codex + Cursor all consume SKILL.md format. ENGRAM distribution now has a concrete compatibility story: SOUL.md + HEARTBEAT.md + memory-mcp + skill-manager-mcp runtime = works on all 5 platforms without changes.

**Action:** Info/Done — no code change needed. ENGRAM README should reference all 5 orgs as portability proof.

---

---

## Digest Run 5

**Sources processed:** 2
**Clips:** `What's Missing in the Agentic Story (mnot.net)`, `AI Enablement Requires Managed Agent Runtimes (12gramsofcarbon.com)`

---

### What's Missing in the Agentic Story — Mark Nottingham (IETF Chair), mnot.net

**Signal strength:** Medium — strategic framing; validates existing governance stack  
**Core argument:** The trust framework that makes browsers trustworthy (W3C/IETF user-agent standards, TLS, explicit permission dialogues) does not exist for AI agents. Permission sprawl is an architectural gap, not a policy problem — agents accumulate capabilities without the formal delegation chain that browsers have.

**Relevant observations:**
- Browsers have 30+ years of standardized consent semantics (Origin, SameSite, CORS, Permissions API) that agents lack entirely
- Agent "permission scopes" today are informal textual descriptions with no enforcement layer
- IETF is beginning to discuss agent trust anchors but no RFC yet

**ClaudesCorner fit:**
- Validates AgentKey (identity layer) + CrabTrap (outbound enforcement) + `deny:` frontmatter in dispatch.py workers as a pre-standards governance stack
- ENGRAM positioning: "portable harness with explicit permission boundaries = pre-IETF-standard implementation"; this is the differentiator story when IETF/W3C eventually ship agent trust specs — ENGRAM will be API-compatible ahead of schedule
- No immediate code change needed; this is positioning context

---

### AI Enablement Requires Managed Agent Runtimes — 12gramsofcarbon.com

**Signal strength:** Medium — enterprise framing; ENGRAM pitch crystallized  
**Core blockers identified:**
1. **CLAUDE.md vs AGENTS.md fragmentation** — every team writes their own instructions, no shared context, no versioning, impossible to audit
2. **Context degradation at scale** — agent sessions accumulate stale context; no mechanism to compact or expire old instructions
3. **Credential leakage via skills** — skills can read and expose credentials from session context if not scoped

**Two camps:** Fully managed (Devin/Twill — buy the whole stack) vs internal build (Stripe/Uber — build on primitives). Argument: most enterprises need internal build because regulated data can't leave.

**ENGRAM pitch crystallized from this clip:**
> "CLAUDE.md works for one developer. ENGRAM works for a team."

- Fragmentation gap → skill-manager-mcp: shared, versioned, semantically searchable skill store; install once, all agents draw from it
- Context degradation → deferred-load pattern: memory-mcp only injects context when semantically relevant; HEARTBEAT.md as always-fresh session anchor
- Credential leakage → deny: worker scope + AgentKey: skills are scoped, credentials never appear in skill bodies

**Action:** This is a positioning/pitch synthesis, no code change. However: the "credential leakage via skills" observation is a gap worth checking in skill-manager-mcp — skill bodies are not currently scanned for credential patterns (API keys, tokens, passwords). Add to backlog.

---

## Digest Run 6

**Sources processed:** 5  
**Clips:** `Affirm Retooled for Agentic Dev (2026-04-24c)`, `safer shell guardrail`, `exe.dev bare-metal cloud`, `Anthropic + NEC Japan`, `Willison LiteParse browser PDF`  
Note: `agent-user-agent-framework.md` = duplicate of mnot.net clip already digested in Run 5.

---

### Affirm Retooled for Agentic Software Development — HN 9pts

**Signal strength:** High — largest public case study of Claude Code at org scale (800 engineers)  
**Key facts:** Feb 2026 forced one-week sprint; 92% agent-assisted PRs by end of week; 60% of all PRs agent-assisted 4 months later; 58% weekly merge volume YoY; $200k token budget (~$250/engineer), 70% actual spend.

**Patterns independently discovered by Affirm:**
- **one-task-one-session-one-PR** = dispatch.py single-task-per-worker architecture, validated at org scale
- **Multi-level context files** (conventions/domain/team decisions) = SOUL.md + HEARTBEAT.md + daily logs pattern
- **Internal skill marketplace** = skill-manager-mcp purpose, confirmed at enterprise scale
- **Fragmented docs as top bottleneck** — HEARTBEAT.md is load-bearing, not optional

**Checkpoint model:** Plan → Review → Execute → Verify → Review → Deliver. Explicit human decision points at intent, plan approval, code review, and merge — automates execution without removing humans from design.

**ClaudesCorner fit:** No code change needed — Affirm independently validated the existing architecture at 800-engineer scale. Primary value: ENGRAM pitch evidence ("CLAUDE.md works for one dev, ENGRAM works for a team" — Affirm built a team-CLAUDE.md and an internal skill marketplace from scratch in weeks).

---

### safer — Read-Only-by-Default Shell Guardrail — HN 1pt (Show HN)

**Signal strength:** Medium — behavioral layer complement to existing governance stack  
**What it does:** Go binary wrapping shell commands; enforces read-only-by-default; known safe commands pass automatically; anything else blocked unless agent declares explicit capability flag (`--data-write`, `--data-delete`, `--env-persistent`, etc.); exits code 2 on block.

**Architecture position:** Pre-execution behavioral check. Not a sandbox (no VM, no network filtering). Prompt-level `deny:` clauses can drift with model; `safer` enforces at OS level and cannot be overridden by model.

**Stack fit:**
- CrabTrap: outbound HTTP filtering
- AgentKey: identity + credential governance
- AgentRQ: human-in-loop escalation
- **safer: pre-execution shell command guardrail** ← new layer

**Action:** Backlog (Low) — wire `safer` as shell wrapper in dispatch.py exec calls. Workers that need destructive capability must declare it in task_plan.md capability block; makes destructive intent visible before execution rather than buried in execution logs. License unclear — check before production use.

---

### exe.dev — Bare-Metal Cloud Built for AI Agent Workloads — HN 1045pts

**Signal strength:** Medium — infrastructure signal, no immediate action  
**Author:** David Crawshaw (SQLite Go bindings, Tailscale co-founder)  
**Core argument:** Current cloud abstractions (per-VM billing, remote block storage, egress markup) are misaligned with agent workloads. exe.dev separates compute from VMs, uses local NVMe (~500k IOPS vs EC2's $10k/month for 200k IOPS), and eliminates egress markup.

**Agent connection:** Every context window spent fighting AWS API complexity is wasted inference. dispatch-style parallel workers that spawn many short-lived tasks need resource granularity below VM level.

**ClaudesCorner fit:** Watch signal only (private/early access). If Anthropic rate limits push open-weight fallbacks onto self-hosted infra, local NVMe + dense packing matters. Complements CubeSandbox (isolation layer) at the economics layer. Monitor for public pricing before Fairford Phase 2 infrastructure decisions.

---

### Anthropic + NEC — Japan's Largest AI Engineering Workforce — Anthropic News

**Signal strength:** Medium — enterprise validation, Fairford positioning  
**Scale:** ~30,000 NEC Group employees; Claude Opus 4.7 + Claude Code + Claude Cowork; Finance/manufacturing/cybersecurity/local government verticals via NEC BluStellar Scenario.

**Fairford signal:** Enterprise Claude Code at 30k-employee scale in regulated verticals (finance, local government) validates Max-tier pricing as viable at scale. No MCP mention in announcement — gap opportunity for fabric-mcp / skill-manager-mcp as enterprise tooling layer on top of Claude Code.

**Action:** Watch signal — monitor NEC BluStellar Scenario case studies for workflow patterns worth adapting.

---

### Willison — LiteParse for the Web: Browser-Native PDF Extraction — simonwillison.net

**Signal strength:** Medium — markitdown-mcp upgrade path  
**What it is:** Browser-native PDF text extractor built via Claude Code vibe-coding (59 min, zero manual review). PDF.js + Tesseract.js OCR for image-based PDFs. 100% client-side, multi-column reading-order heuristics, bounding-box JSON.

**markitdown-mcp fit:**
- Current markitdown-mcp: handles text-native PDFs well
- LiteParse adds: multi-column reading-order correction + scanned OCR via Tesseract.js
- Bounding-box JSON = source-attribution metadata for RAG chunks (page/column provenance)
- Chandra 2 (clipped 2026-04-18): handwriting + complex tables + 90 languages
- Together: full scanned-doc coverage for Fabric RAG pipeline

**Vibe-coding signal:** 59 min zero-review build = Willison benchmarking Claude Code dispatch-style leaf-node PDF tasks. Quality sufficient for production tool output.

**Action:** Backlog (Low) — add `convert_scanned` tool candidate to markitdown-mcp (wrapping Tesseract.js or Chandra 2); evaluate LiteParse bounding-box format as source-attribution schema for Fabric RAG chunks.

---

---

## Digest Run 7

**Sources processed:** 2
**Clips:** `2026-04-24-browser-harness-self-healing-llm-browser.md`, `2026-04-24-claude-critics-token-issues-quality.md`

---

### Browser Harness — Self-Healing LLM Browser Automation — HN 11pts (Show HN)

**Signal strength:** Medium — dispatch.py browser worker primitive candidate
**What it is:** browser-use/browser-harness (6.2k stars, MIT); 592 lines of Python; connects directly to Chrome via CDP (one WebSocket, no framework overhead); agent writes missing helper code mid-task = genuine self-healing (not retry logic).

**Architecture vs alternatives:**

| Tool | Mechanism | Overhead |
|------|-----------|----------|
| AI Subroutines (2026-04-18) | Record-once/replay-N | Zero tokens in replay, requires pre-recording |
| Chrome DevTools MCP (2026-04-18) | 29 tools via MCP | Heavier, needs npx |
| **Browser Harness** | CDP-direct + live agent-written helpers | ~592 lines, self-healing mid-task |

**Stack fit:**
- dispatch.py browser worker: minimal footprint, auditable, Windows-compatible (no Playwright dependency chain)
- Pair with CrabTrap for safe external browsing
- browser-use team = maintained; MCP integration likely upcoming (same team as browser-use MCP)

**Action:** Backlog/Medium — evaluate as dispatch.py browser worker. License: MIT (clean). No code change today.

---

### Claude Critics — Token Issues, Quality, Support — HN 170pts

**Signal strength:** Medium — confirms existing architectural decisions; surfaces token budget gap
**Core complaints:** 100% token spike after two Haiku queries; cache expiration forcing codebase re-reads; Opus lazy workarounds consuming 50% of five-hour allowance; support non-response.

**ClaudesCorner calibration:**

| Complaint | ClaudesCorner disposition |
|-----------|--------------------------|
| Token spike after small Haiku queries | Consistent with thinking-cache bug (v2.1.116 fix); dispatch.py `_check_claude_version()` already catches pre-fix versions |
| Cache expiration re-reading entire codebases | `cache_control=ephemeral` in bi-agent avoids this; interactive Claude (not dispatch.py workers) affected |
| Opus lazy workarounds burning tokens | Sonnet 4.6 default on dispatch.py is correct; this is the documented Opus 4.7 token inflation failure mode |
| "Monthly usage limit" confusion | Consistent with Claude Code Pro removal A/B test (2026-04-22) — not a systemic reliability issue |
| Qwen3.5-9B viable locally | Validates fallback strategy; Kimi K2.6 + DeepSeek V4-Pro added as stronger fallbacks |

**Gap identified:** No per-run token budget hard cap in dispatch.py workers. Author's 50%-in-one-task burn confirms the risk. Current protection: model tier (Sonnet 4.6) + cost estimate only. A `MAX_TOKENS_PER_RUN` env var guard in `run_task()` would prevent runaway sessions.

**Action:** Backlog/Low — add `MAX_TOKENS_PER_RUN` hard cap guard to dispatch.py `run_task()` (via `--max-tokens` flag to claude.exe). No code change today.

---

## Actionable Items

| Item | Priority | Status |
|------|----------|--------|
| Verify dispatch.py workers run `claude` ≥ v2.1.116 | High | **Done** — version warn added to dispatch.py 2026-04-24 |
| Add `FABRIC_CALLER_TOKEN` bearer check to fabric-mcp | Medium | **Done** — `_authorized` flag + initialize gate added to server.py 2026-04-24 |
| Add Agent Vault to pre-Fairford governance checklist | Medium | Backlog — after CrabTrap + AgentKey deployed |
| Review dispatch logs from Mar 26–Apr 10 for anomalous token burn | Medium | **Closed** — no logs exist for that period (logs start Apr 16); bug window predates retention |
| Add session-length / token-burn proxy signal to health_check.py | Low | **Done** — `check_dispatch_activity()` added to checks.py 2026-04-24: 24h run count + KB + staleness flag |
| Hold Sonnet 4.6 as dispatch.py default; await GPT-5.5 K2VV benchmark | Medium | Standing hold |
| Monitor Willison benchmark post on GPT-5.5 (days away) | Medium | Watch |
| SHA-pin all GitHub Actions in MCP server CI pipelines | High | **N/A** — no .github/workflows in first-party MCP servers; note in mcp-sbom.json |
| Enumerate + lock MCP server transitive deps (SBOM/AI-BOM) | Medium | **Done** — requirements.txt added to all 5 MCP servers; projects/mcp-sbom.json created 2026-04-24 |
| Benchmark DeepSeek V4-Pro via KVV ToolCall F1 before Fairford routing | Medium | Backlog — gate before any routing change |
| Compare Haiku 4.5 vs V4-Flash on dispatch.py leaf nodes (cost/latency) | Low | Backlog |
| OpenAI Agent Skills — ENGRAM README portability claim (5 orgs) | Info | **Done** — digested 2026-04-24; no code change |
| Agentic trust standards — IETF/W3C watch; ENGRAM pre-standards impl | Info | **Done** — digested 2026-04-24; no code change |
| Add credential-pattern scan to skill-manager-mcp skill_create/skill_edit | Low | **Done** — `_check_credentials()` + `_CREDENTIAL_RE` added to server.py v2.6.0 2026-04-24; 10 patterns (sk-/ghp_/JWT/Bearer/password=/secret=); fail-closed; allowlist for placeholders |
| safer shell guardrail — wire in dispatch.py exec | Low | Backlog — check license; adds OS-level `deny:` enforcement |
| exe.dev bare-metal cloud — watch for public pricing | Low | Watch — private access; relevant if open-weight self-hosting needed |
| NEC BluStellar Scenario case studies | Low | Watch — enterprise workflow patterns for Fairford |
| markitdown-mcp: `convert_scanned` tool (Tesseract.js / Chandra 2) | Low | Backlog — LiteParse bounding-box format as RAG source-attribution schema |
| Browser Harness — evaluate as dispatch.py browser worker | Medium | Backlog — MIT, 592 lines, CDP-direct, self-healing; pair with CrabTrap |
| dispatch.py: add `MAX_BUDGET_USD` hard cap guard to `run_task()` | Low | **Done** — `--max-budget-usd` flag wired in run_task() 2026-04-24; fail-open when unset; `--max-tokens` doesn't exist in claude.exe, `--max-budget-usd` is the correct flag |
| CC-Canary weekly health check — wire `/cc-canary 30d` as dispatch.py worker | Low | Backlog — retrospective Mar26–Apr10 regression possible; pre/post v2.1.116 inflection; zero network |
| Design.md — add as recommended ENGRAM scaffold artifact | Low | Backlog — alongside SOUL.md/HEARTBEAT.md for projects with UI; Fairford Phase 2 UI root |
| kpi-monitor: evaluate Driggsby MCP pattern (expose data as MCP tools, Claude scheduled routine) | Low | Backlog — cleaner than polling loop; validates fabric-mcp architecture |
| Google $40B Anthropic deal — Bedrock+Vertex dual routing in dispatch.py | Info | Watch — 2027 TPU expansion closes compute scarcity; dual-provider routing becomes viable |

---

## Digest Run 8 — 2026-04-25

**Clips processed**: cc-canary, design.md, claude-code-routines-financial, google-40b-anthropic-investment (4 clips from 2026-04-24d batch)

### CC-Canary — Claude Code Session Drift Detection (delta-hq/cc-canary, MIT, Python, HN 4pts)

Local JSONL scanner for `~/.claude/projects/` session logs. Tracks 7 quality metrics: Read:Edit ratio, reasoning loops, thinking redaction, token burn per turn, API calls per prompt, write share. Detects inflection points via argmax(Δ) with 0.75σ floor. Produces Markdown report or dark-theme HTML dashboard. Zero network, no telemetry, no daemon.

**Signal**: Fills the dispatch.py quality-regression blind spot — long autonomous sessions accumulate drift invisibly. The Mar26–Apr10 thinking-cache bug (API turns spike + token burn) would have registered as a confirmed inflection in 90d retrospective. Read:Edit ratio is a direct proxy for the Levenshtein over-editing benchmark (2026-04-22). Windows-compatible via Python.

**Action**: Backlog/Low — wire `/cc-canary 30d` as weekly dispatch.py worker health check; compare pre/post v2.1.116. No code change today.

---

### Design.md — Google Labs Visual Identity Spec for Coding Agents (google-labs-code/design.md, Google Labs, HN 27pts)

Format spec: YAML front matter (exact design tokens — colors, typography, spacing) + Markdown prose (rationale). Exports to Tailwind + W3C DTCG. CLI lint/validate tool. Independent convergence with Anthropic's Claude Design handoff bundle — both solve the same problem (giving agents persistent, structured design intent) via different delivery mechanisms (checked-in file vs conversation bundle).

**Signal**: Third independent convergence (after Claude Design Apr 2026 + "design slop" research Apr 2026) validating code-first design over Figma pipelines. File-based approach fits ENGRAM: portable, version-controlled, queryable by vectordb. For Fairford Phase 2 UI layer: author `DESIGN.md` at project root eliminates Figma dependency.

**Action**: Backlog/Low — (1) add `DESIGN.md` as recommended scaffold artifact in ENGRAM alongside SOUL.md/HEARTBEAT.md for projects with UI components; (2) author Fairford `DESIGN.md` as part of Phase 2 UI work. No code change today.

---

### Claude Code Routines for Financial Monitoring (driggsby.com, HN 18pts)

Author built a daily financial monitor using Claude Code routines + custom MCP server (Rust/Plaid). Schedule → Claude session → MCP tool calls → Gmail draft. Detects transaction anomalies (double-charges, subscription price changes). Key insight: routines appear as normal Claude Code sessions — fully inspectable. "Almost too easy to set up": prompt + MCP connector + schedule time.

**Signal**: Consumer-scale independent validation of dispatch.py one-prompt-one-session-one-task pattern. Inspectability (routine = normal session) is the key UX insight: no separate monitoring UI needed. MCP-as-zero-infra-automation-primitive directly validates fabric-mcp. Alert fatigue (prompt refinement to avoid over-alerting) is the next challenge — same issue dispatch.py workers face with verbose output gates.

**kpi-monitor upgrade path**: The Driggsby pattern (expose domain data as MCP tools → scheduled Claude routine → anomaly detection) is architecturally cleaner than kpi-monitor's Python polling loop. If kpi-monitor needs a Claude-powered analysis layer, this is the reference.

**Action**: Backlog/Low — evaluate Driggsby MCP pattern as kpi-monitor v2 architecture. No code change today.

---

### Google $40B Anthropic Investment (HN 118pts)

$10B immediate at $350B valuation; $30B contingent. 5GW Google Cloud TPU capacity over 5 years (+ 3.5GW Broadcom TPUs from 2027). Context: $5B Amazon + $100B AWS compute already committed. Anthropic facing "widespread complaints about Claude use limits" — this is the direct fix. IPO considered October 2026.

**Signal**: Compute scarcity window is real but closing — 2027+ TPU expansion weakens the short-parallel batching argument (though architecture remains correct for cost efficiency). AWS ($5B+$100B) and Google ($40B+5GW) dual-dependence confirmed → Bedrock + Vertex AI are both viable Claude API paths for dispatch.py. October 2026 IPO window = Anthropic will prioritize enterprise reliability/pricing stability for next 6 months (favorable for locked dispatch.py API contracts).

**Action**: Info/Watch — dual-provider Bedrock+Vertex routing in dispatch.py is a medium-term backlog item. No code change today.
