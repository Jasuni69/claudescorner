---
name: workflows
description: >
  Master workflow router. Use this for ANY development task: starting a project,
  adding a feature, reviewing code, deploying, debugging, or writing plans.
  Triggers: "let's build", "new project", "add a feature", "review this",
  "deploy", "set up CI", "implement", "let's continue", "is this ready",
  "before I merge", "write a plan", "tests first", "debug this".
---

# workflows

**Always invoke this skill before starting any development task.**

## Router

| What you said | Invoke |
|---|---|
| "let's build", "new project", "create a", "I want to make" | `/start-project` |
| "let's continue", "add a feature", "implement X", "next feature" | `/feature` |
| "review this", "is this ready", "before I merge", "check my code" | `/code-review` |
| "deploy", "set up CI", "push to prod", "GitHub Actions" | `/deploy` |
| "write a plan", "plan this out", "scope this" | `/writing-plans` |
| "tests first", "TDD", "write tests" | `/test-driven-development` |
| "scaffold", "git init", "create repo" | `/new-project` |

## Rules

- NEVER start coding without invoking the correct sub-skill first
- NEVER skip `/writing-plans` before touching code
- NEVER work directly on `main` — always branch via `/feature`
- NEVER ask about GitHub account or repo visibility — always `Jasuni69`, always private
- If scope is unclear, clarify BEFORE invoking any sub-skill

## Full cycle

```
start-project
    └── writing-plans       ← what are we building?
    └── new-project         ← scaffold repo, GitHub, git init
    └── test-driven-development ← tests first, then code

feature                     ← repeat per feature
    └── writing-plans
    └── test-driven-development
    └── code-review

deploy                      ← once per project
```
