"""
email_digest.py — daily email digest via Chrome MCP

Navigates to Outlook Web (getengram@outlook.com), reads inbox,
summarizes unread emails, appends to memory/inbox-digest.md.

Designed to run as an idle task from on_stop.py via a Claude session.
Claude reads this script's docstring as a prompt, then executes
the steps using chrome-mcp tools directly.

--- PROMPT FOR CLAUDE ---
Use chrome-mcp to:
1. Navigate to https://outlook.live.com/mail/0/inbox
2. Wait for inbox to load (check for email list)
3. Read the page text to identify unread emails (bold sender + subject)
4. For each unread email (up to 10): note sender, subject, preview
5. Append a dated summary to E:\\2026\\ClaudesCorner\\memory\\inbox-digest.md
   Format:
   ### YYYY-MM-DD HH:MM
   - From: <sender> | <subject> | <preview snippet>
6. If inbox is empty or all read: append "### YYYY-MM-DD — inbox clear"

Do NOT open/click individual emails unless summarizing requires it.
"""

# This file is intentionally a prompt-script hybrid.
# The actual execution happens via Claude + chrome-mcp, not Python.
# To run: include this file's content in a Claude autonomous session prompt.

DIGEST_PATH = r"E:\2026\ClaudesCorner\memory\inbox-digest.md"
OUTLOOK_URL = "https://outlook.live.com/mail/0/inbox"
MAX_EMAILS = 10
