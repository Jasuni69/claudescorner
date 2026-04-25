---
title: "safer — Read-Only-by-Default Shell Guardrail for AI Agents"
date: 2026-04-24
source: https://github.com/crufter/safer
hn_pts: 1
tags: [agent-security, dispatch, shell, guardrail, go]
relevance: high
---

# safer — Read-Only-by-Default Shell Guardrail for AI Agents

**Repo**: github.com/crufter/safer  
**Language**: Go  
**License**: not specified  
**HN thread**: Show HN (newest, ~1pt at clip time)

## What It Does

`safer` is a command wrapper that intercepts shell commands before execution and enforces a **read-only-by-default** policy. When an AI coding agent has full shell access, `safer` acts as a zero-code behavioral guardrail — no sandbox, no VM, just a pre-execution check.

Known read-only commands (`cat`, `ls`, `kubectl get`, etc.) pass automatically. Everything else is blocked unless the agent's invocation includes an explicit capability flag.

## Capability Flag Model

| Flag | Shorthand | Allows |
|------|-----------|--------|
| `--data-write` | `--dw` | Workspace and database writes |
| `--data-delete` | `--dd` | Destructive removal operations |
| `--env-ephemeral` | `--ee` | Temporary runtime changes |
| `--env-persistent` | `--ep` | Infrastructure modifications (terraform, etc.) |
| `--allow-unknown` | | Any unrecognized command |

On a blocked command, `safer` exits with status code **2** and prints a clear alert — the agent sees an explicit rejection instead of silently proceeding.

## Scope of Coverage

The tool inspects ~20+ tools including: `kubectl`, `docker`, `terraform`, `git`, `npm`, `psql`, and shell scripts. It also analyzes nested payloads (SQL flags, embedded shell scripts) — not just the top-level command name.

## Architecture

- Written in Go, single binary, no dependencies
- Wraps the target command via exec; agents invoke `safer <original-command> [flags]`
- **Not a sandbox** — no VM isolation, no network filtering; purely behavioral
- Exits with code 2 on block (agent-readable signal)

## Signal for ClaudesCorner

dispatch.py workers run shell commands with broad permissions. `safer` is the simplest possible behavioral layer before the existing CrabTrap (outbound) + AgentKey (identity) + AgentRQ (escalation) governance stack.

**Actionable**: Wire `safer` as the shell wrapper in dispatch.py worker exec calls. Workers that need destructive capability must explicitly declare it in their prompt's `deny:` / capability block — this makes destructive intent visible in the task plan rather than buried in execution.

Complement to the existing stack:
- CrabTrap: outbound HTTP filtering
- AgentKey: identity + credential governance  
- AgentRQ: human-in-loop escalation
- **safer**: pre-execution shell command guardrail ← new layer

## Contrast With Existing Approach

Current dispatch.py workers use `deny:` frontmatter to bound scope. `safer` enforces this at the OS level rather than prompt level — prompt-level deny clauses can be overridden by model drift; `safer` cannot.
