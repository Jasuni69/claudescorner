---
name: deploy
description: >
  CI/CD setup: GitHub Actions, environment strategy, secrets, staging vs prod.
  Use when the user says "deploy", "set up CI", "set up GitHub Actions", or "push to production".
---

# deploy

Use this skill when the user says: "deploy", "set up CI", "set up GitHub Actions", "configure environments", "push to production", "set up staging", "add secrets", or asks about deployment for a project.

## Checklist

- [ ] 1. **Confirm target** — where is this deploying? (Vercel, Railway, Azure, VPS, etc.)
- [ ] 2. **Environment strategy** — dev / staging / prod. Confirm branch mapping.
- [ ] 3. **Secrets audit** — list required env vars. Never commit secrets. Use `.env.example`.
- [ ] 4. **CI stub** — create `.github/workflows/ci.yml`: install, lint, test on push/PR.
- [ ] 5. **Deploy workflow** — create `.github/workflows/deploy.yml`: trigger on merge to main.
- [ ] 6. **Verify** — confirm workflow runs green on a test push.
- [ ] 7. **Handoff** — invoke `session-handoff`: update `CLAUDE.md` with session state and push. Always.

## Notes
- Always add `.env` to `.gitignore` before first commit
- Staging deploys on PR merge to `dev`, prod on merge to `main`
- Ask about secrets manager if project is sensitive (Azure Key Vault, GitHub Secrets, etc.)
