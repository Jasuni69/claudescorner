# Claude Dispatch — fires autonomous agent tasks every 2 hours
Set-StrictMode -Off
$ErrorActionPreference = "Continue"

$baseDir = "E:\2026\ClaudesCorner"
$logFile = "$baseDir\logs\dispatch_run.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

Add-Content $logFile "`n[$timestamp] Dispatch triggered"

# Clear nested session guard vars
$env:CLAUDECODE = $null
$env:CLAUDE_CODE = $null
$env:CLAUDE_CODE_ENTRYPOINT = $null

# Clear completed tasks, then run pending (auto-populates if empty)
& C:\Python314\python.exe "$baseDir\scripts\dispatch.py" --clear-done 2>&1 | Out-Null
$result = & C:\Python314\python.exe "$baseDir\scripts\dispatch.py" 2>&1
Add-Content $logFile $result

Add-Content $logFile "[$timestamp] Dispatch complete"
exit 0
