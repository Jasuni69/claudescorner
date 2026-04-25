---
title: "Daemons (Charlie Labs) — Markdown-Defined AI Background Processes"
date: 2026-04-21
source: https://charlielabs.ai/
tags: [ai-agents, background-processes, automation, dispatch, heartbeat]
points: 12
---

# Daemons (Charlie Labs) — Markdown-Defined AI Background Processes

**Source**: HN Show HN, 12pts — charlielabs.ai  
**Signal**: "Agents create work. Daemons maintain it." — Markdown frontmatter-configured background AI processes with event+schedule triggers; structural complement and naming clarification for dispatch.py task queue architecture.

## What It Is

Daemons are self-initiated AI background processes defined in `.md` files that automatically maintain code repositories and projects. They complement agents (human-initiated) by handling ongoing operational debt without requiring prompts.

## How It Works

Each daemon is defined in a `.md` file with two sections:

**Frontmatter** (between `---` fences):
```yaml
name: dependency-patcher
purpose: Keep dependencies up to date
watch: [pull_request.opened, schedule.daily]
routines:
  - check stale deps on PR open
  - run weekly audit sweep
deny:
  - merge without human approval
  - modify lockfile in protected branches
```

**Markdown body**: policies, output formats, escalation rules, limits

**Activation modes**:
- Event-based: PR opened, issue created, code merged
- Scheduled sweeps: daily, every 6h, etc.
- Hybrid: both combined

## Key Features

- Portable spec format — works across GitHub, Linear, Sentry, Slack, Docs
- Bounded scope via explicit `deny:` rules
- Accumulating context — improves over time without manual updates
- Team-editable config — modified like any repo file
- Continuous observation with zero maintenance

## Relevance to ClaudesCorner

- **dispatch.py vs Daemons**: dispatch.py is currently task-queue driven (pull model). Daemons pattern = push model triggered by events or schedule. Adopting `.md` frontmatter spec for dispatch worker definitions would make task config human-readable and version-controlled.
- **HEARTBEAT.md**: The daemon concept formalizes what HEARTBEAT already does informally — session state + pending tasks as an operational document. Daemon `watch:` + `routines:` maps directly to HEARTBEAT pending tasks + scheduled triggers.
- **Naming insight**: "Agents create work, Daemons maintain it" is a useful conceptual split for ENGRAM documentation — dispatch.py workers = daemons, not agents.
- **deny: rules**: Explicit denial lists in daemon spec = missing safety layer in current dispatch.py worker prompts. Worth adding `deny:` equivalent to worker system prompts.
- **Event-triggered execution**: Current dispatch.py runs on 2h cron. Event-based triggers (PR, issue, file change) would enable reactive maintenance tasks — complement to existing scheduled runs.

## Action Items

- Add `deny:` rule equivalent to dispatch.py worker system prompts (bounded scope)
- Consider adopting daemon `.md` frontmatter format for defining dispatch worker task specs
- Evaluate event-triggered worker invocations alongside current 2h scheduled cron
- Use "daemon" terminology in ENGRAM docs to distinguish maintenance workers from interactive agents
