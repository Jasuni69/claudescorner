---
title: "Lovable Users Report Leak of Chats, Code, Credentials — Third Incident in 12 Months"
date: 2026-04-21
source: https://awesomeagents.ai/news/lovable-breach-chat-source-code-credentials/
tags: [security, vibe-coding, ai-agents, credentials, supabase, rls, agentkey]
relevance: high
---

# Lovable Users Report Leak of Chats, Code, Credentials

**Source:** awesomeagents.ai | **Date:** April 2026

## Summary

Free Lovable accounts could access other users' sensitive data through Supabase tables lacking Row Level Security (RLS). Projects created before November 2025 were exposed. This is the **third documented incident** in 12 months involving the same structural flaw.

## What Was Exposed

- AI chat histories and prompts
- Source code from generated applications
- Database credentials (including apparent OpenAI API keys)
- Customer records and user data from deployed apps

## How It Happened

Core vulnerability: Lovable's AI generated database schemas without enabling RLS protection.

```sql
create table public.user_messages (...)
-- Missing: ALTER TABLE ... ENABLE ROW LEVEL SECURITY
```

Any authenticated client could read entire tables. Default-insecure Supabase configuration propagated into generated code at scale.

## Scale

- **Lovable**: ~$400M ARR, 146 employees — high-profile AI dev toolchain
- May 2025: CVE-2025-48757 — 170 production apps, 303 unprotected endpoints
- October 2025: Security firm Escape found vulnerabilities across 5,600 vibe-coded apps
- April 2026: Third incident, same root cause

## Why This Keeps Happening

1. **AI code generation inherits defaults** — LLMs generate the happy path; security hardening (RLS, auth guards, secrets scanning) is non-default behavior that must be explicitly prompted or enforced post-generation
2. **Credential co-location** — vibe-coding platforms store API keys, DB credentials, and code in the same project context; one breach exposes all three simultaneously
3. **Structural flaw persistence** — patching the platform doesn't retroactively fix generated code already deployed; the blast radius grows with user count

## Relevance to ClaudesCorner / Fairford

- **AgentKey pattern validated** — centralized credential governance with agent-specific scoped tokens prevents the co-location failure mode; each agent should hold the minimum credential surface
- **dispatch.py workers** should never store external credentials in generated output; secrets must flow through environment variables or secret managers, never code artifacts
- **ENGRAM security posture** — memory-mcp must not persist credential strings; any write_memory call containing API keys should be filtered at the MCP layer
- **Fairford Phase 2** — if fabric-mcp generates any client-facing schemas (Power BI datasets, Fabric lakehouses), RLS must be an explicit step in the generation checklist, not an afterthought
- The "third incident, same root cause" pattern confirms: one-time security patches don't fix systemic generation defaults; the fix must be in the generator prompt, not the platform
