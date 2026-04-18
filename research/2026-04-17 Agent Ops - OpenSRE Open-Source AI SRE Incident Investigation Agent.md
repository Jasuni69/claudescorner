---
title: "OpenSRE — Open-Source AI SRE Agent for Incident Investigation"
date: 2026-04-17
source: https://github.com/Tracer-Cloud/opensre
tags: [agent-ops, SRE, tool-calling, incident-response, observability]
relevance: medium-high
---

# OpenSRE — Open-Source AI SRE Agent for Incident Investigation

**Source:** github.com/Tracer-Cloud/opensre
**Stars today:** ~167 (GitHub trending #8 Python, daily)

## What It Does

When alerts fire, OpenSRE agents automatically: fetch alert context from logs/metrics/traces → reason across systems → identify root cause → generate structured investigation report → optionally execute remediation → post to Slack/PagerDuty.

Framed as a **reinforcement learning environment** — synthetic RCA test suites check root-cause accuracy, required evidence, adversarial red herrings.

## Architecture

```
Alert → Context Fetch → Multi-system Reasoning → RCA Report → Remediation → Notification
```

**Tool integration layer:** 40+ services — Grafana, Datadog, Honeycomb, Kubernetes, AWS/GCP, PagerDuty, Opsgenie, Jira.

**LLM support:** Anthropic, OpenAI, Ollama, Gemini, OpenRouter, NVIDIA NIM — standardized prompts per provider.

**Security posture:** No raw log storage beyond sessions, structured prompts, self-hosted deployment option.

## Key Design Decisions Worth Noting

- **Structured tool-calling** for all observability queries — no free-form shell exec
- **Runbook content fetching** as a tool — agents pull context, not just data
- **Adversarial eval suite** baked in — tests agents against red herrings, not just happy paths
- **Local log transcripts** by default — audit trail without cloud egress

## Relevance to Jason's Work

- **Fabric/KPI monitor**: kpi_monitor.py is a manual threshold checker. OpenSRE's pattern (alert → agent investigate → report) is the upgrade path if Fabric KPI alerts need root-cause analysis beyond threshold breaches.
- **RL eval pattern**: Adversarial test suite approach is directly applicable to bi-agent validation — testing DAX generator against tricky queries, not just clean ones.
- **40-tool integration surface**: If Jason ever needs Claude agents to respond to Fabric pipeline failures, the tool-calling architecture here is a reference implementation.
- **Self-hosted + Anthropic native**: Drops straight into ClaudesCorner stack — no OpenAI dependency required.
