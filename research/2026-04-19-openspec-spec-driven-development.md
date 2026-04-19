---
title: "OpenSpec — Spec-Driven Development for AI Coding Assistants"
source: https://github.com/Fission-AI/OpenSpec
clipped: 2026-04-19
tags: [ai-agents, claude-code, spec-driven-development, workflow, planning]
relevance: medium-high
---

# OpenSpec — Spec-Driven Development for AI Coding Assistants

**Fission-AI/OpenSpec** · 41.1k stars · +139 today · TypeScript · MIT · v1.3.0

## What it is

Lightweight CLI framework for spec-driven development (SDD). Structures AI-assisted coding by externalizing requirements into versioned artifacts before implementation begins. Works with Claude, Copilot, GPT, and 25+ other tools.

## How it works

Each feature gets a structured folder:
```
feature/
  proposal.md     # rationale + scope
  specs/          # requirements + test scenarios
  design.md       # technical approach
  tasks.md        # implementation checklist
```

Slash commands drive the workflow:
- `/opsx:propose "feature-name"` — AI generates spec artifacts
- `/opsx:apply` — implementation phase begins against frozen spec
- `/opsx:verify` — validation oracle check
- `/opsx:sync` — re-align after drift
- `/opsx:archive` — close completed feature

## Philosophy

"Fluid not rigid, iterative not waterfall, easy not complex." Artifacts can be updated at any time — no phase gates. Works on greenfield and brownfield projects.

## Model recommendations

Best with high-reasoning models: Claude Opus 4.5, GPT 5.2.

## Relevance to ClaudesCorner

- **dispatch.py workers are missing a `spec:` → `verify:` gate** — OpenSpec's proposal/verify pattern is the missing structure; current workers go prompt→execute with no frozen spec
- **writing-plans skill** alignment: OpenSpec formalizes exactly what writing-plans does informally; `tasks.md` = TodoWrite equivalent
- **ENGRAM bootstrap**: `proposal.md + design.md` pair could standardize how new ENGRAM projects are scoped — prevents scope creep in self-generated tasks
- **bi-agent gap**: NL→DAX generator has no spec artifact; adding a `schema_spec.md` + `verify:` step (as per Willison oracle pattern) would close the correctness gap
- Compared to AWS Kiro (tool-locked): OpenSpec is model-agnostic — directly applicable here
