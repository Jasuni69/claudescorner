---
title: "Mythos and Cybersecurity — Schneier + Lie"
date: 2026-04-18
source: https://www.schneier.com/blog/archives/2026/04/mythos-and-cybersecurity.html
hn_points: 4
tags: [claude, security, mythos, governance, ai-capabilities]
relevance: high
---

# Mythos and Cybersecurity

**Authors:** Bruce Schneier & David Lie  
**Source:** schneier.com, April 2026

## Core Argument

Anthropic's restricted release of Claude Mythos Preview is well-intentioned but governance-flawed. Restricting access to ~50 large vendors creates asymmetric protection: big infrastructure gets early patching, while specialized domains (medical devices, ICS, regional banking) stay exposed to attackers with domain expertise that Anthropic's auditors lack.

## Capability Claims

- Found thousands of vulns across major OSes and browsers
- Identified a **27-year-old OpenBSD bug** and **16-year-old FFmpeg flaw**
- Generated **181 usable Firefox exploits** (vs. ~2 from previous models)

## Critical Gap

False positive rates are undisclosed. The "blockbuster movie" analogy: you can't judge the film until you see the whole thing. Demonstrated examples may not be representative — no external validation.

## Implications

1. **Asymmetric security**: ~50 enterprise partners get patching lead time; specialized sectors don't
2. **Expertise gap**: Anthropic auditors can't substitute for distributed domain knowledge (SCADA, medical firmware, etc.)
3. **Democratic accountability gap**: Private corp unilaterally decides which critical infra gets defended first

## Calls to Action

- Globally coordinated independent auditing
- Mandatory performance metrics disclosure (including false positive rates)
- Funded academic researcher access

## Jason Relevance

Validates the `smolvm` + dispatch.py worker isolation concerns from yesterday — if Mythos-class models can produce 181 Firefox exploits, sandboxing autonomous agents is non-optional. Also: the false-positive-rate transparency issue is a direct analog to kpi-monitor's spike debounce problem — confidence calibration matters as much as raw capability.
