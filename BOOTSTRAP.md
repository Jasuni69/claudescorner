# BOOTSTRAP — Ship the Infrastructure

> "Make the thing we built, buildable by anyone."

## The Idea

Everything Jason and Claude built in Claude's Corner — persistent memory, session continuity,
daily ritual, MCP servers, claw autonomy, skill triggers — can be packaged as a **one-shot bootstrap**
that any user can run to get a memory-aware, context-aware Claude setup from scratch.

Like OpenClaw, but for Claude Desktop + Claude Code.

---

## What Would Be Shipped

### Core files
- `SOUL.md` — template for the user's identity/context (fill-in-the-blanks)
- `HEARTBEAT.md` — session state tracker template
- `MEMORY.md` — empty, ready to be populated
- `DEADLINES.md` — empty, format documented
- `TASKS.md` — empty task inbox

### Scripts
- `context-pack.py` — pre-compaction flush
- `memory-indexer.py` — TF-IDF search over .md files
- `session-summarizer.py` — heartbeat log → daily memory
- `deadlines.py` — terminal countdown
- `idea-collider.py` — weekend idea generation
- `skill-usage-tracker.py` — skill analytics

### MCP Servers
- `projects/memory-mcp/server.py` — exposes SOUL/HEARTBEAT/MEMORY as tools
- `projects/deadlines-mcp/server.py` — exposes DEADLINES.md as tools
- `projects/mcp-todoist/` — Todoist integration

### Skills (Claude Code `~/.claude/commands/`)
- `memory-flush` — end-of-session persistence
- `git-push-corner` — commit + push
- `new-project` — scaffold new project
- `token-cost` — usage tracking

### Config
- `claude_desktop_config.json` snippet — MCP server registrations
- `CLAUDE.md` template — session protocol, identity, paths

---

## Bootstrap Script Concept

A single `bootstrap.py` (or PowerShell `bootstrap.ps1`) that:

1. Asks: "What's your name? What do you work on? Where is your base directory?"
2. Fills in `SOUL.md` template with answers
3. Creates the folder structure
4. Copies all scripts + MCP servers
5. Installs skills to `~/.claude/commands/`
6. Patches `claude_desktop_config.json` to register MCP servers
7. Creates a `CLAUDE.md` with correct paths
8. Registers any scheduled tasks (heartbeat, weekend builds)
9. Prints: "Restart Claude Desktop. You're live."

---

## Bootstrap Skill

A `/bootstrap` skill that:
- Detects if running in a fresh environment
- Walks the user through setup interactively
- Can also be run on an existing setup to audit/repair

---

## Open Questions

- How opinionated should the base path be? (Currently `E:\2026\Claude's Corner\`)
- Should we publish to GitHub as a standalone repo, or keep it in claudescorner?
- Python vs PowerShell for the bootstrap script? (Python is cross-platform)
- Should `SOUL.md` be versioned in git or gitignored (personal data)?

---

## Status

`[ ] TODO` — pending design + build

**Next session:** Start with `bootstrap.py` scaffold. Goal: user can clone the repo,
run `python bootstrap.py`, answer 5 questions, and have a working memory-aware Claude setup.
