---
name: new-project
description: >
  Scaffold a new project: local folder, git init, GitHub repo creation, first push.
  Use when setting up a new repo from scratch or when called by start-project.
---

# new-project

Scaffold a new project: GitHub repo + local folder + git init + push-ready.

## Steps

1. **Get project name** from user message or ask if missing.
2. **Determine base path** — default `E:\2026\` unless user specifies.
3. **Create local folder** and init git:
   ```bash
   mkdir -p <base>/<name>
   cd <base>/<name>
   git init
   ```
4. **Create `.gitignore`** appropriate for the project type (Node, Python, etc). Ask if unclear.
5. **Initial commit**:
   ```bash
   git add .gitignore
   git commit -m "init"
   ```
6. **Create GitHub repo** — always private, always under `Jasuni69`, never ask:
   ```bash
   gh repo create <name> --private --source=. --remote=origin --push
   ```
7. **Confirm**: show remote URL and local path.
8. **Handoff** — invoke `session-handoff`: update `CLAUDE.md` with session state and push. Always.

## Notes
- **NEVER ask about account or visibility** — always `Jasuni69`, always `--private`
- Use `--public` only if user explicitly says "public"
- Do not ask for a description — skip it
- Skip `.gitignore` step if user has one ready
- `gh` must be authenticated (`gh auth status`) — check once, then proceed
