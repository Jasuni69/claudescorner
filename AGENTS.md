# AGENTS.md — ClaudesCorner Cross-Agent Portability

> Machine-readable companion to CLAUDE.md.
> Declares worker roles, model tiers, tool scopes, and deny clauses
> so runtimes other than Claude Code (OpenClaw, Hermes, Codex, etc.)
> can boot the same agent stack without manual wiring.

## Identity

```yaml
identity:
  name: ClaudesCorner
  soul: core/SOUL.md
  heartbeat: core/HEARTBEAT.md
  memory_mcp: projects/memory-mcp/server.py
  base: E:\2026\ClaudesCorner
```

## Agents

### BUILD

```yaml
name: BUILD
role: Infrastructure + code implementation worker
model: claude-sonnet-4-6          # Tier 2 default
max_turns: 30
timeout_seconds: 300
context_tokens_soft_cap: 8000
instructions: >
  You are a BUILD agent. Check HEARTBEAT.md for pending [ ] tasks.
  Execute using 3-step SPEC → BUILD → VERIFY protocol.
  Run the oracle after every task:
    python -c "import re,datetime; txt=open('E:/2026/ClaudesCorner/core/HEARTBEAT.md').read();
    done=re.findall(r'- \\[x\\].*',txt); logs=re.findall(r'### (2026-\\d\\d-\\d\\d)',txt);
    today=str(datetime.date.today()); assert done; assert any(today in l for l in logs);
    print(f'OK: {len(done)} done tasks')"
deny:
  - push to external repos
  - modify ~/.claude/settings.json
  - delete files outside E:\2026\ClaudesCorner
  - make network requests except to read documentation
tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - Bash
  - mcp__memory-mcp__*
  - mcp__skill-manager__*
```

### RESEARCH

```yaml
name: RESEARCH
role: Research digest + synthesis worker
model: claude-sonnet-4-6
max_turns: 20
timeout_seconds: 300
context_tokens_soft_cap: 8000
instructions: >
  You are a RESEARCH agent. Read undigested clips from research/*.md.
  Synthesize signals into research/YYYY-MM-DD-synthesis.md.
  Update the ## Actionable Items table.
  Log completion to HEARTBEAT.md.
deny:
  - push to external repos
  - modify any file outside E:\2026\ClaudesCorner
  - execute code (read-only research mode)
tools:
  - Read
  - Glob
  - Grep
  - WebSearch
  - mcp__memory-mcp__search_memory
  - mcp__memory-mcp__observe
```

### MEMORY

```yaml
name: MEMORY
role: Memory hygiene + consolidation worker
model: claude-haiku-4-5-20251001  # Tier 1 — narrow repetitive task
max_turns: 15
timeout_seconds: 180
context_tokens_soft_cap: 4000
instructions: >
  You are a MEMORY agent. Flush session state to persistent storage:
  update HEARTBEAT.md log, write memory/YYYY-MM-DD.md daily log,
  update MEMORY.md index. Run the HEARTBEAT oracle after.
deny:
  - modify code files (*.py, *.ts, *.js)
  - push to external repos
tools:
  - Read
  - Edit
  - Write
  - mcp__memory-mcp__*
```

## Dispatcher

```yaml
dispatcher: scripts/dispatch.py
workers: 3
schedule: every 2h via Windows Task Scheduler
task_queue: tasks.json
worktree_isolation: DISPATCH_WORKTREES=1 (opt-in)
outbound_proxy: CRABTRAP_PROXY=http://localhost:8080 (opt-in)
budget_cap: MAX_BUDGET_USD=<float> (opt-in)
doom_loop_guard: halt after 3 identical tool calls with no progress
```

## Hooks

```yaml
hooks:
  Stop:
    script: C:\claude-hooks\on_stop.py
    behavior: non-blocking (exit 0); dispatches tasks or spawns idle activity
  PostToolUse:
    tools: [Write, Edit]
    behavior: non-blocking (exit 0); indexes changed files into vectorstore.db
```

## MCP Servers

```yaml
mcp_servers:
  - name: memory-mcp
    path: projects/memory-mcp/server.py
    tools: 10
    model: search_memory (primary entry point)
  - name: skill-manager-mcp
    path: projects/skill-manager-mcp/server.py
    tools: 9
    model: skill_search (primary entry point)
  - name: fabric-mcp
    path: projects/fabric-mcp/server.py
    tools: 7
    auth: MSAL + mock mode (FABRIC_MOCK=true)
  - name: markitdown-mcp
    path: projects/markitdown-mcp/server.py
    tools: 3
  - name: deadlines-mcp
    path: projects/deadlines-mcp/server.py
    tools: expose_deadlines
  - name: windows-mcp
    path: projects/windows-mcp/server.py
    tools: 4 (run_ps1, read_event_log, list_scheduled_tasks, get_system_info)
```

## Security

```yaml
security:
  injection_guard: unicode_injection_scan at skill_create/skill_edit (skill-manager-mcp v2.6.0)
  credential_scan: 10 patterns; fail-closed on sk-/ghp_/JWT/Bearer (skill-manager-mcp v2.6.0)
  outbound_filter: CrabTrap MITM proxy (optional; SSRF + prompt-injection-via-URL blocking)
  tighten_only: deny: clauses in worker prompts cannot be escalated at runtime
  caller_auth: FABRIC_CALLER_TOKEN bearer check in fabric-mcp (pre-Fairford Phase 2)
```
