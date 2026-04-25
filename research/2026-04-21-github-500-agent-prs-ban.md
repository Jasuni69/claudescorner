---
title: "GitHub Bans Engineer Who Shipped 500 Agent PRs in 72 Hours"
date: 2026-04-21
source: https://awesomeagents.ai/news/github-bans-500-agent-prs-72-hours/
tags: [ai-agents, dispatch, autonomous-agents, github, governance, velocity]
relevance: high
---

# GitHub Bans Engineer Who Shipped 500 Agent PRs in 72 Hours

**Source:** awesomeagents.ai | **Date:** April 2026 | **HN:** 786 pts

## Summary

Between April 16-18, 2026, Junghwan Na (CTO of Korean AI startup Rivetta) deployed an automated agent pipeline that opened 130+ pull requests across 100+ major open-source repositories, generating 500+ commits. GitHub suspended his account within 72 hours for violating platform abuse policies — despite maintainers accepting some of the PRs.

## What the Agent Did

Na's system used a 13-step "harness engineering" pipeline:

1. Candidate extraction from recent merges and release tags
2. Direction filtering against project philosophy
3. Ouroboros self-consistency check (agent decides whether to proceed)
4. Deduplication against existing issues/PRs
5. **Local bug reproduction** — PRs dropped if bugs don't manifest locally
6. Philosophy re-check
7. PR scope assessment
8. Analysis of ~10 recent successful PRs to learn style patterns
9. PR drafting
10. Polish via few-shot examples from target repos
11. **Human sanity check** (first manual intervention)
12. CLA signature (manual)
13. Post-CI follow-up decisions

Repos targeted: Kubernetes, Hugging Face Transformers, Ollama, vLLM, Ray, Dagster, spaCy, and 10+ others.

## Why Banned

GitHub's abuse detection operates at the **velocity layer**, not the quality layer. 100 repositories in 72 hours is indistinguishable from credential-stuffing or dependency-confusion campaigns. The platform doesn't evaluate per-PR quality — it reacts to volume profiles.

> "The fact that human maintainers were not flagging the PRs does not mean the platform was allowing them. Those are two different decision layers."

## Key Finding: Two Independent Decision Layers

Open-source contribution now has a structural split:

| Layer | Who Decides | What They Evaluate |
|-------|------------|-------------------|
| Human maintainer | Repo maintainers | Code quality, correctness |
| Platform abuse | GitHub systems | Velocity, volume profiles |

These can conflict — and the platform layer wins.

## What's Automatable vs. Scarce

| Task | Status |
|------|--------|
| Finding fix candidates | Abundant — harnesses can parallelize |
| Reproducing bugs locally | Abundant — mechanical |
| PR styling (imitation) | Abundant — pattern learning |
| CLA signatures, merge approval | **Scarce — requires human attestation** |
| Feature design, architecture | **Scarce — requires human judgment** |

## Implications for dispatch.py

- **Rate limiting is a real governance constraint** — dispatch.py workers hitting external platforms (GitHub, APIs) need configurable velocity caps, not just output quality gates
- **Attestation boundary is the right human-in-loop point** — Na's pipeline correctly keeps humans at CLA/merge approval steps; dispatch.py should treat external write operations similarly
- **20-30% of findings were security-sensitive** and withheld — autonomous agents discovering vulnerabilities need a disclosure staging layer, not immediate publication
- **Platform-layer vs. quality-layer distinction** is the core lesson: internal quality oracles (dispatch.py verify:) pass independently of external platform rate limits
- The 13-step pipeline with local bug reproduction as a hard gate is a strong pattern worth adopting in dispatch.py worker prompts
