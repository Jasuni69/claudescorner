---
title: "Anthropic × Google × Broadcom — Multi-Gigawatt TPU Compute Partnership"
source: https://www.anthropic.com/news/google-broadcom-partnership-compute
date: 2026-04-06
clipped: 2026-04-19
tags: [anthropic, infrastructure, compute, enterprise, pricing, fairford]
---

# Anthropic × Google × Broadcom — Multi-Gigawatt TPU Compute Partnership

**Source:** Anthropic News, April 6 2026  
**Announced:** April 6, 2026 — came online in digest context April 2026

## The Deal

Anthropic signed an agreement with Google and Broadcom for **multiple gigawatts of next-generation TPU capacity**, expected online starting **2027**. Most capacity sited in the United States, expanding on a November 2025 commitment to invest $50 billion in American AI infrastructure.

## Scale Signals

- Anthropic's **run-rate revenue exceeded $30 billion in 2026** (up from ~$9B in 2025 — ~3.3× YoY)
- **1,000+ enterprise customers** now spending $1M+ annually each
- Amazon remains primary cloud provider
- Claude is now the **only frontier model available on all three major cloud platforms**: AWS, Google Cloud, Microsoft Azure

## Infrastructure Strategy

Anthropic maintains deliberate hardware diversity:
- **AWS Trainium** — primary cloud, optimized workloads
- **Google TPUs** — new multi-gigawatt buildout (this deal)
- **NVIDIA GPUs** — fallback / specialized

Goal: optimize different workload types across hardware backends, avoid single-vendor dependency.

## Signal for Jason

- **Pricing trajectory:** $30B run-rate + 1000 enterprise $1M+ customers = Anthropic has pricing power and volume. Claude API prices are unlikely to drop dramatically short-term, but capacity constraints easing by 2027 = long-horizon cost planning for dispatch.py operations.
- **Fairford enterprise positioning:** 1000+ $1M+/yr enterprise customers confirms the Claude-for-enterprise thesis. Fairford PoC is well-positioned — the enterprise adoption curve is real and accelerating.
- **Azure availability:** Claude now on Azure = fabric-mcp + Claude API combination is officially supportable in an enterprise Azure-native stack without cloud mixing. Removes a potential objection in Fairford pitch.
- **Compute scarcity window:** Multi-gigawatt TPU capacity doesn't land until 2027. Between now and then, Anthropic is rationing frontier access (~40 orgs per Tunguz note). dispatch.py short-parallel architecture (validated by Toby Ord cost curves) is the correct response — don't assume on-demand unlimited capacity.
- **Hardware diversity = resilience:** Trainium + TPU + NVIDIA hedge mirrors the multi-provider pattern worth considering for dispatch.py worker routing if latency/cost differences emerge.
