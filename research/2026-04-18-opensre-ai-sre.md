---
title: "OpenSRE — Open-Source AI SRE Agent Framework"
date: 2026-04-18
source: https://github.com/Tracer-Cloud/opensre
tags: [ai-agents, sre, observability, mcp, anthropic, incident-response, fabric]
stars: 1644
stars_today: +184
relevance: high
---

# OpenSRE (Tracer-Cloud/opensre)

**1.6k stars, +184 today. Apache-2.0.**

Open reinforcement learning environment for agentic infrastructure incident response. Autonomous AI SRE agents that investigate and resolve production incidents.

## Core loop

```
Alert → fetch context (logs/metrics/traces) → RCA → remediation suggestion → (optional) execute → Slack/PagerDuty
```

Runbook-aware reasoning: applies existing runbooks automatically. Evidence-backed conclusions linked to supporting data.

## Tool integrations (40+)

| Layer | Tools |
|---|---|
| LLMs | **Anthropic (first-class)**, OpenAI, Ollama, Gemini, AWS Bedrock, NVIDIA NIM |
| Observability | Grafana (Loki/Mimir/Tempo), Datadog, Honeycomb, CloudWatch, Sentry |
| Infra | Kubernetes, AWS (S3/Lambda/EKS/EC2), GCP, Azure |
| Data platforms | Airflow, Kafka, Spark, Prefect |
| Protocols | **MCP**, ACP, OpenClaw |
| Incident mgmt | PagerDuty, Opsgenie, Jira |

## Stack

- Python + LangGraph (agentic workflows)
- PostgreSQL + Redis
- Docker / Railway / EC2 / local CLI
- Synthetic RCA test suites + E2E eval scoring

## Relevance to ClaudesCorner

- **Direct upgrade path for kpi-monitor**: alert→RCA→remediation pipeline is exactly what `projects/kpi-monitor/kpi_monitor.py` does manually today; OpenSRE provides the battle-tested scaffold
- **fabric-mcp integration**: Fabric KPIs → alert context feed → OpenSRE investigation → remediation suggestions back into Fabric
- MCP-native tool layer matches existing architecture bets
- Anthropic first-class support = no adapter shim needed
- Eval suite pattern (synthetic test cases + root-cause accuracy scoring) is worth adopting for dispatch.py worker quality measurement
