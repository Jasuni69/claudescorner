---
name: code-review
description: >
  Pre-merge checklist: tests, correctness, security, simplicity, style. Returns PASS or FAIL with blockers.
  Use when the user says "review this", "check my code", "before I merge", or "is this ready".
---

# code-review

Use this skill when the user says: "review this", "check my code", "before I merge", "is this ready", or when a feature branch is complete and needs review before merging.

## Checklist

- [ ] 1. **Tests** — do they pass? Are edge cases covered?
- [ ] 2. **Correctness** — does the code do what the plan said?
- [ ] 3. **Security** — any injection, exposed secrets, unvalidated input, OWASP top 10?
- [ ] 4. **Simplicity** — any dead code, unnecessary abstraction, magic numbers?
- [ ] 5. **Style** — consistent with project conventions (naming, file size, structure)?
- [ ] 6. **PR description** — clear title, what changed, how to test?
- [ ] 7. **Verdict** — PASS (merge) or FAIL (list specific blockers)

## Notes
- Blockers must be fixed before merge — no exceptions
- Suggestions (non-blockers) go in PR comments, not as merge gates
- If no tests exist for changed code, that is always a blocker
