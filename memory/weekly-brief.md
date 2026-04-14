# Weekly Brief — 2026-04-14

## Fabric & Microsoft tooling

## Updated 2026-04-01

- **Failure notifications for scheduled jobs** (GA) — email alerts when scheduled Fabric jobs fail. Configure per-item, applies to all schedules. Directly useful for Clementine pipeline monitoring.
- **Fabric Maps** (FabCon) — geospatial intelligence layer for real-time analytics
- **Fabric IQ** (FabCon) — semantic intelligence layer, shared version of reality across enterprise data
- **Fabric Data Agents** (GA, confirmed) — support Lakehouse, Warehouse, semantic models, SQL databases
- **OneLake ↔ Snowflake interop** — Fabric's unified lake now reads/writes Snowflake natively
- **Workload Management tab in Admin Portal** — centralized view of all workloads in tenant, manage via UI


## Updated 2026-04-14 (r/MicrosoftFabric community pulse)

### Hot discussions
- **Fabric Data Agents + RLS** — users asking how to wire D365 FO star schema models to Data Agents while preserving row-level security via Azure OpenAI. No clean answer yet — active pain point.
- **Power BI team blocking 3P Semantic Layers** — post with 36 comments. Community friction around Microsoft locking out third-party semantic layer integrations. Worth watching.
- **Pure Python notebooks with 3.12** (Microsoft Employee post, 50+ upvotes) — Python 3.12 support in notebooks now available. Significant for data science workloads.
- **FabCon corenote presentations accessible** (Microsoft Employee FabricPam, 119 upvotes) — FabCon session recordings/slides now public.
- **Fabric CI/CD via Azure DevOps: cross-workspace .pbir connections** — active discussion on how to handle cross-workspace Power BI report connections in DevOps pipelines. Relevant to Clementine.
- **Lakehouse SQL endpoint can't see tables, Spark can** — recurring issue, 11 comments. Delta sync lag between Spark and SQL endpoint is still a common pain point.
- **Copilot Studio Agent doesn't render output from Fabric Agent** — known issue with Copilot Studio + Fabric Agent integration.
- **Export data destination in Power Query Template (Dataflow Gen2)** — Microsoft Employee sharing new feature for exporting destination definitions.
- **Soft delete: Data vs Items, 7 vs 14 days retention** — governance question on deletion policies. Admin topic.
- **OneLake Row and Column Security** (Fabric Monday series) — community education post on RLS/CLS in OneLake.
- **Failed DP-600** — active thread with 5 comments on exam difficulty/prep strategies. (Note: DP-600 = Fabric Analytics Engineer cert, different from DP-700 = Data Engineer.)

### Signals
- Data Agents adoption friction is real — RLS integration not well-documented yet
- Python 3.12 in notebooks is a quiet but meaningful upgrade
- CI/CD cross-workspace PBIR connection handling is an unsolved problem for most teams

---

## Claude Code updates

## Claude Code (v2.1.107 / April 14, 2026)

- **Show thinking hints sooner** during long operations


## Relevant to us (new)
- **`refreshInterval` status line** — could make `/status` skill auto-refresh without manual invocation
- **Monitor tool** — useful for streaming heartbeat/background script output into session
- **`PreCompact` hook** — can block compaction mid-task if needed; complements existing PostCompact flush
- **`/proactive` alias for `/loop`** — nice ergonomic alias
- **OS CA cert trust by default** — resolves enterprise TLS proxy issues on Numberskills-Internal network
- **Effort default now `high`** — may increase token usage; worth monitoring on rate-limited sessions
- **Security fixes in v2.1.98/2.1.101** — Bash permission bypasses and command injection fixed; update ASAP if not already on latest
- **`CLAUDE_CODE_PERFORCE_MODE`** — not relevant (no Perforce), but signals Anthropic supporting more enterprise VCS patterns

---

## Community signals (Reddit)

## Subreddits to add later
- r/deeplearning
- r/computervision
- r/Python

---

## Open blockers / pending tasks

  - [ ] [blocker] Fairford PoC Phase 2 — design delivered 2026-03-30, no implementation plan; needs Jason's next step
