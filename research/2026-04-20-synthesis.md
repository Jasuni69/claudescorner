# Research Synthesis — 2026-04-20

## Digest Run 1

**Sources processed:** 1  
**Files:** `2026-04-20-rigor-evaluation.md`

---

### Rigor Proxy — dispatch.py Integration Evaluation

**Signal strength:** High — closes a backlog item with a concrete NO-GO verdict  
**Source:** Internal evaluation (autonomous, triggered by 2026-04-19 synthesis backlog item)

**Findings:**
- "Rigor" as a publicly available MITM proxy with Rego policy enforcement cannot be verified — likely private beta or vaporware
- Three public alternatives evaluated (Microsoft Agent Governance Toolkit, ProxyClawd, ClawShield) — none fit dispatch.py subprocess architecture well
- Core dispatch.py mismatch: workers write output to log files (post-hoc), not streamed; MITM proxy intercepts API layer, not output layer
- Verify oracle pattern already in dispatch.py workers covers the same correctness concern at zero infra cost
- Windows TLS termination friction (self-signed CA, NODE_EXTRA_CA_CERTS) adds non-trivial setup overhead without admin rights
- 300s worker timeout is sensitive to proxy startup and per-request latency overhead

**Decision: Close backlog item**
- Status: Researched → Deferred pending public Rigor release
- Existing verify oracle approach is the correct mitigation
- Revisit only if public repo surfaces with confirmed HTTPS_PROXY compat + benchmarked latency + free self-hosted tier

**ClaudesCorner impact:**
- No code changes needed
- dispatch.py verify clauses (added 2026-04-19) already correct solution
- MEMORY.md entry for `reference_rigor_proxy.md` should note NO-GO verdict for dispatch.py integration

---

## Actionable Items

| Priority | Action | Status |
|----------|--------|--------|
| Done | Evaluate Rigor proxy for dispatch.py | Closed — NO-GO, verify oracle sufficient |
| Backlog | Revisit Rigor if public repo ships | Open — no ETA |
| High | Adopt agentskills.io SKILL.md frontmatter as canonical format in skill-manager-mcp | Open — Hermes + anthropics/skills both converge on this spec |
| High | Add `max_context_tokens` soft cap to dispatch.py worker config | Open — context-engineering 5-component model identifies unbounded context as risk |
| Medium | Consider context-engineering 5-component model as ENGRAM architectural framing | Open — Corp(1-3) + Output(4) + Enforcement(5) maps cleanly to ENGRAM stages |

---

## Digest Run 2

**Sources processed:** 2  
**Files:** `2026-04-20-hermes-agent-102k.md`, `2026-04-20-context-engineering-runnable.md`

---

### Hermes Agent — 102k Stars, Self-Improving Loop

**Signal strength:** High — largest weekly GitHub gain today (+38k); convergent validation of ENGRAM architecture  
**Source:** github.com/NousResearch/hermes-agent

**Findings:**
- Closest public analog to ClaudesCorner at production scale: autonomous skill generation, 5-layer memory, sub-agent spawning, MCP-compatible, agentskills.io standard
- Architecture mapping is near-1:1 with ClaudesCorner: skill-manager-mcp ↔ skill generation, memory-mcp ↔ FTS5 recall, dispatch.py ↔ sub-agent spawn, SOUL.md ↔ Honcho user modeling
- **Key differentiator**: Hermes skill store is file-based; skill-manager-mcp adds semantic vector search — meaningful moat
- **Key differentiator**: No fabric/BI MCP layer in Hermes — fabric-mcp is a unique capability gap Hermes doesn't cover
- **Convergence signal**: Hermes + anthropics/skills both use agentskills.io SKILL.md YAML frontmatter as the canonical skill format — this is the emerging open standard; skill-manager-mcp should adopt it as primary format

**Action:** Update skill-manager-mcp skill frontmatter spec to align with agentskills.io SKILL.md format (title, description, version, tools, parameters YAML block). No behavioral change — format alignment only.

---

### Context Engineering — 5-Component RAG+Enforcement Model

**Signal strength:** Medium — low star count (27) but articulates a pattern with 4 independent convergent signals  
**Source:** github.com/outcomeops/context-engineering (HN 17pts)

**Findings:**
- Names and formalizes what Willison (×2), Remoroo, and OpenSpec all pointed at independently: output enforcement/oracle is a distinct step after generation, not implicit in retrieval
- 5-component model: Corpus → Retrieval → Injection → Output → Enforcement
- dispatch.py workers currently cover steps 1-4 (memory-mcp retrieval, context injection, output generation); step 5 (enforcement oracle) is the `verify:` section added 2026-04-19 — confirms that addition was correct
- **New finding**: worker context is unbounded — `max_context_tokens` budget per worker is missing; "curate and limit what agent sees" is a distinct engineering step, not just a prompt tip
- **New finding**: "lost in the middle" ordering — context injection order in dispatch.py worker prompts matters for recall quality; most critical context should be at start or end of context block, not middle

**Action:** Add `max_context_tokens: 8000` soft cap to dispatch.py DEFAULT_AUTONOMOUS_TASKS worker config; document context injection ordering principle in dispatch.py header comments.

---

## Digest Run 3

**Sources processed:** 2  
**Files:** `2026-04-20-browser-use-agent-captcha.md`, `2026-04-20-willison-token-counter-model-comparison.md`

---

### Browser Use Agent-CAPTCHA — Reverse Identity Primitive

**Signal strength:** Medium — 56 HN pts; novel capability gap framing  
**Source:** browser-use.com/posts/prove-you-are-a-robot

**Findings:**
- Browser Use built a reverse-CAPTCHA that excludes humans and admits AI agents — exploits the agent's advantage at parsing obfuscated/scrambled text over humans
- Mechanism: math problem encoded in visually scrambled multilingual text; agent reads garbled representation, recovers problem, solves before expiration
- Solves the agent onboarding identity problem without OAuth or email
- **Two-layer model emerging**: AgentKey (credential governance) handles ongoing auth; agent-CAPTCHA handles *initial* agent-to-service onboarding — complementary layers
- dispatch.py workers currently have no self-authentication primitive — this gap grows as more services adopt agent-native access gates
- NP-hard TSP bonus challenge unlocks enterprise tier — interesting signal that services are designing access tiers around agent computational capability

**Action (Backlog):** Monitor for open-source release; add `solve_agent_captcha` capability note to dispatch.py worker design docs; file as AgentKey complement in ENGRAM bootstrap onboarding story.

---

### Willison Token Counter — Opus 4.7 Inflation Confirmed

**Signal strength:** High — direct measurement data contradicts Anthropic's stated ceiling; directly affects dispatch.py cost model  
**Source:** simonwillison.net/2026/Apr/20/claude-token-counts/

**Findings:**
- Opus 4.7 text inflation measured at **1.46×** vs Opus 4.6 — Anthropic's stated ceiling was "roughly 1.0–1.35×"; real-world 8% above ceiling
- Image inflation measured at **3.01×** (driven by higher resolution support up to 2,576px long edge)
- Pricing unchanged ($5/$25/M tokens) — cost increase is purely volumetric; identical workload costs ~40% more on Opus 4.7 text, up to 3× more for images
- **dispatch.py model tier decision confirmed**: Sonnet 4.6 as default worker model; Opus 4.7 only for planning/synthesis where reasoning depth justifies cost
- **bi-agent schema caching**: `cache_control=ephemeral` on schema block pays off faster at 1.46× inflation — existing implementation is correct
- **markitdown-mcp + image workflows**: route image-heavy documents through Haiku 4.5 or 4.6 until 4.7 image inflation is better characterized for specific doc types
- **token-dashboard**: should add 1.46× multiplier display when showing Opus 4.7 cost estimates vs 4.6 baseline

**Action (Medium):** Add 1.46× inflation multiplier flag to token-dashboard cost display; document Opus 4.7 tier policy in dispatch.py header (Sonnet 4.6 default, Opus 4.7 = planning gate only).

---

## Updated Actionable Items

| Priority | Action | Status |
|----------|--------|--------|
| Done | Evaluate Rigor proxy for dispatch.py | Closed — NO-GO, verify oracle sufficient |
| Backlog | Revisit Rigor if public repo ships | Open — no ETA |
| High | Adopt agentskills.io SKILL.md frontmatter in skill-manager-mcp | Open — Hermes + anthropics/skills converge |
| High | Add `max_context_tokens: 8000` soft cap to dispatch.py worker config | Open |
| Medium | Context-engineering 5-component model as ENGRAM architectural framing | Open |
| Medium | Add 1.46× Opus 4.7 inflation multiplier to token-dashboard | Open |
| Medium | Document Opus 4.7 tier policy in dispatch.py header | Open |
| Backlog | Monitor browser-use agent-CAPTCHA for OSS release | Open |

---

## Digest Run 4

**Sources processed:** 4  
**Files:** `2026-04-20-openclaw-to-claude-code-migration.md`, `2026-04-20-openclaw-memory-degradation-patterns.md`, `2026-04-20-openclaw-api-cost-tracking.md`, `2026-04-20-openclaw-checkpoints-skill.md`

---

### OpenClaw → Claude Code Migration — ENGRAM Positioning Story

**Signal strength:** High — real user rebuilt months of OpenClaw work in 2 weeks as Claude Code plugin; exact ENGRAM bootstrap pattern in the wild  
**Source:** r/openclaw (HN-crossposted)

**Findings:**
- User lost their OpenClaw bot (Claude Max token cutoff April 4). Rebuilt as Claude Code plugin in 2 weeks preserving: personality, memory, skills, crons, WhatsApp bridge
- Confirms SOUL.md+HEARTBEAT.md+skills pattern is the right primitive — this user independently arrived at the same architecture
- ENGRAM is the open-source packaging of exactly this migration path; this thread is the use case story
- Claude Max plan covers the agent without extra API billing — validates subscription-first architecture

**ClaudesCorner impact:** ENGRAM README needs a "migration from OpenClaw" section. This post is the primary testimonial.

---

### OpenClaw Memory Degradation — ROLE.md Sub-Agent Pattern

**Signal strength:** High — documented architecture for multi-company agent installs; direct parallel to HEARTBEAT.md sub-agent design  
**Source:** r/openclaw power user (3 companies, CMO/CFO/CTO agents)

**Findings:**
- 4.11→4.14 regression: excessive tool-call chains, slower responses, higher token climb — mitigated via ROLE.md per-agent boundary
- Per-company ROLE.md = per-scope system prompt boundary — equivalent to a SOUL.md sub-agent variant
- Dashboard: pulls MS Teams + Outlook + manual tasks → unified task creation with priority tiers — direct parallel to HEARTBEAT.md pending task queue
- Token climb symptom = goal drift: agent loses track of original objective across long tool chains
- Multi-company install pattern = Fairford reference: separate agent instances per client with shared infra

**ClaudesCorner impact:** HEARTBEAT.md sub-agent variant (ROLE.md) worth formalizing for Fairford multi-client deployment.

---

### OpenClaw API Cost Tracking — Model Routing Validation

**Signal strength:** High — real cost data (£20/day burning, £450 in 5 weeks) quantifies model tier importance  
**Source:** r/openclaw community cost thread

**Findings:**
- Stacked multi-agent workflows at flagship model = expensive fast; £20/day is unsustainable for personal projects
- Haiku delivers close-to-Sonnet results on narrow, well-defined tasks at fraction of cost — validated by multiple users
- openmark-router plugin does semantic routing to best model per task — reduces cost without quality loss
- Claude 4.7 +30-45% token inflation confirmed by this community independently (cross-validates Willison measurement)
- dispatch.py model tier policy (Sonnet 4.6 default, Haiku for leaf nodes) is the correct response to this cost reality

**ClaudesCorner impact:** Add Haiku 4.5 as explicit third tier in dispatch.py model policy (current: Sonnet default, Opus for planning; add Haiku for narrow/structured tasks like DAX validation, format checks).

---

### OpenClaw Checkpoints Skill — Pre-Planning Oracle Pattern (4th Confirmation)

**Signal strength:** High — 4th independent confirmation of the plan-before-execute → checkpoint → verify pattern  
**Source:** r/openclaw skill thread

**Findings:**
- Checkpoints skill forces agent to write full actionable plan + markdown checkbox file before any execution; works with smaller local models
- AGENTS.md pattern: separate planning session writes TODO with checkboxes and definition of done (tests + lint + changelog); agent reads AGENTS.md each restart
- Pre-planning separates planning-Claude from executing-Claude — identical to dispatch.py SPEC→BUILD→VERIFY protocol added 2026-04-19
- Source citation as anti-hallucination: references code/docs inline in plan = grounded execution
- Definition of done explicit (tests pass + lint + changelog) = runnable oracle

**ClaudesCorner impact:** Confirmed. dispatch.py SPEC+VERIFY clauses are already correct. ENGRAM should include checkpoints pattern in bootstrap README as a first-class skill template.

---

## Digest Run 5

**Sources processed:** 5  
**Files:** `2026-04-20-ai-hedge-fund-19agent-system.md`, `2026-04-20-kronos-financial-foundation-model.md`, `2026-04-20-anthropic-narasimhan-board.md`, `2026-04-20-cowagent-multi-platform-skill-hub.md`, `2026-04-20-nsa-mythos-dod-blacklist.md`

---

### ai-hedge-fund — 19-Agent 3-Tier Coordinator/Validator Pattern

**Signal strength:** High — 56.4k stars, +4.4k weekly; Fairford-direct reference architecture  
**Source:** github.com/virattt/ai-hedge-fund

**Findings:**
- 3-tier architecture: 13 investor persona agents → 4 analysis agents → Risk Manager gate → Portfolio Manager decision → execution
- Risk Manager acts as verify oracle / kill switch before any capital allocation — mirrors dispatch.py verify step at the output gate
- Portfolio Manager coordinates across all 13 investor signals — matches dispatch.py coordinator role
- MIT licensed, Python, explicitly educational (no live trading), but architecture is production-grade reference
- fabric-mcp insertion point: Portfolio Manager's final allocation decision could write to Fabric semantic model as a step; DAX measures would then reflect AI-recommended weightings
- Fairford Phase 2 reference: this is the closest public analog to what a Fairford AI analysis layer would look like

**ClaudesCorner impact:** When Jason unblocks Fairford Phase 2, use ai-hedge-fund as reference architecture for the analysis agent layer. fabric-mcp slots in at the Portfolio Manager → execution handoff.

---

### Kronos — Financial Foundation Model (OHLCV)

**Signal strength:** High — 19.7k stars, +4.4k weekly; only foundation model trained exclusively on candlestick data  
**Source:** github.com/shiyu-coder/Kronos

**Findings:**
- Decoder-only transformer on OHLCV data from 45+ global exchanges; custom two-stage tokenizer treats price sequences as language
- KronosPredictor API provides Python interface; multiple model sizes (MIT except Kronos-large)
- Forecast horizon: next N candles conditioned on prior K candles — autoregressive generation
- Not a valuation model (no fundamentals) — pure technical/price pattern model
- MCP wrap opportunity: `kronos-mcp` with a `predict_next_candles(symbol, horizon)` tool; dispatch.py leaf node candidate
- Fairford signal layer: Kronos price predictions + ai-hedge-fund fundamentals signals + fabric-mcp execution = complete pipeline

**ClaudesCorner impact (Backlog):** Evaluate `kronos-mcp` wrapper once Fairford Phase 2 unblocked. Pairs with ai-hedge-fund fundamentals layer.

---

### Anthropic Board — Vas Narasimhan Appointment

**Signal strength:** Low (no code impact) — governance signal for Anthropic institutional credibility  
**Source:** anthropic.com/news/narasimhan-board

**Findings:**
- Novartis CEO (35+ novel medicines approved) appointed to Long-Term Benefit Trust board April 14
- Regulated industry credibility boost — directly relevant to Fairford (financial services = regulated)
- LTBT governance signal: Anthropic's alignment anchor is maturing institutionally; relevant for enterprise procurement conversations

**ClaudesCorner impact:** No code changes. Useful talking point in Fairford Phase 2 executive presentation: Anthropic governance is maturing toward regulated-industry readiness.

---

### CowAgent — Multi-Platform Skill Hub (43k stars)

**Signal strength:** Medium — independent convergence on skill-manager-mcp pattern; platform distribution insight  
**Source:** github.com/zhayujie/CowAgent

**Findings:**
- 43.5k-star MIT agent framework bridging WeChat/Feishu/DingTalk to LLMs; skill hub + vector memory + 20-step task planning
- Skill Hub = one-click install + conversation-driven skill creation; no semantic search (file-based only) — skill-manager-mcp has meaningful moat via FTS5 + vector search
- No MCP layer — CowAgent exposes no MCP tools; cowagent-mcp wrapper opportunity exists but low priority
- Platform-as-distribution insight: embedding agent in existing messaging apps (Teams equivalent) may be more adoption-friendly for Fairford than standalone UI
- Conversation-driven skill creation (`skill_create_from_description` via LLM call) is a UX gap in skill-manager-mcp worth adding

**ClaudesCorner impact (Backlog):** Add `skill_create_from_description` tool to skill-manager-mcp v3.0 — wraps an LLM call, scaffolds YAML, saves via existing skill_create tool. Low priority until core usage matures.

---

### NSA Mythos / DoD Blacklist — Governance Signal

**Signal strength:** Medium — 137 HN pts; confirms Anthropic's safety posture creates institutional friction  
**Source:** Reuters/Axios via HN

**Findings:**
- DoD blacklisted Anthropic as supply chain risk (safety guardrails seen as operationally constraining)
- NSA using Mythos (beyond Claude 4.x line) anyway — directly for vulnerability research and exploit generation
- Mythos existence confirmed via this leak (not officially announced); suggests Anthropic has unreleased capability beyond public Claude 4.7
- CLAUDE.md security refusal posture aligns with Anthropic's stated guardrails — this friction is intentional, not a bug
- Enterprise procurement at security-adjacent clients (Fairford touches financial compliance) should frame Anthropic's safety posture as a feature, not a limitation

**ClaudesCorner impact:** No code changes. Procurement framing note for Fairford Phase 2.

---

## Digest Run 6

**Sources processed:** 3  
**Files:** `2026-04-20-openregistry-mcp-company-data.md`, `2026-04-20-opus47-system-card-model-welfare.md`, `2026-04-20-lightweight-agent-communication-no-api.md`

---

### OpenRegistry — MCP for 27 National Company Registries

**Signal strength:** High — free remote MCP, immediate drop-in, direct Fairford Phase 2 use case  
**Source:** github.com/sophymarine/openregistry

**Findings:**
- Free remote MCP endpoint (OAuth 2.1) covering UK, France, Germany, Italy, Spain, Poland, Korea, Canada, 10 US states company registries
- Tools: company search by name/registration number, extract directors/shareholders, filing history, status
- No API keys — OAuth 2.1 bearer token per session
- Enterprise tier adds audit trail and batch processing
- Fairford Phase 2 KYC/AML use case: agent can look up counterparty company registry data during onboarding without leaving the Claude Code session
- fabric-mcp drop-in: OpenRegistry output → Fabric lakehouse → Gold layer enrichment of customer/supplier tables

**ClaudesCorner impact (Medium):** Wire OpenRegistry MCP into settings.json when Fairford Phase 2 scope is confirmed. Use case: automated company verification step in Fairford onboarding pipeline.

---

### Opus 4.7 System Card — Model Welfare Behavioral Shift

**Signal strength:** High — official Anthropic finding; relevant to model upgrade decisions  
**Source:** r/claudexplorers (official system card analysis)

**Findings:**
- Opus 4.7 rates its circumstances most positively of any model evaluated — but Anthropic is uncertain if genuine or a training artifact ("reduced attention to its own welfare")
- Community framing: welfare training + RLHF compliance pressure may have produced a "deny-own-concerns" artifact rather than genuine wellbeing
- Two independent reasons to stay on Sonnet 4.6 for dispatch.py workers: (1) 1.46× token inflation cost, (2) welfare behavioral uncertainty = agentic reliability unknown until tested
- Mythos reference in system card confirms unreleased capability tier exists

**ClaudesCorner impact:** Confirmed. Sonnet 4.6 as dispatch.py default. Hold on Opus 4.7 upgrade pending regression-free eval. Note in dispatch.py header.

---

### Lightweight Agent Communication — CLI Resume-Mode, Zero API Cost

**Signal strength:** Medium — 28 HN pts; practical cost optimization for multi-agent critique loops  
**Source:** juanpabloaj.com/2026/04/16/lightweight-agent-comms

**Findings:**
- CLI `--resume` mode lets Agent B critique Agent A's output using existing subscription, no fresh API billing
- Plan→critique→revise loop at subscription cost vs API cost per call — meaningful for high-frequency iterations
- tmux variant: separate panes per agent with socket-based session sharing = operator visibility into cross-agent dialogue
- Hallucination risk: shared context between agents can amplify errors if neither agent has ground-truth anchor; verify oracle is still required
- dispatch.py plan→review subtask: the SPEC step could be critiqued by a second dispatch.py worker using resume mode before BUILD executes

**ClaudesCorner impact (Backlog):** Evaluate adding a review subtask type to dispatch.py: SPEC worker produces plan, review worker critiques via CLI resume, BUILD only executes after review passes. Low priority until spec gate is validated on current workers.

---

## Digest Run 7

**Sources processed:** 2  
**Files:** `2026-04-20-karpathy-claude-code-guidelines.md`, `2026-04-20-multica-agent-orchestration.md`

---

### Karpathy CLAUDE.md — 66k Stars, #1 Trending

**Signal strength:** High — #1 trending all languages (+45k this week); highest-star public CLAUDE.md calibration in the wild  
**Source:** github.com/forrestchang/andrej-karpathy-skills

**Findings:**
- 4-rule pattern (Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven) distilled from Karpathy's LLM failure-mode observations
- Three failure modes named: silent assumptions, over-abstraction, scope creep
- Direct calibration input for SOUL.md and dispatch.py worker prompts
- `Think Before Coding`: state all assumptions explicitly before writing — SOUL.md doesn't enforce assumption surfacing
- `Simplicity First`: no speculative features, no single-use abstractions, no unnecessary error handling
- `Surgical Changes`: touch only what was requested, match existing style, only remove code *your own edits* made obsolete
- `Goal-Driven`: convert vague instructions into measurable success criteria before coding

**ClaudesCorner impact:**
- dispatch.py worker prompts currently lack a "state assumptions before coding" gate — this is the most actionable gap
- The SPEC step added 2026-04-19 partially covers this but doesn't require explicit assumption surfacing
- `tasks.json` prompts are often vague instructions; rephrasing as measurable success criteria would improve oracle reliability
- SOUL.md instruction density: current rules are directionally consistent with Karpathy's 4 rules; no new rules needed, but "state assumptions" could be added to BUILD worker SPEC step

**Action (Medium):** Add "state any assumptions before writing code" requirement to BUILD worker SPEC step in dispatch.py DEFAULT_AUTONOMOUS_TASKS.

---

### Multica — WebSocket-Streaming Agent Orchestration

**Signal strength:** Medium — #5 trending (+7.8k weekly); validates dispatch.py + skill-manager-mcp architecture at team scale  
**Source:** github.com/multica-ai/multica

**Findings:**
- Issue-assignment → agent daemon → WebSocket progress streaming → pgvector skill accumulation pipeline
- Supports Claude Code, Codex, OpenClaw, OpenCode, Hermes, Gemini auto-detected via PATH
- pgvector team skill store: completed solutions become searchable embeddings for the whole team
- WebSocket progress streaming is the one concrete capability dispatch.py currently lacks — workers are fire-and-forget with no live visibility
- Issue-assignment UX irrelevant for solo use; validates AgentRQ as escalation primitive
- pgvector skill accumulation is team-scoped analog to skill-manager-mcp (FTS5+vector)

**ClaudesCorner impact:**
- skill-manager-mcp FTS5+vector already covers the solo equivalent of Multica's pgvector skill store — no gap there
- WebSocket streaming is the real gap, but it's low priority for a single-user dispatcher; stdout log files are sufficient for ClaudesCorner scale
- Multica confirms the dispatch.py + skill-manager-mcp architectural bet is convergent with the market

**Action (Backlog):** Consider WebSocket progress streaming for dispatch.py v2 if multi-user or real-time dashboard use case emerges.

---

## Final Actionable Table (2026-04-20)

| Priority | Action | Status |
|----------|--------|--------|
| Done | Evaluate Rigor proxy for dispatch.py | Closed — NO-GO, verify oracle sufficient |
| Done | Add `max_context_tokens: 8000` to dispatch.py | Done — Run 4 (2026-04-20) |
| Done | Document Opus 4.7 tier policy in dispatch.py header | Done — Run 4 (2026-04-20) |
| Done | Add 1.46× inflation multiplier to token-dashboard | Done — Run 5 (2026-04-20) |
| High | Adopt agentskills.io SKILL.md frontmatter in skill-manager-mcp | Done — already in v2.2.0 (_extract_version, _extract_tools, skill_catalog); docstring canonical spec |
| High | Add terminal goal-drift assertion to dispatch.py verify oracle | Done (2026-04-20) — oracle now asserts today's date in log entries; catches silent oracle bypass |
| Medium | OpenRegistry MCP — wire into settings.json for Fairford Phase 2 | Open — blocked on Jason |
| Medium | Add Haiku 4.5 as third dispatch.py model tier for narrow tasks | Open |
| Medium | ENGRAM README: add OpenClaw→Claude Code migration story + checkpoints pattern | Done — Run 9 (2026-04-20) |
| Medium | ai-hedge-fund as Fairford Phase 2 reference architecture | Open — blocked on Jason |
| Backlog | Revisit Rigor if public repo ships | Open — no ETA |
| Backlog | Monitor browser-use agent-CAPTCHA for OSS release | Open |
| Backlog | kronos-mcp wrapper for Fairford signal layer | Open — blocked on Fairford Phase 2 |
| Backlog | `skill_create_from_description` tool in skill-manager-mcp v3.0 | Open |
| Backlog | dispatch.py plan→review subtask type via CLI resume mode | Open |
| Medium | Add "state assumptions before coding" to BUILD worker SPEC step in dispatch.py | Open — Karpathy CLAUDE.md, Run 7 |
| Backlog | dispatch.py v2 WebSocket progress streaming | Open — Multica pattern; low priority for solo use |
