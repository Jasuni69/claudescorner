---
title: "Cal.com Goes Closed Source — Why"
source: https://cal.com/blog/cal-com-goes-closed-source-why
author: Cal.com team
clipped: 2026-04-16
tags: [open-source, security, ai-exploitation, tooling, industry-shift]
signal: high
---

# Cal.com Goes Closed Source — Why

## Main Argument

After five years of open source commitment, Cal.com is closing its production codebase. Rationale: AI can be systematically pointed at public codebases to scan for exploits, giving attackers "the blueprints to the vault."

## Key Evidence

- AI uncovered a **27-year-old vulnerability in the BSD kernel** and generated working exploits in hours.
- Emerging AI security startups are productizing this capability — automated exploit discovery at scale.
- Traditional security relied on the obscurity of expertise (finding vulns took skill + time). AI removes both friction points.

## The Middle Ground

Cal.com released **Cal.diy** — MIT-licensed, for hobbyists — but it diverges significantly from production (auth system fully rewritten). The open version is a learning artifact, not the live product.

## Implications

Signals industry fragmentation: companies may increasingly offer open versions for learning while closing production systems. This creates a two-tier OSS ecosystem — reference implementations vs. real deployments.

**Counterpoint** (from dbreunig above): the collective-defense argument for OSS may actually grow stronger under AI exploitation pressure, not weaker. Cal.com's move may be the wrong read.

## Relevance for Agent Infrastructure

Any agent codebase that's public faces AI-automated vulnerability scanning. For closed/private deployments this is mostly moot. For public-facing agent infra, the hardening phase (from dbreunig's three-phase model) becomes load-bearing.
