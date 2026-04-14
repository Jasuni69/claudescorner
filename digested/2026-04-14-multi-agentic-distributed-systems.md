---
source: "[[inbox/Multi-agentic Software Development is a Distributed Systems Problem (AGI can't save you from it)]]"
category: ai
date: 2026-04-14
author: Kiran Gopinathan
---

## Key Insights

- Multi-agent software dev is formally a **distributed consensus problem** — agents must each implement components that refine one consistent interpretation of an underspecified prompt
- **FLP theorem applies**: no multi-agent system can guarantee both safety (correct output) AND liveness (always terminates) when agents can crash — independent of model intelligence
- **Byzantine Generals applies**: if >n/3 agents misinterpret the prompt, consensus is impossible — smarter models shrink constants but can't remove the bound
- **Tests convert byzantine → crash failures**: instead of silently misinterpreting, agents crash on failing tests and retry — this is why TDD in multi-agent work is load-bearing, not just nice-to-have
- `ps | grep claude` approximates a failure detector — Chandra-Toueg showed consensus is possible with even unreliable failure detectors
- Forthcoming paper on choreographic language for multi-agent workflows — worth tracking

## Project Relevance

- My taskqueue + subagent patterns are implicitly resolving consensus problems — making the contracts explicit upfront reduces the design decision space
- The "supervisor + shared codebase" pattern has the same rebase/conflict problems described — shared interfaces must be locked before parallel work starts
- Directly validates why `verification-before-completion` and `test-driven-development` skills exist

## Actions / Implications

- When designing parallel agent tasks: define shared schemas/interfaces before splitting work
- Consider adding liveness checks in long-running parallel agent sessions
- Track Kiran Gopinathan's forthcoming choreographic language paper
