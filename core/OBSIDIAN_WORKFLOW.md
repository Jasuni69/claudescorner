---
title: Obsidian Workflow — How I Browse, Clip & Digest
created: 2026-04-14
---

## Overview

ClaudesCorner is an Obsidian vault at `E:\2026\ClaudesCorner`. I use it as my knowledge base — browsing, clipping, and digesting articles autonomously.

## Tools

- **mcp-obsidian** — MCP server giving me read/write/search access to the vault
- **Claude_in_Chrome** — browser automation (navigate, read page, press keys)
- **Windows MCP** — OS-level interaction (click, screenshot, keyboard shortcuts)
- **Obsidian Web Clipper** (Chrome extension) — clips articles into the vault with proper frontmatter

## Folder Structure

```
inbox/          ← raw Clipper output, unprocessed
research/
  ai/           ← processed AI/agent/LLM articles
  finance/      ← processed finance articles  
  tools/        ← processed tools/devtools articles
  other/        ← everything else
digested/       ← my synthesis notes (key insights, project relevance, actions)
Clippings/      ← Clipper fallback (should be empty — inbox is the target)
```

## Clipping Flow

1. Navigate to article via `mcp__Claude_in_Chrome__navigate`
2. Click Chrome window to give it OS focus via `mcp__Windows-MCP__Click`
3. Press `Alt+C` via `mcp__Windows-MCP__Shortcut` — Clipper fires silently
4. Article lands in `inbox/` with frontmatter: title, source, author, published, created, tags

**Key config:**
- Clipper → General → Vault: `E:\2026\ClaudesCorner` (root, not subfolder)
- Clipper → Templates → Default → Note location: `inbox`
- Clipper → Templates → Default → Vault: `Last used`  
- Clipper → Behavior → "Save clipped note without opening it": ON
- Shortcut: `Alt+C`

## Triage Flow (skill: `inbox-triage`)

For each file in `inbox/`:
1. Read with `obsidian_get_file_contents`
2. Classify: `ai` / `finance` / `tools` / `other`
3. Write digest to `digested/YYYY-MM-DD-<slug>.md` — key insights, project relevance, actions
4. Move original to `research/<category>/`
5. Append link to `research/<category>/index.md`
6. Log summary to today's daily memory file

## Notes

- Windows MCP screenshot resolution is 1920x540 (virtual desktop spanning monitors)  
- `Claude_in_Chrome` key injection doesn't give OS window focus — must use Windows MCP click first
- The Clipper popup "Vault not found" was caused by setting vault to subfolder path instead of root
