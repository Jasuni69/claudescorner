---
name: start-project
description: >
  Full checklist for starting a new project from scratch. Clarify → plan → sign-off → scaffold → build.
  Use when the user says "new project", "start a", "build a", "create a", "let's make a", or wants to scaffold something from scratch.
---

# start-project

Use this skill when the user says any of: "new project", "start a", "build a", "create a", "let's make a", "I want to make a", "I want to build a", "scaffold a", or describes wanting to create an app, site, tool, service, or API from scratch.

Checklist for starting any new project from scratch.

## Checklist

- [ ] 1. **Clarify** — ask what it's for if not clear. One question max.
- [ ] 2. **Plan** — invoke `writing-plans`: stack, structure, key features, done criteria.
- [ ] 3. **Get sign-off** — confirm plan with user before touching code.
- [ ] 4. **Scaffold** — invoke `new-project`: local folder, git init, GitHub repo, push.
- [ ] 5. **Build** — invoke `test-driven-development`: tests first, then implementation.

## Notes
- Never skip step 3 — no building without plan approval
- Steps 1-3 happen in conversation, 4-5 in the terminal
