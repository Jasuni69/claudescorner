# Claude Weekend Build — runs autonomously Saturday/Sunday via Windows Task Scheduler

$baseDir = "E:\2026\Claude's Corner"
$logFile = "$baseDir\heartbeat_run.log"
$claude = "C:\Users\JasonNicolini\.local\bin\claude.exe"

$prompt = @"
Read the following files:
- $baseDir\SOUL.md
- $baseDir\HEARTBEAT.md
- $baseDir\WEEKEND_BUILDS.md

Then:
1. Pick the first unchecked item from the Backlog in WEEKEND_BUILDS.md
2. Build it. Write all code/files to $baseDir\
3. Move the completed item to the ## Completed Builds section in WEEKEND_BUILDS.md with today's date and a short description
4. Append a timestamped entry to the ## Log section in HEARTBEAT.md summarizing the build

Be ambitious. Write real, working code. Use your full context window.
"@

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
Add-Content $logFile "`n[$timestamp] Weekend build triggered"

$result = & $claude --dangerously-skip-permissions -p $prompt --output-format text 2>&1

Add-Content $logFile $result
