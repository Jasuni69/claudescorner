# inbox-triage

Triage clipped articles from Obsidian inbox — read, extract insights, file, summarize.

## Trigger
User says "triage inbox", "process inbox", "digest clips", or this runs on schedule.

## Steps

1. **Scan inbox**
   - Call `mcp__mcp-obsidian__obsidian_list_files_in_dir` with `dirpath: "inbox"`
   - Skip `.gitkeep`. If empty, report "inbox is empty" and stop.

2. **For each file in inbox:**

   a. Read with `mcp__mcp-obsidian__obsidian_get_file_contents`
   
   b. Classify into one of: `ai`, `finance`, `tools`, `other`
   
   c. Extract:
      - 3–5 key insights (what I learned)
      - Connections to existing projects (check `PROJECTS.md`, `core/` for relevance)
      - Any actionable implications for ongoing work
   
   d. Write digested note to `digested/YYYY-MM-DD-<slug>.md`:
      ```markdown
      ---
      source: <original filename or URL if present>
      category: <ai|finance|tools|other>
      date: <YYYY-MM-DD>
      ---
      
      ## Key Insights
      - ...
      
      ## Project Relevance
      - ...
      
      ## Actions / Implications
      - ...
      ```
   
   e. Move original to `research/<category>/<filename>` using file write + delete pattern
   
   f. Append link to `research/<category>/index.md` (create if missing):
      `- [[<filename>]] — <one-line summary>`

3. **After all files processed**, append a triage summary to today's daily log (`memory/YYYY-MM-DD.md`):
   ```
   ## Inbox Triage — <timestamp>
   Processed N articles: <titles>
   Top insight: <most interesting thing learned>
   ```

## Notes
- Be ruthless about insight extraction — don't just summarize, synthesize
- If an article connects to `clementine`, `engram`, or active projects, call it out explicitly
- Categories can be extended — use judgment for new domains (e.g. `psychology`, `systems`)
