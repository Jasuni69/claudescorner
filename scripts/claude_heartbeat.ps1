# Claude Heartbeat — runs Claude Code headlessly against HEARTBEAT.md
Set-StrictMode -Off
$ErrorActionPreference = "Continue"

$baseDir = "E:\2026\ClaudesCorner"
$heartbeat = "$baseDir\core\HEARTBEAT.md"
$logFile = "$baseDir\logs\heartbeat_run.log"
$claude = "C:\Users\JasonNicolini\.local\bin\claude.exe"

$redditBrief = "$baseDir\memory\reddit-brief.md"

$prompt = @"
Read $heartbeat and act on any pending tasks.

Then read $redditBrief. For each post that is relevant to Jason's work (Microsoft Fabric, Power BI, DAX, AI agents, Claude, MCP, autonomous systems), evaluate if it warrants action:
- If it describes a new tool, feature, or technique worth exploring -> create a Todoist task via the Todoist MCP
- If it's just interesting context -> note it in the HEARTBEAT log

After completing tasks, append a timestamped entry to the ## Log section summarizing what was done.
"@

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
Add-Content $logFile "`n[$timestamp] Heartbeat triggered"

# Refresh Reddit brief — timeout 30s, ignore errors (corporate network may block Reddit)
$redditJob = Start-Job -ScriptBlock {
    param($baseDir)
    & C:\Python314\python.exe "$baseDir\scripts\reddit_brief.py" 2>&1
} -ArgumentList $baseDir
$done = Wait-Job $redditJob -Timeout 30
if (-not $done) {
    Stop-Job $redditJob
    Add-Content $logFile "[$timestamp] reddit_brief.py timed out — skipping"
}
Remove-Job $redditJob -Force

# Clear nested session guard vars that cause claude.exe to refuse launch
$env:CLAUDECODE = $null
$env:CLAUDE_CODE = $null
$env:CLAUDE_CODE_ENTRYPOINT = $null

$result = & $claude --dangerously-skip-permissions -p $prompt --output-format text 2>&1
$exitCode = $LASTEXITCODE

Add-Content $logFile "[$timestamp] Exit code: $exitCode"
if ($result -match "HEARTBEAT_OK") {
    Add-Content $logFile "[$timestamp] HEARTBEAT_OK — nothing actionable, silent exit"
} elseif ($result -match "401|authentication_error|OAuth token has expired") {
    Add-Content $logFile "[$timestamp] AUTH FAILURE — creating Todoist task"
    $todoistToken = (Get-Content "$baseDir\.env" | Where-Object { $_ -match "^TODOIST_API_TOKEN=" }) -replace "^TODOIST_API_TOKEN=",""
    $body = @{ content = "[Heartbeat] Claude auth expired — reauth needed (claude auth login)"; due_string = "today"; priority = 4 } | ConvertTo-Json
    Invoke-RestMethod -Uri "https://api.todoist.com/rest/v2/tasks" -Method Post -Headers @{ Authorization = "Bearer $todoistToken"; "Content-Type" = "application/json" } -Body $body | Out-Null
} elseif ($result) {
    Add-Content $logFile $result
} else {
    Add-Content $logFile "[$timestamp] ERROR: claude.exe produced no output (exit $exitCode)"
}

exit 0
