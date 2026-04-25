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
