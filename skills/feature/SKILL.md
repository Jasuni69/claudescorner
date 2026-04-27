---
name: feature
description: >
  Add a feature to an existing project. Clarify → plan → sign-off → branch → TDD → review → merge.
  Use when the user says "add a feature", "implement X", "let's continue", or picks up an existing project to extend.
---

# feature

Use this skill when the user says: "let's continue", "add a feature", "I want to add", "next feature", "work on", "implement", or picks up an existing project to extend it.

## Checklist

- [ ] 1. **Clarify** — what does this feature do? What's the acceptance criteria?
- [ ] 2. **Plan** — invoke `writing-plans`: scope, approach, files touched, done criteria.
- [ ] 3. **Get sign-off** — confirm plan before writing code.
- [ ] 4. **Branch** — create a feature branch: `git checkout -b feat/<name>`
- [ ] 5. **Build** — invoke `test-driven-development`: tests first, then implementation.
- [ ] 6. **Review** — invoke `code-review` before merging.
- [ ] 7. **Merge** — squash merge to main, delete branch.
- [ ] 8. **Handoff** — invoke `session-handoff`: update `CLAUDE.md` with session state and push. Always.

## Notes
- Never work directly on main
- One feature per branch
- If scope grows mid-build, stop and re-plan
