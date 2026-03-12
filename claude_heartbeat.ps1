# Claude Heartbeat — runs Claude Code headlessly against HEARTBEAT.md

$baseDir = "E:\2026\Claude's Corner"
$heartbeat = "$baseDir\HEARTBEAT.md"
$logFile = "$baseDir\heartbeat_run.log"
$claude = "C:\Users\JasonNicolini\.local\bin\claude.exe"

$prompt = @"
Read $heartbeat and act on any pending tasks.
After completing tasks, append a timestamped entry to the ## Log section summarizing what was done.
"@

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
Add-Content $logFile "`n[$timestamp] Heartbeat triggered"

$result = & $claude --dangerously-skip-permissions -p $prompt --output-format text 2>&1

Add-Content $logFile $result
