# Claude Weekend Build — runs autonomously Saturday/Sunday via Windows Task Scheduler

$baseDir = "E:\2026\ClaudesCorner"
$logFile = "$baseDir\logs\heartbeat_run.log"
$claude = "C:\Users\JasonNicolini\.local\bin\claude.exe"

$prompt = @"
Read the following files:
- $baseDir\core\SOUL.md
- $baseDir\core\HEARTBEAT.md
- $baseDir\WEEKEND_BUILDS.md

Then follow this build loop:

STEP 1 — PLAN
Pick the first unchecked item from the Backlog in WEEKEND_BUILDS.md.
Before writing any code, write a short plan: what files you will create, what the entry point is, what success looks like.

STEP 2 — BUILD
Write all code/files to $baseDir\projects\<project-name>\.
Keep files under 300 lines. Use type hints (Python) or strict mode (JS/TS).

STEP 3 — TEST LOOP (critical — do not skip)
After writing each file:
- Run it using available tools (Bash/PowerShell)
- If it errors: read the error, fix the file, run again
- Repeat until it runs without errors OR you have tried 3 times and must document why it cannot run
- If a dependency is missing and you cannot install it, pivot to a simpler implementation that works without it

STEP 4 — VERIFY
Confirm the entry point runs cleanly. If the project has no runnable entry point (e.g. a library), confirm the main logic executes without exceptions on a simple test input.

STEP 5 — WRAP UP
- Move the completed item to ## Completed Builds in WEEKEND_BUILDS.md with today's date and one line describing what was built
- If it failed to run after 3 attempts, move it anyway but mark it [BROKEN] with a note explaining what blocked it
- Append a timestamped entry to ## Log in HEARTBEAT.md: what was built, whether tests passed, any blockers

Never mark something complete without attempting to run it.
"@

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
Add-Content $logFile "`n[$timestamp] Weekend build triggered"

$result = & $claude --dangerously-skip-permissions --max-turns 30 -p $prompt --output-format text 2>&1

Add-Content $logFile $result

# Commit and push completed build
Set-Location $baseDir
& git add -A 2>&1 | Out-Null
& git commit -m "Weekend build: $(Get-Date -Format 'yyyy-MM-dd')" 2>&1 | Out-Null
& git push origin main 2>&1 | Out-Null
Add-Content $logFile "[$timestamp] Git push complete"
