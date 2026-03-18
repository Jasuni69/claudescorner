# OpenClaw Docs — Study Notes
> Read 2026-03-18. Source: docs.openclaw.ai

## What OpenClaw Is
A self-hosted AI agent gateway — persistent sessions, scheduled automation, hooks, multi-channel messaging. Their architecture mirrors what we've built manually in Claude's Corner.

---

## Key Concepts & What We Can Steal

### 1. Agent Loop
- Runs: intake → context assembly → model inference → tool execution → streaming → persistence
- Per-session serialization (queue per session key) — prevents race conditions
- Timeout: 600s hard limit, agent.wait defaults 30s
- **For us:** claw.py already serializes tasks. Worth enforcing an explicit timeout.

### 2. System Prompt Construction
They auto-inject bootstrap files per turn: AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md, BOOTSTRAP.md
- Max 20,000 chars per file (`bootstrapMaxChars`)
- Memory files in `memory/*.md` are on-demand, NOT auto-injected
- Three prompt modes: Full (primary agent), Minimal (sub-agents), None (identity only)
- **For us:** We already do SOUL.md + HEARTBEAT.md. We're missing TOOLS.md and IDENTITY.md as structured files. Worth adding.

### 3. Context
- `/context list` and `/context detail` commands for inspecting token usage
- Compaction: summarize old history, preserve recent messages
- Pruning: remove old tool results without modifying transcript
- **For us:** Our context-pack.py does manual compaction. Solid.

### 4. Context Engine (Plugin)
- Pluggable system: ingest → assemble → compact → after_turn lifecycle
- `assemble` can inject dynamic system prompt additions — powerful for RAG
- `ownsCompaction` flag to take over compaction strategy
- **For us:** Our memory-mcp + search_memory is essentially a lightweight context engine. The `systemPromptAddition` pattern (inject retrieved memory into prompt dynamically) is worth implementing.

### 5. Agent Workspace
- Default: `~/.openclaw/workspace` — maps exactly to our `E:\2026\Claude's Corner\`
- Standard files: AGENTS.md, SOUL.md, USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, memory/YYYY-MM-DD.md
- Security: private git repo, no secrets in workspace
- **For us:** We're already aligned. Missing: TOOLS.md (notes on local tools), IDENTITY.md (separate from SOUL).

### 6. Hooks ⭐ Most actionable
Event-driven scripts that fire on: command:new, command:reset, command:stop, session:compact:before/after, agent:bootstrap, gateway:startup, message:received/sent

**Bundled hooks we should replicate:**
- `session-memory`: saves session context to memory/YYYY-MM-DD-slug.md on /new — we do this manually at session end
- `bootstrap-extra-files`: injects additional files per-agent — useful for project-specific context
- `command-logger`: JSONL audit trail of all commands
- `boot-md`: runs BOOT.md instructions at gateway startup — we have heartbeat.ps1 doing similar

**Hook structure:**
```
my-hook/
├── HOOK.md    # YAML frontmatter: name, events, emoji, requirements
└── handler.ts # async (event) => void
```

**For us:** Claude Code has hooks! (`~/.claude/settings.json` hooks section). We can implement:
- Pre-tool-use hooks (e.g., log all bash commands)
- Post-tool-use hooks (e.g., update HEARTBEAT after file edits)
- Session end hooks (memory flush trigger)

### 7. Cron vs Heartbeat ⭐ Very applicable
| Use | Mechanism |
|-----|-----------|
| Periodic ambient checks (inbox, calendar) | Heartbeat (batched, context-aware) |
| Exact time ("9am daily report") | Cron (isolated) |
| One-shot reminder | Cron with --at |
| Background project health | Heartbeat |

**Key insight:** Heartbeat replies `HEARTBEAT_OK` silently if nothing needs attention. We should implement this — our heartbeat currently always writes output.

**Their HEARTBEAT.md pattern:**
```md
# Heartbeat checklist
- Check email for urgent messages
- Review calendar for events in next 2 hours
- If a background task finished, summarize results
- If idle for 8+ hours, send a brief check-in
```

**For us:** Our HEARTBEAT.md is currently state/log hybrid. Should split:
- HEARTBEAT.md = checklist (what to DO each run)
- Session state tracked separately

---

## Action Items (Priority Order)

1. **Add TOOLS.md** — document local tools: python path, node, powershell, mcp servers, scripts
2. **Add IDENTITY.md** — separate identity file (name, characteristics) vs SOUL.md (purpose/context)
3. **Restructure HEARTBEAT.md** — make it a checklist, not a state dump
4. **Implement HEARTBEAT_OK** — silent exit in heartbeat.ps1 when nothing actionable
5. **Explore Claude Code hooks** — especially post-session hooks for auto memory flush
6. **session-memory pattern** — auto-save session to memory/YYYY-MM-DD-slug.md on session end (not just manual flush)

---

## What We Already Have That They Document
- ✅ SOUL.md (persona)
- ✅ HEARTBEAT.md (periodic run)
- ✅ memory/YYYY-MM-DD.md (daily logs)
- ✅ Scheduled tasks (Windows Task Scheduler = their cron)
- ✅ Memory MCP (search_memory = their context engine)
- ✅ claw.py (their agent runner / task dispatcher)
- ✅ Private git repo

## What We're Missing
- ❌ TOOLS.md
- ❌ IDENTITY.md
- ❌ HEARTBEAT_OK silent suppression
- ❌ session-memory auto-hook (we do it manually)
- ❌ command-logger (JSONL audit trail)
- ❌ Structured hook system (we have heartbeat.ps1 but not event-driven hooks)
