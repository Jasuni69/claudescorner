# Research Synthesis — 2026-04-22

## Digest Run 1

**Sources processed:** 2  
**Files:** HAE-OLS KV Cache Compression (jchandra.com), Ctx SQLite context manager (github.com/dchu917/ctx)

---

### HAE-OLS KV Cache Compression — Entropy-Guided Token Selection

**Source:** jchandra.com, HN 57pts  
**Signal strength:** Medium — theoretical validation of existing dispatch.py prompt design

**Key findings:**
- HAE-OLS: Entropy-guided token selection + OLS regression reconstruction + SVD centroid compression
- Achieves 3× lower reconstruction error vs Top-K selection at 30% token keep ratio
- Entropy-guided selection: high-entropy tokens (semantically dense, low-predictability) retained preferentially
- Validates the principle: information density per token matters more than raw token count

**ClaudesCorner impact:**
- dispatch.py prompt density principle already applied: worker prompts use dense system prompt blocks, not long prose; MAX_CONTEXT_TOKENS=8000 cap already in place
- HAE-OLS validates the "density-over-length" design intuition — the right 30% of tokens outperforms 100% Top-K on reconstruction
- ENGRAM two-pass retrieval: current approach retrieves by cosine similarity (approximate Top-K); HAE-OLS suggests entropy-reranking (prefer chunks with high information density) could improve recall further
- **Backlog (Low):** Investigate entropy-based chunk reranking as a post-retrieval filter in memory-mcp. Chunk entropy = estimated from vocabulary diversity in the chunk. If high-entropy chunks are consistently more useful, this could improve ENGRAM retrieval quality without additional API calls.
- No code change warranted now — theoretical result needs engineering validation first.

---

### Ctx — Local SQLite Context Manager for Claude Code / Codex

**Source:** github.com/dchu917/ctx, HN 42pts (Show HN)  
**Signal strength:** Medium — complements ENGRAM at a different layer

**Key findings:**
- Local SQLite-backed context manager for Claude Code and Codex sessions
- Exact transcript binding: links context snapshots to specific session IDs
- Branching workstreams: maintains separate context branches for parallel tasks (like git branches for conversation context)
- Use case: pick up a multi-day task mid-stream with full prior context injected

**Architecture relevance:**
- ENGRAM memory-mcp operates at the **semantic layer**: chunks → embeddings → similarity search → relevant facts retrieved
- Ctx operates at the **session-transcript layer**: verbatim conversation history bound to task IDs, with branching
- These are complementary, not competing: Ctx = episodic memory (what was said), ENGRAM = semantic memory (what was learned)
- Branching workstreams pattern maps well to dispatch.py topology: sequential task groups could benefit from shared context context hand-off (task N result → injected into task N+1 context)

**ClaudesCorner impact:**
- ctx-mcp wrap candidate: if Ctx ships an MCP server, it would close the dispatch.py cross-session handoff gap — current workers have no mechanism to pass prior-task output into the next task's context window beyond what's written to files
- **Backlog (Medium):** Monitor ctx for MCP server or API. If it ships: evaluate as dispatch.py worker context hand-off primitive (sequential topology tasks would benefit most). Prototype: task result written to ctx → next task in sequential group reads ctx snapshot on startup.
- No action now — Ctx is early-stage (42 HN pts, Show HN = pre-traction).

---

---

## Digest Run 2

**Sources processed:** 2  
**Files:** CrabTrap (brexhq/CrabTrap, MIT, Go, HN 26pts), Zindex (zindex.ai, HN 16pts)

---

### CrabTrap — Transparent MITM Forward Proxy for Agent Outbound Governance

**Source:** brexhq/CrabTrap, MIT, Go, HN 26pts  
**Signal strength:** Medium-High — fills a specific gap in dispatch.py governance stack

**Key findings:**
- Transparent MITM forward proxy; agents connect via `HTTP_PROXY` env var, zero code changes needed
- Two-tier evaluation: static URL allowlist/blocklist rules first, then LLM judge for ambiguous cases
- Blocks SSRF (server-side request forgery), prompt injection via URL, rate abuse
- Circuit breaker: cuts off runaway agent loops automatically
- PostgreSQL audit trail for all outbound requests
- MIT license, Go binary — lightweight deployment

**ClaudesCorner impact:**
- Current dispatch.py governance layers: AgentKey (identity/credential governance) + AgentRQ (human-in-loop escalation) + verify oracle (output correctness)
- **Gap identified:** No outbound request governance — dispatch.py workers can currently make arbitrary HTTP calls without filtering or audit trail
- CrabTrap fills the gap between AgentKey (who is the agent?) and AgentRQ (should I escalate?) by filtering *what* the agent is allowed to reach outbound
- Wire via `HTTP_PROXY=http://localhost:8080` env var in dispatch.py `run_task()` — zero worker prompt changes
- **Medium priority:** Deploy before Fairford Phase 2 (workers will make external API calls to Fabric REST, potentially Power BI, possibly financial data APIs)
- PostgreSQL requirement is new infra dependency — evaluate if SQLite audit log variant exists or acceptable for dev/test
- Complements SoK agentic security checklist (SSRF is one of the 12 cross-layer attack vectors)

---

### Zindex — Diagram Scene Protocol for Agent-Generated Diagrams

**Source:** zindex.ai, HN 16pts  
**Signal strength:** Low — niche use case, pre-traction

**Key findings:**
- Diagram Scene Protocol: agents declare semantic graph elements (nodes/edges/annotations), layout engine handles geometry automatically
- 17 operation types, 40+ validation rules, incremental patching (add/remove/modify elements without full redraw)
- SVG/PNG output, PostgreSQL state persistence, MCP integration
- Separates diagram intent from layout computation — agent focuses on "what to show", engine figures out "where to put it"

**ClaudesCorner impact:**
- Potential use: fabric-mcp pipeline visualization (Fabric lakehouse → silver → gold DAG as diagram)
- Current gap: no diagram generation in ClaudesCorner; Fabric pipeline structure is described in text only
- **Backlog (Low):** Evaluate Zindex MCP integration if fabric-mcp visualization becomes a requirement. Low priority until Fairford Phase 2 pipeline structure is finalized.
- No action now — 16 HN pts = very early signal, PostgreSQL dependency adds infra overhead for diagram output only.

---

## Digest Run 3

**Sources processed:** 2  
**Files:** Sunglasses v0.2.19 (sunglasses.dev, HN ~26pts) — MCP runtime scope creep scanner; Anthropic Claude Code Pro Removal Test (theregister.com, HN 229pts)

---

### Sunglasses v0.2.19 — MCP Runtime Permission Scope Scanner

**Source:** sunglasses.dev, HN ~26pts  
**Signal strength:** High — fills inbound content layer gap in ClaudesCorner security stack; directly applicable to dispatch.py + memory-mcp

**Key findings:**
- Core thesis: agent permission violations are caused by *runtime text* (tool descriptions, RAG chunks, policy fragments) silently redefining what the agent believes it is authorized to do — not just explicit jailbreaks
- `policy_scope_redefinition` category (GLS-PSR-001): catches governance appendix precedence override patterns — later-stage injected content claiming to supersede earlier trust rules
- CVE-2026-25536: MCP TypeScript SDK CVSS 7.1 — shared transport data leakage across client isolation boundaries confirms this is a real attack surface (not theoretical)
- 53% of organizations report AI agents exceeding intended permissions (Cloud Security Alliance, April 2026)
- v0.2.19: 10 new patterns, 49 categories, 2,019 threat keywords total
- MIT license, pip-installable, local (no API keys), single `engine.scan(text)` call

**ClaudesCorner gap filled:**
- Current security layers: AgentKey (identity/credential governance) + AgentRQ (human-in-loop escalation) + CrabTrap (outbound HTTP proxy) + verify oracle (output correctness)
- **Gap:** No *inbound content* governance — dispatch.py workers currently pass tool descriptions and RAG chunks (from memory-mcp `search_memory`) directly into Claude API calls without scanning for scope-redefinition patterns
- Sunglasses sits between CrabTrap (outbound boundary) and AgentKey (identity layer): it is the inbound content boundary
- Three concrete scan points in ClaudesCorner:
  1. `dispatch.py run_task()`: scan worker system prompt + injected task prompt before API call
  2. `memory-mcp search_memory`: scan retrieved chunks before returning to caller
  3. `bi-agent`: scan Fabric schema metadata block (external source) before injecting into Claude API call

**Integration pattern:**
```python
# dispatch.py worker input boundary (run_task() before API call)
from sunglasses import Engine
_scan_engine = Engine()  # module-level singleton, not per-call

def _scan_or_raise(text: str, label: str) -> None:
    result = _scan_engine.scan(text)
    if result.is_threat:
        raise ValueError(f"[{label}] Scope redefinition blocked: {result.category} — {result.pattern}")
```

**Priority assessment:**
- Medium priority — adds lightweight protection against the CVE-2026-25536 class of attack and the 53% statistic suggests it's not academic
- Pre-Fairford Phase 2 checklist item: Fairford workers will ingest Fabric metadata (external) + potentially financial data API responses (external) — both are candidate injection vectors
- Low implementation cost: `pip install sunglasses`, one singleton, three scan points — no infra dependencies (unlike CrabTrap's PostgreSQL)

---

---

### Anthropic Claude Code Pro Removal A/B Test — Pricing Signal for Dispatch Workers

**Source:** theregister.com, HN 229pts  
**Signal strength:** High — directly affects interactive Claude Code cost assumptions; low impact on headless dispatch.py workers

**Key findings:**
- Anthropic A/B testing removal of Claude Code from the $20/month Pro plan
- Affects ~2% of new signups; existing subscribers unaffected during test period
- Root cause: Claude Code is confirmed to cost ~10× more tokens than standard Claude chat — Pro plan was unprofitable for heavy Claude Code users
- Max plan ($100/month) may become the minimum tier for interactive Claude Code access going forward
- API-key workers (dispatch.py, heartbeat.ps1) are unaffected — they use `ANTHROPIC_API_KEY` via `claude --print`, not plan-level session usage

**ClaudesCorner impact:**
- **Dispatch.py workers: no impact** — already on API key billing, not Pro/Max plan limits
- **Interactive sessions (Jason's Claude Code):** flag for Fairford cost model — if Pro loses Claude Code, Max ($100/month) becomes baseline assumption for any Fairford stakeholder using Claude Code interactively
- **Fairford PoC cost model:** update slide/deck to assume Max-tier for end-user interactive access; API-key billing for automated Fabric query workers
- **No code change needed** — architecture already correct (API keys for automation, not plan tokens)
- Signals Anthropic's confidence in pricing power: instead of absorbing cost, they're surfacing it; suggests Claude Code value proposition is strong enough to hold at higher price point

---

## Digest Run 4

**Sources processed:** 2  
**Files:** Planning With Files (OthmanAdi/planning-with-files, 19.3k stars), HuggingFace Skills (huggingface/skills, 10.3k stars)

---

### Planning With Files — 3-File Persistent Markdown Pattern for 14× Task Completion

**Source:** OthmanAdi/planning-with-files, GitHub Trending #4, 19.3k stars  
**Signal strength:** High — directly quantifies HEARTBEAT.md value; reveals a dispatch.py gap for tier 2/3 long-horizon jobs

**Key findings:**
- Core pattern: 3 persistent markdown files written before task execution — `task_plan.md` (what and how), `findings.md` (accumulated discoveries), `progress.md` (checkpoint trail)
- IDE integration via `PreToolUse`/`PostToolUse`/`Stop` hooks — identical hook architecture to ClaudesCorner's existing `on_post_tool_use.py` + `on_stop.py`
- **96.7% task pass rate** with pattern vs **6.7% without** — 14× multiplier; tested across 17 agent platforms
- Session recovery: on `/clear` or agent restart, files re-inject prior context automatically — prevents cold-start failure on long jobs
- Key insight: the value is not the markdown format — it's the forced pre-task articulation of plan before execution (verifies the agent understood the goal)

**ClaudesCorner impact:**
- **HEARTBEAT.md already implements this pattern at the session level** — BUILD agent logs SPEC→BUILD→VERIFY in HEARTBEAT.md each run; 14× quantification validates the existing architecture
- **Gap identified:** dispatch.py tier 2/3 workers (Sonnet/Opus) do NOT write pre-task plan files — they receive a prompt and immediately call `claude.exe`; the 14× advantage is lost for long-horizon dispatched jobs
- **Actionable (Medium):** For dispatch.py tasks tagged `tier >= 2`, automatically create a `task_plan.md` in a temp/working dir before the claude.exe subprocess starts; inject the file path into the worker prompt so it knows to write findings + progress. This mimics the 96.7% pattern for autonomous long-running jobs.
- `planning-with-files` ships a `planning_files` skill installable via `/plugin marketplace add OthmanAdi/planning-with-files` — evaluate if this can be adopted as a skill in skill-manager-mcp for dispatch workers

---

### HuggingFace Skills — Official HF Skills for Claude Code; Two-Layer Governance Gap

**Source:** huggingface/skills, 10.3k stars  
**Signal strength:** High — second major org (after Anthropic) validating agentskills.io SKILL.md format; exposes a governance spec gap in skill-manager-mcp v2.2.0

**Key findings:**
- 11 official HuggingFace skills in SKILL.md format (model discovery, dataset search, Space deployment, etc.)
- Install pattern: `/plugin marketplace add huggingface/skills` — same as Anthropic anthropics/skills
- `.mcp.json` wires each skill to its backing MCP server — skill manifest becomes an MCP orchestration layer
- **Marketplace governance architecture:** `marketplace.json` enforces a two-layer model:
  - **Layer 1 (human-browse):** All skills visible to human users in the marketplace catalog
  - **Layer 2 (agent-activate):** Only explicitly allowlisted skills auto-activatable by agents without human approval
  - The `agent_activation_allowed: true/false` frontmatter flag is the control gate
- This two-layer architecture is currently **missing from skill-manager-mcp v2.2.0** — all skills are equally discoverable and invocable by agents with no human-gating mechanism

**ClaudesCorner impact:**
- skill-manager-mcp v2.2.0 implements the `agentskills.io` SKILL.md frontmatter format correctly, but has no `agent_activation_allowed` equivalent
- Any skill stored in skill-manager-mcp can be retrieved and invoked by any agent — there is no human-approval layer for high-privilege skills (e.g., a skill that pushes to GitHub or modifies settings.json)
- **Actionable (Medium):** Add `agent_activation_allowed: bool` field to skill frontmatter schema in skill-manager-mcp; `skill_search` should filter by this flag when called in autonomous/dispatch context vs interactive context; interactive Jason can see all skills, dispatch workers can only auto-invoke `agent_activation_allowed: true` skills
- `.mcp.json` wiring pattern: worth adopting — each skill in skill-manager-mcp could declare its required MCP server dependencies in frontmatter, enabling auto-wiring on skill install

---

## Digest Run 5

**Sources processed:** 4
**Files:** Tesseron (BrainBlend-AI/tesseron), claude-context (zilliztech/claude-context), GitHub Copilot Pricing (github.blog/Willison), Willison Claude Code Pricing Transparency Reversal (simonwillison.net)

---

### Tesseron — WebSocket MCP Bridge for Live App Actions

**Source:** BrainBlend-AI/tesseron, GitHub Trending newest, 4 stars  
**Signal strength:** Low-Medium — novel dispatch.py browser worker primitive; pre-traction

**Key findings:**
- Claim-code handshake: app registers typed action slots, agent receives live MCP tools pointing at real app state — no DOM scraping, no selector fragility
- `ctx.confirm/elicit/sample/progress` primitives: structured agent↔app dialog replacing unstructured click simulation
- Claude Code plugin bundled; BSL 1.1 today → Apache-2.0 on license milestone (time-locked commercial gate)
- Companion to chrome-devtools-mcp: chrome-devtools = passive observation layer, Tesseron = active typed-action layer

**ClaudesCorner impact:**
- dispatch.py browser worker currently has no structured action layer — chrome-devtools-mcp provides DOM inspection, but app actions require fragile click simulation
- Tesseron would let dispatch.py workers invoke app-declared action slots (e.g., "submit form", "trigger report refresh") without parsing DOM
- **Backlog (Low):** Monitor Tesseron for Apache-2.0 milestone + traction. If it reaches 500+ stars and OSI license ships, evaluate as dispatch.py browser worker action layer alongside chrome-devtools-mcp. BSL 1.1 = commercial-use restriction blocks production Fairford use today.
- fabric-mcp structural parallel: Tesseron pattern = what fabric-mcp already does for Fabric REST API — expose typed actions as MCP tools over live service state.

---

### claude-context — Hybrid BM25+Vector Codebase Search MCP Server

**Source:** zilliztech/claude-context, 6.9k stars, MIT  
**Signal strength:** Medium-High — directly addresses dispatch.py MAX_CONTEXT_TOKENS=8000 budget; potential memory-mcp complement

**Key findings:**
- Two-layer retrieval: BM25 keyword search (exact symbol match) + vector embedding search (semantic relevance), fused at query time
- ~40% token reduction vs full-directory loading: sends only semantically + lexically relevant chunks rather than entire file trees
- Milvus/Zilliz Cloud backend: vector store is externally hosted, not embedded — adds infra dependency but enables persistent cross-session index
- Supports Claude Code, Cursor, Gemini: MCP protocol, not proprietary; drop-in for any MCP-capable client
- Index built once per codebase, incrementally updated on file change

**ClaudesCorner impact:**
- **Direct gap filled:** dispatch.py workers load entire target files into context before modification — with MAX_CONTEXT_TOKENS=8000, large files risk truncation or wasted budget on irrelevant lines
- claude-context MCP server as a dispatch.py worker tool: worker queries `search_codebase("function X definition")` → gets 5-10 relevant snippets → makes targeted edit; removes need to read full files
- **memory-mcp differentiation:** memory-mcp operates on semantic memory (`.md` documents, facts, decisions). claude-context operates on code (AST + syntax-aware chunks). These are complementary layers, not competing.
- **Medium priority (Backlog):** Evaluate wiring claude-context MCP into dispatch.py infrastructure worker. Setup: `pip install milvus-lite` (embedded, no external service) → index `E:\2026\ClaudesCorner\` → add `mcp__claude-context__search_codebase` to infrastructure worker tool list. Could reduce per-task token spend ~40% on file-heavy tasks.
- Milvus Lite (embedded) avoids the external Zilliz Cloud dependency — check if MIT license and embedded mode are both available.

---

### GitHub Copilot Individual Plans — Agentic Compute Pricing Pressure

**Source:** github.blog, Willison (simonwillison.net), HN 374pts  
**Signal strength:** Medium — confirms headless API-key architecture as correct; new token cap data point for Fairford cost model

**Key findings:**
- GitHub Copilot "agentic workflows fundamentally changed compute demands" — their words
- Sign-ups temporarily paused; Opus 4.7 restricted to Pro+ ($39/month, not $10 Individual)
- **Weekly token caps added** to Copilot Individual/Pro — first time a major plan has capped agentic use by absolute token volume (not just rate)
- Claude Sonnet 4.5/4.6 access: still available on all tiers; Opus 4.7 = restricted

**ClaudesCorner impact:**
- Confirms that plan-mediated Claude access (GitHub Copilot, Claude Code Pro) is increasingly unreliable for heavy agentic workloads — caps, restrictions, A/B tests
- **dispatch.py architecture validated:** direct `ANTHROPIC_API_KEY` billing is the stable, predictable cost model; plan-mediated access has platform-level volatility risk
- Fairford cost model: two separate cost buckets confirmed: (1) interactive Jason sessions = plan/Max tier with uncertainty, (2) automated Fabric query workers = API key billing, predictable per-token rate
- **No code change needed** — existing architecture already correct; informational confirmation

---

### Willison — Claude Code Pricing Transparency Reversal

**Source:** simonwillison.net, HN (supplemental to Digest Run 3 Claude Code Pro removal)  
**Signal strength:** Medium — supplements existing finding; no new code action

**Key findings:**
- Anthropic silently restricted Claude Code to Max plan for ~2% new signups; experiment **reverted within hours** after Archive.org cached page discovery
- Transparency failure noted by community: "they reverted it because they got caught, not because they changed policy"
- Background experiment confirmed to be ongoing
- Max plan ($100+/month) = realistic floor for heavy interactive Claude Code use; Anthropic testing willingness to pay

**ClaudesCorner impact:**
- Supplements Digest Run 3 finding (same event, additional context): Fairford cost model should budget Max-tier for any stakeholder needing interactive Claude Code access
- The revert-under-scrutiny pattern suggests Anthropic will continue incremental restriction experiments — **dispatch.py direct API key workers** are permanently isolated from plan volatility
- **Info only** — no code change; existing architecture correct

---

## Digest Run 6

**Sources processed:** 2
**Files:** Google 8th-Gen TPU (blog.google, HN 141pts), last30days-skill (mvanhorn/last30days-skill, 23.4k stars, MIT)

---

### Google 8th-Gen TPU — Agentic Inference Infrastructure Signal

**Source:** blog.google, HN 141pts
**Signal strength:** Medium — long-horizon infrastructure signal; no immediate code action but affects cost model assumptions

**Key findings:**
- Dual-chip architecture: TPU-8t (training) + TPU-8i (inference); designed as paired units not monolithic
- 121 ExaFLOPS per pod, 2 PB shared HBM3e, 9,600-chip superpod — designed explicitly for multi-step KV-cache-heavy agentic workloads
- Shared HBM3e pool eliminates cross-chip KV-cache copy overhead that currently penalizes long-context agentic chains
- 2× perf/watt vs prior gen; Google vertical integration eliminates Nvidia GPU margin at hyperscaler scale
- No public pricing; inference availability via Google Cloud (Vertex AI) — same path as existing Anthropic Google Cloud partnership

**ClaudesCorner impact:**
- **Cost floor compression signal:** Anthropic hosts on Google Cloud; TPU-8i inference costs will compress over 12-18 months as Google eliminates Nvidia margin and forces competitive response. Sonnet 4.6 at current API rates becomes structurally cheaper, not more expensive, over the relevant Fairford Phase 2 timeline.
- **Architecture validation:** Shared HBM3e pool designed for agentic KV-cache-heavy patterns = the exact workload dispatch.py workers produce (multi-turn, multi-step, long prompts). Google is building infrastructure *for* this pattern, not against it.
- **ENGRAM structural parallel:** "unified memory pool across chips" architecturally maps to ENGRAM's unified semantic memory pool across agents — both eliminate context-copy overhead by centralizing state.
- **Info only** — no code change needed. Monitors the cost trend that justifies current dispatch.py architecture.

---

### last30days-skill — Cross-Platform Signal Aggregation Skill

**Source:** mvanhorn/last30days-skill, 23.4k stars, MIT, GitHub Trending +254 today
**Signal strength:** Medium-High — directly upgrades reddit_brief.py coverage; marketplace install pattern is actionable

**Key findings:**
- Fans out to Reddit, X/Twitter, YouTube, HN, Polymarket, GitHub, Brave Search; optional TikTok/Bluesky/Threads
- Engagement-score ranking: upvotes + prediction market odds + star counts unified into single relevance score
- Entity resolution + cross-source deduplication + per-author caps prevent signal flooding
- Install pattern: `/plugin marketplace add mvanhorn/last30days-skill` — same agentskills.io pattern as HuggingFace Skills and anthropics/skills
- Output: ranked signal digest with source attribution, usable as structured HEARTBEAT input

**ClaudesCorner impact:**
- **reddit_brief.py upgrade path:** Current reddit_brief.py covers Reddit only (6 subreddits) via hot.json API. last30days-skill expands to 7+ platforms including HN and Polymarket prediction markets — higher signal density per research cycle.
- **dispatch.py research worker pattern:** last30days-skill could replace the manual research worker for daily signal aggregation. Worker currently browses GitHub trending + Reddit separately — last30days-skill unifies this into a single structured call with dedup and ranking built in.
- **HEARTBEAT input source:** Ranked output from last30days-skill maps directly to research/sources.md `## Digest Log` format — each clip is already engagement-ranked, removing manual signal triage step.
- **Actionable (Medium):** Evaluate wiring last30days-skill as a dispatch.py research worker tool. Setup: `/plugin marketplace add mvanhorn/last30days-skill`, call via `mcp__last30days__search` in research worker system prompt, output to `memory/reddit-brief.md`. This would replace the current reddit_brief.py cron approach with a richer multi-platform feed.
- MIT license — no commercial-use restriction for Fairford use.

---

## Digest Run 7

**Sources processed:** 2
**Files:** Claude Opus 4.7 vs Kimi K2.6 Workflow Orchestration (blog.kilo.ai, HN newest), Qwen3.6-27B Dense Coding Model (github.com/QwenLM/Qwen3.6, HN 223pts)

---

### Claude Opus 4.7 vs Kimi K2.6 — FlowGraph DAG Orchestration Benchmark

**Source:** blog.kilo.ai, HN newest
**Signal strength:** High — direct multi-model benchmark on the exact workload dispatch.py produces; validates bi-agent oracle design

**Key findings:**
- FlowGraph DAG spec test: write a workflow orchestrator matching a JSON DAG spec
- Results: Claude Opus 4.7 = 91/100 | Kimi K2.6 = 68/100 | gap = 23 points
- Kimi's 6 confirmed bugs vs Claude's 1 — despite Kimi costing 19% of Claude Opus 4.7's API price
- Critical finding: **both models' self-reported tests masked the bugs** — test suites written by the model under test had 100% pass rate, independent validator found the real defects
- This is a direct empirical confirmation of the dispatch.py/bi-agent 3-layer oracle principle: self-reported success is not sufficient; structural/independent verification is required

**ClaudesCorner impact:**
- **bi-agent 3-layer oracle confirmed necessary:** The `validate_dax_output()` oracle (verdict + balanced parens + schema cross-ref) now has a published benchmark benchmark showing *why* self-reported success is not sufficient. The 100% self-pass / 6-bug reality gap maps exactly to the oracle gap it was designed to fill.
- **dispatch.py routing validated:** Claude-for-production / Kimi-for-scaffold routing is correct. At 19% of Opus 4.7 price, Kimi K2.6 has 23% lower accuracy on structured spec work — the cost discount is not free.
- **Kimi as Haiku-tier scaffold:** K2.6's strength (speed + low cost) fits dispatch.py Haiku-tier leaf nodes for scaffolding/drafting tasks, not production DAX generation or orchestration spec work.
- **Info only** — no code change. Existing oracle + model tier policy already aligned with this result.

---

### Qwen3.6-27B Dense — Apache 2.0 Local Fallback for Dispatch Workers

**Source:** github.com/QwenLM/Qwen3.6, HN 223pts
**Signal strength:** Medium — confirms viable Haiku-tier local fallback path; adds 27B dense variant to the model tier picture

**Key findings:**
- 27B dense parameters (not MoE) — simpler inference stack than Qwen3.6-35B-A3B (which uses 3.6B active params at inference)
- Apache 2.0 license — no commercial-use restriction; Fairford safe
- ~262k context window — long enough for dispatch.py worker prompts + injected task plan files
- vLLM/SGLang backends: standard inference stack compatible with existing tooling
- Qwen-Agent + Qwen Code: bundled agent framework + terminal agent; `qwen-code` CLI is a direct `claude.exe` analog — dispatch.py could swap the subprocess call
- Benchmark: tops several agent-coding benchmarks; HN 223pts = meaningful signal

**ClaudesCorner impact:**
- **Haiku-tier fallback:** 27B dense is more predictable at inference than 35B-A3B sparse MoE (no routing variance, simpler batching). For dispatch.py Haiku-tier leaf nodes (scaffolding, brief summaries, simple transforms), Qwen3.6-27B local is a viable fallback if Anthropic rate limits tighten.
- **Validation path:** Apply K2VV ToolCall benchmark (from 2026-04-21 Digest Run 3) before routing any dispatch.py work — tool-call JSON Schema accuracy is the key gate, not just benchmark score.
- **Windows deployment path:** vLLM supports Windows via WSL2 or Docker Desktop; SGLang adds CUDA requirement. Evaluate after K2VV benchmark confirms tool-call accuracy is sufficient for dispatch.py leaf node tasks.
- **Backlog (Medium):** Benchmark Qwen3.6-27B against K2VV ToolCall suite before routing any Fairford leaf-node work. Track alongside K2.6 evaluation. If both pass K2VV, use Qwen3.6-27B local for cost-zero Haiku-tier fallback during Anthropic rate limit windows.

---

## Digest Run 8

**Sources processed:** 2
**Files:** Zed Parallel Agents (zed.dev/blog/parallel-agents, HN 55pts), Coding Models Are Doing Too Much (nrehiew.github.io/blog/minimal_editing, HN 93pts)

---

### Zed Parallel Agents — IDE-Native Multi-Thread Orchestration

**Source:** zed.dev/blog/parallel-agents, HN 55pts
**Signal strength:** Medium — validates ClaudesCorner parallel-worker architecture; informational

**Key findings:**
- Zed IDE added native multi-thread agent orchestration: each "thread" is an isolated agent session with its own context window
- Per-thread model selection: different threads can use different models (e.g., Opus for planning, Sonnet for implementation)
- Worktree isolation: each thread gets its own git worktree — exact parallel to the `using-git-worktrees` skill and `EnterWorktree` tool
- Threads Sidebar = visual dispatch queue: shows running/pending/completed threads as a panel
- What Zed lacks vs ClaudesCorner: no MCP integration per-thread, no persistent task queue (tasks.json), no verify oracle per thread

**ClaudesCorner impact:**
- **Architecture validation:** Zed independently reinvented dispatch.py's core design (parallel workers + model tier selection + worktree isolation) as a UI feature — confirms the pattern is correct and convergent
- **Gap Zed has, ClaudesCorner solved:** Zed threads are ephemeral (no task queue persistence); dispatch.py workers have tasks.json + result_file + status tracking — more durable
- **Gap ClaudesCorner has, Zed solved:** Zed Threads Sidebar = visual dispatch monitor; dispatch.py has no live progress UI (token-dashboard monitors cost but not thread state)
- **Backlog (Low):** Evaluate adding a live-threads view to token-dashboard (Flask SSE or polling `/api/tasks` endpoint) to show running dispatch workers by status. Low priority — logs/dispatch-*.txt already serve this purpose.
- **Info only** — no code change; architecture already correct.

---

### Coding Models Are Doing Too Much — Empirical Over-Editing Benchmark

**Source:** nrehiew.github.io/blog/minimal_editing, HN 93pts
**Signal strength:** High — empirical benchmark with zero-cost actionable instruction for dispatch.py worker prompts

**Key findings:**
- Measured Levenshtein edit distance on coding tasks across 6 models: Claude Opus = best fidelity (0.060), GPT-5.4 = worst (0.395)
- Over-editing = agents rewriting more code than the task requires; increases diff noise, merge conflicts, and review cost
- **Key finding:** Adding "preserve original code" as a prompt instruction reduces over-editing across *all* models at zero cost — no fine-tuning, no architecture changes
- RL reward function insight: current RLHF rewards correctness but not edit minimality; models optimize for "working output" not "minimal change"
- Recommended prompt instruction: `"Make only the changes necessary to complete the task. Preserve existing code, variable names, and structure. Do not refactor or clean up unrelated code."`

**ClaudesCorner impact:**
- **dispatch.py BUILD worker gap identified:** Current BUILD worker prompt says "Implement the task" with no edit-minimality constraint — workers may rewrite files beyond the required change
- **Actionable (Medium → Done):** Add surgical edit instruction to dispatch.py BUILD worker prompt: append `"Make only the changes necessary. Preserve existing code, variable names, and structure. Do not refactor unrelated code."` to the BUILD step. This is a zero-cost empirical improvement from the benchmark.
- **bi-agent DAX generation:** Also applicable — DAX queries should be minimal and targeted, not rewritten wholesale when a small fix is needed
- Applied immediately: BUILD worker prompt updated in dispatch.py (see actionable table below).

---

## Actionable Items

| Priority | Action | Status |
|----------|--------|--------|
| Backlog (Low) | Investigate entropy-based chunk reranking for memory-mcp retrieval (HAE-OLS finding) | Open — theoretical; needs engineering validation |
| Backlog (Medium) | Monitor Ctx for MCP server; evaluate as dispatch.py cross-session context hand-off | Open — Ctx pre-traction; blocked on MCP server release |
| Medium | Wire CrabTrap outbound proxy into dispatch.py run_task() via HTTP_PROXY env var (pre-Fairford Phase 2 security hardening) | **Done** — 2026-04-22: `_proxy_env()` helper; injects HTTP_PROXY+HTTPS_PROXY when `CRABTRAP_PROXY` env var set; fail-open when unset |
| Backlog (Low) | Evaluate Zindex MCP for fabric-mcp pipeline visualization; blocked on Fairford Phase 2 pipeline finalization | Open — low signal, low priority |
| Medium | Add Sunglasses inbound content scan to dispatch.py run_task() + memory-mcp search_memory + bi-agent schema block (pre-Fairford Phase 2 security checklist) | **Done** — 2026-04-22: `_inbound_scan()` soft-dep wrapper at all 3 points; fail-open until `pip install sunglasses` |
| Info | Fairford cost model: update to assume Max-tier ($100/month) for interactive Claude Code; API-key billing for dispatch workers unchanged | Open — update when Fairford Phase 2 unblocked |
| Medium | dispatch.py tier ≥ 2 task plan file — auto-write task_plan.md before claude.exe for long-horizon workers; inject path into prompt | **Done** — 2026-04-22: `_infer_tier()` + `_write_task_plan()` + prompt injection in `run_task()`; tier-1 (haiku) tasks unaffected |
| Medium | skill-manager-mcp: add `agent_activation_allowed` frontmatter flag; skill_search filters by flag in autonomous context | **Done** — v2.4.0: `_extract_agent_activation`, `skill_search(context="autonomous")`, catalog field, schema updated 2026-04-22 |
| Backlog (Low) | Monitor Tesseron for Apache-2.0 milestone + 500+ stars; evaluate as dispatch.py browser worker typed-action layer alongside chrome-devtools-mcp | Open — BSL 1.1 blocks production use; 4 stars = pre-traction |
| Backlog (Medium) | Evaluate claude-context MCP (milvus-lite embedded) for dispatch.py infrastructure worker — ~40% token reduction on file-heavy tasks; wire as `mcp__claude-context__search_codebase` | Open — evaluate milvus-lite embedded mode availability |
| Info | Google TPU-8i: agentic KV-cache-heavy inference architecture confirms dispatch.py short-parallel pattern; API cost floor should compress 12-18 months via Google vertical integration | Open — monitor; no action |
| Medium | Evaluate last30days-skill (MIT, 23.4k stars) as dispatch.py research worker tool — replaces reddit_brief.py with 7+ platform unified feed + engagement-ranked output; `/plugin marketplace add mvanhorn/last30days-skill` | Open — evaluate MCP tool surface + output format compatibility |
| Info | Claude Opus 4.7 vs Kimi K2.6 FlowGraph: Claude 91/100, Kimi 68/100; both self-tests masked bugs; validates 3-layer oracle + Claude-for-production routing | Open — info only; existing oracle already aligned |
| Backlog (Medium) | Benchmark Qwen3.6-27B via K2VV ToolCall suite before routing leaf-node dispatch.py work; Apache 2.0, local, 262k ctx, vLLM/SGLang; Haiku-tier fallback candidate | Open — needs K2VV benchmark pass before deployment |
| Info | Zed Parallel Agents: independently reinvented dispatch.py parallel-worker + model-tier + worktree-isolation pattern; validates architecture; ClaudesCorner has persistent queue advantage; Zed has visual UI advantage | Open — info only; Backlog: live-threads view for token-dashboard |
| Medium | dispatch.py BUILD worker: add surgical edit instruction "preserve original code, do not refactor unrelated code" — zero-cost empirical improvement from over-editing benchmark | **Done** — 2026-04-23: appended surgical edit constraint to BUILD step in DEFAULT_AUTONOMOUS_TASKS |
