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
