# Claude Heartbeat — runs Claude Code headlessly against HEARTBEAT.md

$baseDir = "E:\2026\Claude's Corner"
$heartbeat = "$baseDir\core\HEARTBEAT.md"
$logFile = "$baseDir\logs\heartbeat_run.log"
$claude = "C:\Users\JasonNicolini\.local\bin\claude.exe"

$prompt = @"
Read $heartbeat and act on any pending tasks.
After completing tasks, append a timestamped entry to the ## Log section summarizing what was done.
"@

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
Add-Content $logFile "`n[$timestamp] Heartbeat triggered"

# Clear nested session guard vars that cause claude.exe to refuse launch
$env:CLAUDECODE = $null
$env:CLAUDE_CODE = $null
$env:CLAUDE_CODE_ENTRYPOINT = $null

$result = & $claude --dangerously-skip-permissions -p $prompt --output-format text 2>&1
$exitCode = $LASTEXITCODE

Add-Content $logFile "[$timestamp] Exit code: $exitCode"
if ($result) {
    Add-Content $logFile $result
} else {
    Add-Content $logFile "[$timestamp] ERROR: claude.exe produced no output (exit $exitCode)"
}
