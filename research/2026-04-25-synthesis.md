# Research Synthesis — 2026-04-25

## Digest Run 1

**Sources processed:** 2
**Clips:** `2026-04-25-claude-stop-hooks-exit-code-fix.md`, `2026-04-25-free-claude-code-proxy-open-weight-routing.md`

---

### Claude Stop Hooks Ignored — Exit Code 2 + Stderr Required — HN 52pts

**Signal strength:** High — directly actionable protocol knowledge for any future blocking hook authorship

**Root cause (community consensus):**

Three compounding errors explain most "stop hook ignored" reports:

| Mistake | Consequence |
|---------|-------------|
| Exit code `0` | Hook treated as success; block directive silently ignored |
| `stdout` instead of `stderr` | Output discarded even with exit 2 |
| JSON output | Resembles prompt-injection payload; Claude's injection defense may suppress it |

**Correct blocking stop hook pattern:**
```bash
#!/bin/bash
echo "BLOCKED: <reason>" >&2
exit 2
```

**ClaudesCorner assessment:**

- `on_stop.py` exits 0 via `main()` returning normally — **this is correct**. It is a notification hook (runs tasks, spawns idle activities) — it should never block. No fix needed.
- `settings.local.json` `PostToolUse` hook: indexes files on Write/Edit; exit 0 is correct (audit-only, non-blocking).
- **No blocking stop hooks currently exist** in ClaudesCorner infrastructure. The exit 2 + stderr pattern is new knowledge for when blocking hooks are authored in future (e.g., "block commit if tests failed", "block session end if oracle fails").

**Action:** Info/Done — on_stop.py and PostToolUse hook are correctly configured. Future blocking hooks must use exit 2 + plain text stderr.

---

### free-claude-code — FastAPI Proxy Routes Claude Code to Open-Weight Models — 8.7k stars

**Signal strength:** Medium — viable cost-mitigation path; blocked by ToS ambiguity

**What it is:** MIT FastAPI proxy (`ANTHROPIC_BASE_URL=http://localhost:8082`) intercepts Claude Code API calls and forwards to NVIDIA NIM (free, 40 req/min), OpenRouter, DeepSeek, or llama.cpp. Format translation is bidirectional (Anthropic ↔ OpenAI-compatible). Per-model routing: Opus/Sonnet/Haiku can route to different backends independently.

**ClaudesCorner relevance:**

| Feature | Dispatch.py fit |
|---------|----------------|
| Per-model routing | Haiku-tier workers → NVIDIA NIM free tier; Sonnet → DeepSeek |
| Zero code changes | Two env vars in `run_task()` env dict |
| Rate limiting | 40 req/min NIM cap = ceiling for 3-worker burst |
| Thinking token support | `<think>` → native thinking blocks |
| Discord/Telegram bot mode | Not relevant |

**Concerns:**

1. **Anthropic ToS ambiguity** — this is a workaround, not a sanctioned integration. Not suitable for Fairford or any client-facing dispatch work.
2. **Quality delta unknown** — K2VV ToolCall F1 benchmark required before any routing change. NIM/DeepSeek are not validated for DAX generation quality.
3. **Rate limit ceiling** — 40 req/min NIM free tier is tight for 3 concurrent workers with burst.
4. **CrabTrap + AgentKey still required** — proxy is transparent; outbound filtering and identity governance remain at the worker layer.

**Comparison to existing:** dispatch.py already has Haiku/Sonnet/Opus tier routing. This adds a fourth tier: **free local/open-weight fallback** for overnight non-critical batch jobs when Anthropic rate limits are saturated.

**Action:** Backlog/Low — viable as emergency Haiku-tier fallback only; requires K2VV benchmark pass + Anthropic ToS clarity before deployment. Do not use for Fairford.

---

## Actionable Items

| Item | Priority | Status |
|------|----------|--------|
| Stop hooks: exit 2 + stderr required for blocking hooks | Info | **Done** — documented; on_stop.py + PostToolUse hook confirmed correct (non-blocking, exit 0) |
| free-claude-code: FastAPI proxy for open-weight fallback | Low | Backlog — ToS ambiguity + K2VV benchmark required; emergency overnight fallback only |
| DeepSeek V4-Pro as Sonnet-tier routing fallback | Medium | Backlog — K2VV ToolCall F1 gate required; $1.74/M vs $3/M input (42% cheaper); MIT; no Fairford use until benchmarked |
| DeepSeek V4-Flash as Haiku-tier routing fallback | Low | Backlog — $0.14/M; verify task quality on leaf-node workloads; quantized local run expected soon |
| cc-canary thinking_redaction metric — wire as dispatch.py pre-dispatch check | Low | Backlog — surfaces Mar26-Apr10 class harness bugs; retrospective validation of prior dispatch runs possible |

---

## Digest Run 2

**Sources processed:** 2
**Clips:** `2026-04-25-deepseek-v4-willison-analysis.md`, `2026-04-25-willison-claude-code-quality-postmortem-analysis.md`

---

### DeepSeek V4 — Willison Analysis: V4-Pro at $1.74/M Undercuts Sonnet 4.6 — HN High Signal

**Signal strength:** High — strongest open-weight Sonnet-tier routing candidate yet; price advantage confirmed by Willison benchmarks

**Models:**

| Model | Params | Context | Input $/M | Output $/M |
|-------|--------|---------|-----------|------------|
| V4-Flash | 284B / 13B active MoE | 1M | $0.14 | $0.28 |
| V4-Pro | 1.6T / 49B active MoE | 1M | $1.74 | $3.48 |

Both MIT licensed. Available on HuggingFace (865GB Pro / 160GB Flash) and via OpenRouter now.

**Price comparison vs current stack:**
- V4-Pro ($1.74/M) vs Claude Sonnet 4.6 ($3/M) — 42% cheaper on input
- V4-Flash ($0.14/M) vs Haiku 4.5 — potential Haiku-tier replacement
- Net-cheaper despite trailing frontier by ~3–6 months on reasoning tasks

**Performance:** SWE-Verified 80.6%, MCPAtlas 73.6% Pass@1, LiveCodeBench 93.5%. Pelican SVG test: solid but anatomical issues per Willison.

**ClaudesCorner relevance:**

| Use case | Assessment |
|----------|------------|
| dispatch.py Sonnet-tier fallback | V4-Pro viable — K2VV ToolCall F1 gate required first |
| dispatch.py Haiku-tier fallback | V4-Flash $0.14/M compelling — 13B active params, verify quality on leaf-node tasks |
| Fairford work | Blocked until K2VV benchmark clears — silent tool-call serialization failures are the risk |
| 1M context window | dispatch.py MAX_CONTEXT_TOKENS=8000 cap less binding if routing to V4 |

**Action:** Backlog/Medium — run K2VV ToolCall benchmark on V4-Pro before adding routing lane. If F1 + JSON Schema accuracy matches Sonnet 4.6, 42% cost reduction justifies Sonnet-tier routing.

---

### Willison on Claude Code Quality Postmortem — Harness Bugs Hit Long Sessions Hardest

**Signal strength:** High — directly actionable for dispatch.py session health monitoring

**Root cause (three bugs, all fixed in v2.1.116):**

| Bug | Window | Impact |
|-----|--------|--------|
| Reasoning downgraded to medium | Mar 4 – Apr 7 | Silent quality regression |
| Thinking cache cleared every turn | Mar 26 – Apr 10 | Most dangerous — made Claude appear forgetful/repetitive throughout session |
| Verbosity cap regression | Apr 16 – Apr 20 | 3% coding regression |

**Key insight:** The thinking-cache bug ran on every subsequent turn after session idle, not just once. Any extended session (tier 2/3 dispatch.py workers) would have had thinking wiped every turn during Mar26–Apr10. This is invisible without per-session telemetry — looks identical to model quality drift.

**ClaudesCorner assessment:**
- dispatch.py long-session workers were the highest-exposure class during the bug window
- Retrospective audit possible: review dispatch logs Mar26–Apr10 for anomalous token burn, repetition, re-asking answered questions
- dispatch logs start Apr 16 (pre-bug window logs don't exist) — retrospective partially blocked
- cc-canary `thinking_redaction` metric directly surfaces this failure class — should be wired as periodic worker health check
- Current workers already run short one-shot sessions (not multi-turn) — exposure limited vs Willison's persistent sessions

**Action:** Backlog/Low — wire `/cc-canary 30d` as weekly dispatch.py worker health metric. Pre/post v2.1.116 comparison still possible on Apr16+ logs.

---

## Digest Run 3

**Sources processed:** 1
**Clips:** `2026-04-25-microsoft-apm-v092-portable-agent-manifest.md`

---

### Microsoft APM v0.9.2 — Portable Agent Package Manager for Claude Code Stacks — 2k stars

**Signal strength:** High — directly actionable ENGRAM bootstrap artifact; governance docs validate ClaudesCorner's SOUL/HEARTBEAT/skills architecture at enterprise scale

**What it is:** Microsoft's open-source Agent Package Manager (`microsoft/apm`). Declares an agent stack in a single `apm.yml` manifest: instructions, skills, prompts, agents, hooks, plugins, MCP servers, transitive deps. Each version adds governance hardening:

| Version | Addition |
|---------|----------|
| v0.9.0 | `--mcp` declarative flag for MCP server wiring |
| v0.9.1 | Entra ID auth + install-time policy enforcement |
| v0.9.2 | Governance docs; tighten-only org policy; Unicode injection scan |

**Key patterns:**

- **Tighten-only org policy**: permissions can be revoked but never escalated via manifest update — complements `deny:` worker scoping in dispatch.py
- **Unicode injection scan**: sanitizes skill/prompt content at install time — analogous to `_check_injection()` in skill-manager-mcp (added 2026-04-23); apm.yml could adopt ClaudesCorner's regex set
- **Transitive deps**: resolves and locks sub-agent dependencies at install — fills the supply-chain gap identified in the Checkmarx incident audit (mcp-sbom.json created 2026-04-24)
- **GitHub Actions integration**: enables CI-based manifest validation before deployment — relevant for any Fairford Phase 2 CI pipeline

**ClaudesCorner relevance:**

| apm.yml concept | ClaudesCorner analog |
|-----------------|---------------------|
| `instructions:` | `core/SOUL.md` |
| `skills:` | `~/.claude/skills/` + skill-manager-mcp |
| `hooks:` | `settings.local.json` PostToolUse/Stop hooks |
| `mcp_servers:` | `settings.local.json` mcpServers section |
| `agents:` | `scripts/dispatch.py` worker definitions |
| `transitive deps` | `projects/mcp-sbom.json` (partial analog) |

**Gap:** ClaudesCorner has all these components but no single bootstrap manifest. A consumer cloning ENGRAM must manually wire each layer. `apm.yml` provides the missing portable declaration format.

**Action:** Backlog/Medium — author `apm.yml` at ENGRAM repo root declaring SOUL/HEARTBEAT/memory-mcp/skill-manager-mcp as versioned deps. This is the ENGRAM bootstrap artifact that reduces onboarding from "read the README and wire 6 things manually" to `apm install`.

---

## Actionable Items (updated)

| Item | Priority | Status |
|------|----------|--------|
| Stop hooks: exit 2 + stderr required for blocking hooks | Info | **Done** — on_stop.py + PostToolUse hook confirmed correct |
| free-claude-code: FastAPI proxy for open-weight fallback | Low | Backlog — ToS ambiguity + K2VV benchmark required |
| DeepSeek V4-Pro as Sonnet-tier routing fallback | Medium | Backlog — K2VV ToolCall F1 gate required |
| DeepSeek V4-Flash as Haiku-tier routing fallback | Low | Backlog — verify quality on leaf-node tasks |
| cc-canary thinking_redaction metric — weekly dispatch.py health check | Low | Backlog — wire `/cc-canary 30d` pre/post v2.1.116 |
| Microsoft APM v0.9.2 — author apm.yml for ENGRAM bootstrap | Medium | **Done** — `projects/engram/apm.yml` created 2026-04-25; 13-key manifest: instructions/skills/mcpServers/hooks/agents/deps/security |

---

## Digest Run 4

**Sources processed:** 4
**Clips:** `2026-04-25-aivo-multi-provider-coding-agent-cli.md`, `2026-04-25-claude-token-billing-anomalies-hn833.md`, `2026-04-25-stash-persistent-memory-mcp-28-tools.md`, `2026-04-25-vtcode-rust-tui-multi-provider-agent.md`

---

### Aivo — Unified Multi-Provider CLI with Cross-Agent MCP Sessions — 2pts (pre-viral)

**Signal strength:** Medium — interesting cross-agent session sharing primitive; production maturity too early to act on

**What it is:** Unified CLI abstracting provider differences (Anthropic, OpenAI, Google, DeepSeek, Ollama, and more). Key differentiator: `--as reviewer` cross-agent session sharing via MCP — one agent writes, a named peer reads the live session state directly, without file-passing overhead.

**ClaudesCorner relevance:**

| Feature | Assessment |
|---------|------------|
| Multi-provider failover | Mirrors free-claude-code proxy pattern; dispatch.py currently routes by tier but doesn't failover within a tier |
| `--as reviewer` MCP session sharing | Missing cross-worker context primitive — dispatch.py workers currently pass artifacts via task_plan.md files, not live session state |
| SQLite per-session token log | Complements token-dashboard; queryable token burn per agent run = drift detection |
| Free built-in provider + OpenRouter | Zero-cost Haiku-tier fallback during rate-limit saturation |

**Gaps:** 2 HN points = very early; cross-agent session sharing security surface is unknown (shared session = shared context = injection risk); no K2VV benchmark.

**Action:** Backlog/Low — monitor for growth; evaluate `--as reviewer` as dispatch.py cross-worker review primitive once production stability confirmed.

---

### Claude Token Billing Anomalies — Undocumented Monthly Cap + Cache-Clear-on-Break — HN 833pts

**Signal strength:** High — 833pts community signal on undocumented billing behavior directly affecting dispatch.py cost model

**Key undocumented behaviors documented by community:**

| Behavior | Dispatch.py Impact |
|----------|--------------------|
| **Undocumented monthly cap** | Long dispatch weeks may silently hit ceiling not visible in hourly/weekly stats |
| **Cache cleared on forced break** | Tier 2/3 workers that pause mid-session pay double tokens on resume — codebase context must reload |
| **Token window shifted from rolling to Monday reset** | HEARTBEAT.md token availability estimates may be wrong if window is Mon-based not rolling 7d |
| **2 questions → 100% spike post-break** | Per-session budgets don't reset the same way post-break; `MAX_BUDGET_USD` cap still needed |

**Confirmation:** Opus lazy-workaround pattern (generating indirection scripts vs direct edits) is consistent with thinking-cache bug window and Opus 4.7 inflation. Sonnet 4.6 default confirmed correct.

**Action:** Backlog/Low — add `monthly_limit_warning` to health-check `checks.py`; document cache-invalidation-on-break in HEARTBEAT session startup notes; verify Monday vs rolling window.

---

### Stash — 6-Stage Memory Consolidation + 28 MCP Tools — Apache 2.0, 18pts

**Signal strength:** High — most architecturally complete memory consolidation system seen to date; directly addresses memory-mcp gaps

**Architecture:** 6-stage pipeline: Episodes → Facts → Relationships → Causal links → Patterns → Contradiction resolution. Recent additions: goal inference, failure pattern detection, hypothesis scanning. Backend: PostgreSQL + pgvector, 28 MCP tools.

**ClaudesCorner capability gap analysis:**

| Capability | memory-mcp (current) | Stash |
|---|---|---|
| Contradiction resolution | ✗ | ✓ (stage 6) |
| Causal links | ✗ | ✓ (stage 4) |
| Goal inference | ✗ | ✓ |
| **Failure pattern detection** | ✗ | ✓ — directly addresses dispatch.py doom-loop blind spot |
| MCP tools | 10 | 28 |

**Key insight:** Failure pattern detection across sessions is the missing layer in dispatch.py's doom-loop guard. Currently doom-loop detection is intra-session only (3 identical calls in a row). Stash would surface cross-session failure patterns — e.g., worker type X has failed 3 times on YAML-validation tasks.

**Gaps:** PostgreSQL + Docker Compose required (heavy vs sqlite-vec); Windows needs Docker Desktop or WSL2; API stability at 18 HN points unknown.

**Action:** Backlog/Medium — evaluate for ENGRAM v2 write-layer (especially contradiction resolution + causal links); consider as Fairford team memory backend where PostgreSQL is already available.

---

### VT Code — Rust TUI Agent, Multi-Provider Failover, A2A Protocol, Agent Skills — 508 stars

**Signal strength:** Medium — second Rust TUI agent (after claude-code-rust 94 stars); 362 releases = production-grade; A2A protocol adoption worth tracking

**Key capabilities:**

| Feature | ClaudesCorner relevance |
|---------|------------------------|
| Multi-provider failover (OpenAI/Anthropic/Google/DeepSeek/Ollama) | dispatch.py currently stalls on rate-limit; VT Code pattern shows automatic rerouting |
| tree-sitter-bash shell validation | Lightweight alternative to CrabTrap for shell-injection blocking at command-parse level |
| Agent2Agent (A2A) protocol | If dispatch.py workers adopt A2A, inter-worker handoff is standardized vs ad-hoc task_plan.md files |
| ATIF trajectory export | Session replay for doom-loop post-mortems + cc-canary drift detection |
| agentskills.io SKILL.md compatible | Sixth major runtime confirming SKILL.md as de facto standard |

**Gaps:** Windows sandbox (Seatbelt/Landlock) not confirmed; A2A is Google-origin, Anthropic not formally adopted (interop risk); 508 stars modest.

**Action:** Backlog/Low — monitor A2A adoption; if Anthropic endorses A2A, evaluate for dispatch.py inter-worker handoff standardization. tree-sitter-bash validation pattern worth extracting regardless of VT Code adoption.

---

## Actionable Items (Digest Run 4 update)

| Item | Priority | Status |
|------|----------|--------|
| Stop hooks: exit 2 + stderr required for blocking hooks | Info | **Done** |
| free-claude-code: FastAPI proxy for open-weight fallback | Low | Backlog — ToS ambiguity + K2VV benchmark required |
| DeepSeek V4-Pro as Sonnet-tier routing fallback | Medium | Backlog — K2VV ToolCall F1 gate required |
| DeepSeek V4-Flash as Haiku-tier routing fallback | Low | Backlog — verify quality on leaf-node tasks |
| cc-canary thinking_redaction metric — weekly dispatch.py health check | Low | Backlog |
| Microsoft APM v0.9.2 — author apm.yml for ENGRAM bootstrap | Medium | **Done** |
| Aivo cross-agent `--as reviewer` session sharing | Low | Backlog — monitor for production maturity; evaluate vs task_plan.md file passing |
| Claude token billing: monthly_limit_warning in health-check | Low | **Done** — `check_monthly_limit_warning()` added to `checks.py`; 3 notes (monthly cap / cache-clear-on-break / Monday window reset); wired into `run_all()`; 30/31 checks pass |
| Claude token billing: document cache-invalidation-on-break | Low | **Done** — documented in check_monthly_limit_warning() docstring + detail strings |
| Stash failure pattern detection for dispatch.py cross-session doom-loop | Medium | Backlog — evaluate as ENGRAM v2 write-layer; Fairford pgvector backend |
| VT Code A2A protocol for dispatch.py inter-worker handoff | Low | Backlog — monitor Anthropic A2A adoption signal |

---

## Digest Run 5

**Sources processed:** 4
**Clips:** `2026-04-25-wuphf-multi-agent-collaborative-wiki.md`, `2026-04-25-gpt55-prompting-guide-willison.md`, `2026-04-25-memori-agent-native-memory-infrastructure.md`, `2026-04-25-memsearch-markdown-first-agent-memory.md`

---

### WUPHF — Multi-Agent Collaborative Office with Shared Wiki + MCP Tool Scoping — 94 stars

**Signal strength:** High — independent production validation of ENGRAM's two-tier memory model; MCP tool scoping matches dispatch.py tier logic

**What it is:** MIT multi-agent office built on Claude Code. Agents share a two-tier memory: per-agent private notebooks + workspace-wide shared wiki. Three wiki backends: `markdown` (git-native, `~/.wuphf/wiki/`), `Nex` (knowledge graph), `GBrain` (vector search). Launches at `localhost:7891`.

**Performance:**
- 97% cache hit rate via Anthropic prompt caching
- ~87k input tokens/turn → ~40k billable after caching
- 10-turn session: ~286k total tokens
- Push-driven (not polling) → zero idle burn

**ClaudesCorner relevance:**

| Feature | ClaudesCorner analog |
|---------|---------------------|
| Notebook → wiki promotion | `memory/YYYY-MM-DD.md` → memory-mcp durable write |
| 4-tool DM mode vs 27-tool full office | dispatch.py Haiku (4 tools) vs Sonnet (full stack) tier |
| `markdown` backend git-native storage | `memory/YYYY-MM-DD.md` pattern confirmed production-viable at 165 releases |
| `team_wiki_write` tool interface | Reference implementation for ENGRAM's durable write authority model |

**Key insight:** WUPHF independently discovered the same two-tier private/shared memory split that ENGRAM implements. The promotion flow (notebook → wiki) is the same as daily-log → memory-mcp durable write. At 165 releases and 97% cache hit rate, this validates the architecture at production maturity — not just theory.

**Action:** Backlog/Low — evaluate WUPHF's `team_wiki_write` tool interface as reference for memory-mcp write-gate v2; git-native markdown backend confirms ClaudesCorner pattern correct.

---

### GPT-5.5 Prompting Guide — "Treat as New Model Family, Not Drop-In" — Willison

**Signal strength:** High — directly affects any multi-model dispatch routing plan; hardens case for benchmarking gate before routing changes

**Key finding:** OpenAI explicitly advises against migrating existing prompts from GPT-5.2/5.4 to GPT-5.5. Existing prompts break. Reasoning effort, verbosity, tool descriptions, and output formats all require re-tuning from scratch. Minimal-prompt-first rebuild is the required approach.

**Implications for dispatch.py:**

| Implication | Impact |
|------------|--------|
| Prompt incompatibility across model families | Model routing is not a 1-line endpoint swap — requires per-model prompt variants |
| Switching cost from Sonnet 4.6 to GPT-5.5 | Full prompt re-tuning per worker role; cannot reuse existing dispatch prompts |
| K2VV benchmark gate | GPT-5.5 joining DeepSeek V4-Pro and Kimi K2.6 as challengers — all require F1 + JSON Schema accuracy gate before any routing change |
| User-visible progress updates | Agentic UX pattern: short acknowledgment before tool calls prevents perceived freezing — already dispatch.py comment logging |

**ENGRAM implication:** If ENGRAM adds multi-model support, SOUL.md needs a `model:` frontmatter key for per-model instruction variants — otherwise a model switch silently breaks SOUL.md-based behavior.

**Action:** Info/Done — no routing change needed. Sonnet 4.6 default confirmed correct. GPT-5.5 "new family" warning added to model-routing decision criteria: gate requires K2VV ToolCall F1 + full prompt re-tuning budget before adopting any new model family.

---

### Memori — Agent-Native Memory Infrastructure, 81.95% LoCoMo at 5% Token Cost — 13.8k stars

**Signal strength:** High — benchmarked production memory layer directly comparable to memory-mcp; surfaces specific gaps

**Architecture:** Three-tier entity model: Entity (users, places, objects) / Process (agents, programs) / Session (current window). Augmentation: attributes, events, facts, people, preferences, relationships, rules, skills. Intelligent Recall auto-injects relevant context into future prompts.

**Performance (LoCoMo benchmark):**
- 81.95% accuracy at **1,294 tokens per query** (5% of full-context cost)
- 67% smaller prompts vs Zep
- HTTP MCP server — zero-SDK integration with Claude Code, Cursor, Codex, Warp

**Gaps memory-mcp has vs Memori:**

| Capability | memory-mcp | Memori |
|-----------|-----------|--------|
| LoCoMo benchmark score | Unverified | 81.95% |
| Entity/process/session attribution | Not in write payloads | ✓ native |
| Transparent SDK interception | PostToolUse hook (explicit) | Auto-capture via client registration |
| Cross-framework | Claude Code only | LangChain, Pydantic AI, Agno |
| LLM-agnostic | Anthropic only | OpenAI, Anthropic, Bedrock, Gemini, DeepSeek, Grok |

**Actionable:** Benchmark memory-mcp retrieval accuracy against LoCoMo; adopt entity/process/session attribution in memory-mcp write payloads (schema upgrade, backward-compatible); evaluate BYODB mode as memory-mcp backend upgrade path.

**Action:** Backlog/Medium — adopt Memori's entity/process/session attribution schema in memory-mcp `add_memory` tool payloads; benchmark retrieval vs LoCoMo; evaluate BYODB as memory-mcp backend upgrade for ENGRAM v2.

---

### Memsearch — Markdown-First Cross-Platform Agent Memory, BM25+Vector RRF Hybrid — 1.4k stars

**Signal strength:** High — fills three specific technical gaps in brain-memory/memory-mcp that are actionable now

**Architecture:** Markdown files as source of truth → Milvus vector DB as rebuildable shadow index. File watcher with SHA-256 content hashing (skips unchanged files). Hybrid search: dense vector + BM25 sparse with RRF reranking. 3-layer progressive retrieval: semantic chunks → full section expansion → raw transcript.

**By Zilliz** (Milvus maintainers) — production-grade embedding infrastructure background. Supports ONNX bge-m3 (local), OpenAI, Ollama, Google, Voyage, Jina.

**Gaps in brain-memory/memory-mcp vs Memsearch:**

| Gap | Current state | Memsearch solution |
|----|---|---|
| Search quality | all-MiniLM-L6-v2 dense-only | BM25+vector RRF fusion |
| Reindex efficiency | index_all.py re-indexes everything | SHA-256 delta: skip unchanged files |
| Cross-platform | Claude Code only | CC + OpenClaw + OpenCode + Codex via plugins |
| Progressive retrieval | Single-pass semantic search | 3-layer: chunk → section → transcript |

**Key validation:** Memsearch independently converges on `memory/YYYY-MM-DD.md` as correct architecture: markdown-as-source-of-truth + vector index as cache. This is exactly what `projects/brain-memory/` implements. Architecture is confirmed; gaps are in search quality and efficiency.

**Actionable (ranked by impact):**
1. **RRF hybrid search** — add BM25 + dense vector fusion to `brain-memory/src/vectordb.py`; highest quality impact
2. **SHA-256 delta indexing** — skip unchanged files in `index_all.py`; cuts reindex time proportionally to unchanged file ratio
3. **Cross-platform plugin layer** — evaluate memsearch as plugin layer above memory-mcp for ENGRAM v2 multi-platform support

**Action:** Backlog/Medium — (1) add RRF hybrid search to `brain-memory/src/vectordb.py`; (2) add SHA-256 content-hash delta to `index_all.py`; (3) evaluate memsearch as ENGRAM v2 cross-platform plugin layer.

---

## Actionable Items (Digest Run 5 update)

| Item | Priority | Status |
|------|----------|--------|
| Stop hooks: exit 2 + stderr required for blocking hooks | Info | **Done** |
| free-claude-code: FastAPI proxy for open-weight fallback | Low | Backlog — ToS ambiguity + K2VV benchmark required |
| DeepSeek V4-Pro as Sonnet-tier routing fallback | Medium | Backlog — K2VV ToolCall F1 gate required |
| DeepSeek V4-Flash as Haiku-tier routing fallback | Low | Backlog — verify quality on leaf-node tasks |
| cc-canary thinking_redaction metric — weekly dispatch.py health check | Low | Backlog |
| Microsoft APM v0.9.2 — author apm.yml for ENGRAM bootstrap | Medium | **Done** |
| Aivo cross-agent `--as reviewer` session sharing | Low | Backlog — monitor for production maturity |
| Claude token billing: monthly_limit_warning in health-check | Low | **Done** |
| Claude token billing: document cache-invalidation-on-break | Low | **Done** |
| Stash failure pattern detection for dispatch.py cross-session doom-loop | Medium | Backlog — evaluate as ENGRAM v2 write-layer |
| VT Code A2A protocol for dispatch.py inter-worker handoff | Low | Backlog — monitor Anthropic A2A adoption signal |
| WUPHF `team_wiki_write` as memory-mcp write-gate v2 reference | Low | Backlog — evaluate promotion-flow logic |
| GPT-5.5 routing gate: K2VV + full prompt re-tuning required | Info | **Done** — no routing change; Sonnet 4.6 confirmed; gate criteria documented |
| Memori entity/process/session schema in memory-mcp write payloads | Medium | **Done** — optional `entity`/`process`/`session` fields added to `observe` tool inputSchema + handler; bullets now emit `[entity:X][process:Y][session:Z]` attribution inline; backward-compatible (all fields optional); LoCoMo benchmark + BYODB remain Backlog |
| Memsearch RRF hybrid search in brain-memory/src/vectordb.py | Medium | **Done** — already implemented: vectordb.py uses BM25 via FTS5 + dense cosine + RRF fusion (confirmed in docstring + source, 2026-04-25) |
| Memsearch SHA-256 delta indexing in index_all.py | Low | **Done** — already implemented: index_all.py lines 216-229 check content_sha + mtime before re-embedding (confirmed 2026-04-25) |
| Memsearch cross-platform plugin layer for ENGRAM v2 | Low | Backlog — evaluate above memory-mcp |

---

## Digest Run 6

**Sources processed:** 4
**Clips:** `2026-04-25-awesome-codex-skills-composio-mcp-builder.md`, `2026-04-25-claude-howto-visual-guide-advanced-agents.md`, `2026-04-25-surf-cli-browser-automation-ai-agents.md`, `2026-04-25-marmelab-claude-code-tips-day-one.md`

---

### awesome-codex-skills — ComposioHQ SKILL.md Library + mcp-builder Eval Harness — 1.2k stars

**Signal strength:** High — sixth independent SKILL.md org; mcp-builder is first known skill for constructing and testing MCP servers

**What it is:** 50+ SKILL.md modular instruction bundles for Codex CLI/API, organized by Composio (ComposioHQ). Same `skill-name/SKILL.md` dir structure + YAML frontmatter used by Anthropic, OpenAI, HuggingFace, VoltAgent, and marketingskills. **6th major org independently adopting SKILL.md as de facto standard.**

**Key patterns:**

| Pattern | ClaudesCorner relevance |
|---------|------------------------|
| `mcp-builder/` skill | First known skill for *building and testing MCP servers*; eval harness pattern applicable to skill-manager-mcp + memory-mcp pre-release QA |
| `helium-mcp/` | Real-time market data via MCP; Fairford alternative-data complement to Kronos |
| Composio 1000+ app integrations | Action-execution primitive for dispatch.py workers needing external writes |

**Key insight:** The SKILL.md de facto standard now spans Anthropic, OpenAI, HuggingFace, VoltAgent, marketingskills, and Composio — all without coordination. ENGRAM portability story is empirically provable across 6 runtimes.

**Action:** Backlog/Low — evaluate `mcp-builder` eval harness pattern for pre-release MCP server validation; monitor `helium-mcp` as Fairford alternative-data signal layer.

---

### claude-howto — Visual Claude Code Guide, 28 Hook Events, 28.8k Stars — MIT

**Signal strength:** High — most comprehensive public reference for Claude Code hook surface area; 28 hook events vs ClaudesCorner's current 2 (Stop + PostToolUse)

**Key gaps surfaced:**

| Module | Gap | Action |
|--------|-----|--------|
| Hooks (28 events, 5 types) | PreToolUse, UserPromptSubmit, PreCompact not used in dispatch.py | Audit on_stop.py + dispatch.py hooks against this list |
| Subagents | Isolated-context templates for code review, testing, security | Copy-paste starting points for ENGRAM worker definitions |
| Checkpoints | Session rewind not used in dispatch.py | Relevant for long-horizon worker recovery on context exhaustion |
| MCP config templates | `.mcp.json` patterns for GitHub, databases | Compare against current settings.json for gaps |

**ENGRAM value:** 28.8k stars + MIT + current (v2.1.119) = citable community reference for ENGRAM README agent patterns; validates SOUL.md per-agent isolation principle.

**Action:** Backlog/Low — audit dispatch.py/on_stop.py hooks against 28-event list; evaluate PreToolUse hook for token-burn telemetry; use as ENGRAM README reference.

---

### Surf-CLI — Zero-Config CLI Browser Automation for AI Agents — 453 stars, MIT

**Signal strength:** Medium — simpler browser automation alternative to chrome-devtools-mcp; CLI-first = dispatch.py worker compatible without MCP wiring

**What it is:** CLI + Unix socket browser automation via Chrome DevTools Protocol. No API keys. Commands: navigate, extract accessibility tree, click/type, screenshot (auto-resize to 1200px), network log/replay. Multi-browser: Chrome, Brave, Edge, Arc, Chromium. **Windows: experimental.**

**dispatch.py fit:**

| Feature | Assessment |
|---------|------------|
| CLI-first (no MCP wiring) | `surf` invokable as shell command from BUILD/RESEARCH workers |
| 1200px screenshot auto-resize | Real token saver given Opus 4.7 3.01× image inflation |
| Window isolation | One Surf instance per dispatch.py worker without cross-contamination |
| AI query bridge (ChatGPT/Gemini/Perplexity) | Reuse browser auth — no new credentials per worker |
| Windows experimental | Test before committing — may fail on current Windows 11 environment |

**vs chrome-devtools-mcp:** Surf is lighter (CLI) and simpler; chrome-devtools-mcp is richer (29 tools, slim mode, npx install) and MCP-native. Surf better fit for dispatch.py leaf nodes needing occasional scraping; chrome-devtools-mcp for full-session automation.

**AI Subroutines complement:** Surf's workflow mode (deterministic multi-step sequences) = execution layer; AI Subroutines (clipped 2026-04-18) = recording layer. Pair for record-once/replay-N browser tasks.

**Action:** Backlog/Low — evaluate Surf-CLI as dispatch.py RESEARCH worker browser primitive on Windows (test experimental support first); compare slim chrome-devtools-mcp (3 tools) vs Surf for lowest-overhead dispatch worker use.

---

### Marmelab — Claude Code Production Tips: Error Compounding + CLAUDE.md Hygiene + Session Retrospectives

**Signal strength:** High — production-validated patterns that directly reinforce or extend existing dispatch.py + HEARTBEAT.md architecture; one new check implemented immediately

**Key insight:** *"The human bottleneck was a feature, not a bug. At human pace, errors compound slowly. With an army of agents, small mistakes compound at a rate that outruns your ability to catch them."* — clearest articulation of why dispatch.py needs doom-loop detection + verify oracles.

**Actionable patterns:**

| Pattern | Status |
|---------|--------|
| CLAUDE.md 200-line limit | **Done** — `check_claude_md_size()` added to health-check/checks.py (2026-04-25); both global (41 lines) and project (31 lines) pass |
| Bug documentation (investigate → ADR → fix) | Maps to `feedback_flywheel.py` + SELF_IMPROVEMENT.md — already in place |
| Session retrospective via on_stop.py | Not implemented — `on_stop.py` does skill extraction + AutoDream gate only; add retrospective distillation step |
| AGENTS.md alongside CLAUDE.md | Not present in ClaudesCorner; cross-agent portability (OpenClaw/Hermes/Codex compat) |
| Context7 Plugin (library docs at pinned versions) | Not wired — prevents dispatch.py workers hallucinating stale MCP API signatures |

**Action:** Backlog/Low — (1) add session retrospective step to on_stop.py Stop hook; (2) author AGENTS.md for cross-agent portability; (3) evaluate Context7 Plugin for dispatch.py worker library-doc grounding.

---

## Actionable Items (Digest Run 6 update)

| Item | Priority | Status |
|------|----------|--------|
| Stop hooks: exit 2 + stderr required for blocking hooks | Info | **Done** |
| free-claude-code: FastAPI proxy for open-weight fallback | Low | Backlog — ToS ambiguity + K2VV benchmark required |
| DeepSeek V4-Pro as Sonnet-tier routing fallback | Medium | Backlog — K2VV ToolCall F1 gate required |
| DeepSeek V4-Flash as Haiku-tier routing fallback | Low | Backlog — verify quality on leaf-node tasks |
| cc-canary thinking_redaction metric — weekly dispatch.py health check | Low | Backlog |
| Microsoft APM v0.9.2 — author apm.yml for ENGRAM bootstrap | Medium | **Done** |
| Aivo cross-agent `--as reviewer` session sharing | Low | Backlog — monitor for production maturity |
| Claude token billing: monthly_limit_warning in health-check | Low | **Done** |
| Claude token billing: document cache-invalidation-on-break | Low | **Done** |
| Stash failure pattern detection for dispatch.py cross-session doom-loop | Medium | Backlog — evaluate as ENGRAM v2 write-layer |
| VT Code A2A protocol for dispatch.py inter-worker handoff | Low | Backlog — monitor Anthropic A2A adoption signal |
| WUPHF `team_wiki_write` as memory-mcp write-gate v2 reference | Low | Backlog — evaluate promotion-flow logic |
| GPT-5.5 routing gate: K2VV + full prompt re-tuning required | Info | **Done** — no routing change; Sonnet 4.6 confirmed |
| Memori entity/process/session schema in memory-mcp write payloads | Medium | **Done** — optional `entity`/`process`/`session` fields added; backward-compatible |
| Memsearch RRF hybrid search in brain-memory/src/vectordb.py | Medium | **Done** — already implemented: BM25+FTS5+dense+RRF in vectordb.py (confirmed 2026-04-25) |
| Memsearch SHA-256 delta indexing in index_all.py | Low | **Done** — already implemented: content_sha+mtime delta in index_all.py lines 216-229 (confirmed 2026-04-25) |
| Memsearch cross-platform plugin layer for ENGRAM v2 | Low | Backlog — evaluate above memory-mcp |
| awesome-codex-skills mcp-builder: MCP eval harness pattern | Low | Backlog — apply to skill-manager-mcp + memory-mcp pre-release QA |
| claude-howto: audit dispatch.py hooks against 28-event list | Low | **Done** — Global settings: Stop/SessionStart/PreCompact/PostCompact/PostToolUse(×2) all wired; project: PostToolUse(index_all). Two gaps: PreToolUse (no pre-execution gate) + UserPromptSubmit (no prompt-level injection scan). PreCompact was already wired (on_pre_compact.py) — not a gap as synthesis originally noted. Documented 2026-04-25. |
| Surf-CLI as dispatch.py RESEARCH browser primitive (Windows) | Low | Backlog — test Windows experimental support before committing |
| Marmelab CLAUDE.md 200-line limit check | Low | **Done** — `check_claude_md_size()` added to health-check/checks.py; both files pass (41/31 lines) |
| Marmelab session retrospective in on_stop.py | Low | Blocked (auto mode) — on_stop.py at C:\claude-hooks\ outside ClaudesCorner write scope; requires Jason approval |
| Marmelab AGENTS.md for cross-agent portability | Low | **Done** — `AGENTS.md` created 2026-04-25; BUILD/RESEARCH/MEMORY worker defs, model tiers, deny clauses, hooks, MCP servers, security; OpenClaw/Hermes/Codex/Codex compat |
