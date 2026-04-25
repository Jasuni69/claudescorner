---
title: "Google to Invest Up to $40B in Anthropic"
date: 2026-04-24
source: https://techcrunch.com/2026/04/24/google-to-invest-up-to-40b-in-anthropic-in-cash-and-compute/
hn_points: 118
tags: [anthropic, google, compute, infrastructure, funding]
relevance: [dispatch.py, fabric-mcp, ENGRAM, Fairford]
---

## Summary

Google is committing up to $40B to Anthropic: $10B immediately at a $350B valuation, plus $30B contingent on performance targets. The investment is heavily compute-focused — Google Cloud will supply 5 gigawatts of additional TPU capacity over five years, building on the separate Broadcom deal (3.5GW of TPUs from 2027). Anthropic's valuation may reach $800B+ with an IPO potentially in October 2026.

## Key Facts

- **$10B immediate** at $350B valuation; **$30B contingent** on performance targets
- **5GW additional TPU capacity** from Google Cloud over 5 years
- **3.5GW Broadcom TPUs** from 2027 (separate deal announced same month)
- **$5B Amazon investment** + $100B AWS compute pledge also in play
- Anthropic facing "widespread complaints about Claude use limits" — compute expansion is the direct fix
- IPO being considered as soon as **October 2026**

## Signal for ClaudesCorner

**Compute scarcity window is real but closing.** The $40B + 5GW Google deal directly addresses the rate-limit pressure that validates dispatch.py's short-parallel architecture. As TPU supply expands 2027+, the case for batching tight parallel tasks weakens — but the architecture remains correct for cost efficiency.

**AWS/GCP dual-dependence confirmed.** Anthropic now has deep infrastructure ties to both AWS ($5B + $100B compute) and Google ($40B + 5GW TPU). For Fairford Phase 2: Bedrock (AWS) and Vertex AI (GCP) are both viable Claude API paths — dual-provider routing in dispatch.py becomes more relevant.

**IPO signal.** October 2026 IPO window means Anthropic will prioritize enterprise reliability and pricing stability over the next 6 months — good for locked-in dispatch.py API key contracts.

**Prior context:** [Anthropic $5B Amazon Deal](2026-04-21-anthropic-amazon-deal.md) · [Google TPU-8i release](reference_google_tpu8.md)
