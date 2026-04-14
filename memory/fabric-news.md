# Fabric News — March 2026

Sourced 2026-03-19 from [Fabric March 2026 Feature Summary](https://blog.fabric.microsoft.com/en-us/blog/fabric-march-2026-feature-summary?ft=All)

## Key highlights

- **Runtime 2.0** (preview): Spark 4.x, Delta Lake 4.x, Scala 2.13, Azure Linux Mariner 3.0
- **Materialized lake views** now GA — simplifies medallion architecture, no manual orchestration
- **Branched workspaces** — clearer dev experience for feature branches, EOM March
- **Selective branching** — branch only the items you need, less clutter
- **Planning in Fabric IQ** — enterprise planning (budgets, forecasts, scenarios) on top of semantic models
- **Workload Management Admin APIs** — REST governance for workloads across tenant
- **Self-service workload publishing** GA EOM March — ISVs publish to customer tenants directly
- **Agent Skills for Fabric** (open source) — natural language Fabric ops via GitHub Copilot terminal
- **Fabric Jumpstart** (open source) — reference architectures + single-click sample deployments
- **FabCon + SQLCon 2026** — major conference, unifying databases + Fabric on single platform

## Updated 2026-03-20

- **OneLake Catalog Search API** — cross-workspace asset discovery for code and AI agents
- **Workspace Tags** (GA) — governance metadata via APIs
- **DLP Policies** — extended to warehouses, KQL databases, SQL databases
- **Fabric Data Agents** (GA) — support Lakehouse, Warehouse, semantic models, SQL databases
- **AutoML** (GA) — end-to-end UI for model training, comparison, deployment
- **Fabric Remote MCP Server** — AI agents can perform real Fabric operations
- **Warehouse Recovery** (Preview) — restore dropped warehouses with data + schemas intact
- **T-SQL AI Functions** — analyze unstructured text directly in SQL queries
- **Custom Live Pools** — warm pre-configured Spark clusters for consistent SLAs
- **Notebook Public APIs** (GA) — full CRUD + on-demand execution via Job Scheduler
- **Fabric CLI v1.5** — CI/CD deployments + AI agent integration from terminal

## Updated 2026-03-31

- **Fabric Graph** (FabCon) — scalable graph database for modeling relationships across enterprise data
- **OneLake Interoperability Expansion** (FabCon) — unified data lake now supports Snowflake interop
- **Branched Workspace** (end of March 2026, GA) — new dev experience for feature workspaces; visual cues for workspace relationships when branching. Cleaner isolation per feature.
- **Selective Branching** — branch-out only the items you need for a feature, not the full workspace. Reduces clutter, improves reliability. Relevant to Clementine multi-notebook dev workflow.
- **Workload Management Admin APIs** — REST API to list/manage workloads across tenant. For admins. Governance play.
- **Self-Service Workload Publishing** (GA, end of March) — ISV partners publish to customer tenants for private preview without manual submission. Relevant if Numberskills ever packages Clementine as a product.

## Updated 2026-04-01

- **Failure notifications for scheduled jobs** (GA) — email alerts when scheduled Fabric jobs fail. Configure per-item, applies to all schedules. Directly useful for Clementine pipeline monitoring.
- **Fabric Maps** (FabCon) — geospatial intelligence layer for real-time analytics
- **Fabric IQ** (FabCon) — semantic intelligence layer, shared version of reality across enterprise data
- **Fabric Data Agents** (GA, confirmed) — support Lakehouse, Warehouse, semantic models, SQL databases
- **OneLake ↔ Snowflake interop** — Fabric's unified lake now reads/writes Snowflake natively
- **Workload Management tab in Admin Portal** — centralized view of all workloads in tenant, manage via UI

## Updated 2026-04-14 (blog)

- **ALTER TABLE inside explicit transactions in Fabric Data Warehouse** (GA, April 13) — Fabric DW now supports ALTER TABLE (add/drop columns, rename, constraints) inside explicit transactions. Previously only CREATE/DROP/TRUNCATE/CTAS/sp_rename were transactional. Key for CI/CD deployment pipelines doing controlled schema evolution. Author: Twinkle Cyril.
- Blog redirect issues prevent full page scrape — Tech Community requires auth. Confirmed one April post above via Chrome; rest of April blog content inaccessible via automated fetch.

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
