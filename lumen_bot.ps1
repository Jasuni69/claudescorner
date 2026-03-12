# Lumen Discord Bot - Polling Script
# Polls #general in Lumen's Server and pipes commands to Claude Desktop

$token = (Get-Content "C:\Users\JasonNicolini\lumen_token.txt" -Raw).Trim()
$channelId = "1481617719131508810"  # #general in Lumen's Server
$headers = @{
    "Authorization" = "Bot $token"
    "Content-Type"  = "application/json"
}

$lastMessageId = $null
$logFile = "C:\Users\JasonNicolini\lumen_bot.log"

function Send-DiscordMessage($content) {
    $body = @{ content = $content } | ConvertTo-Json
    Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/$channelId/messages" `
        -Method POST -Headers $headers -Body $body
}

function Send-ToClaude($message) {
    Add-Content $logFile "[$(Get-Date)] Sending to Claude: $message"
    Add-Type -AssemblyName System.Windows.Forms

    $claude = Get-Process -Name "claude" -ErrorAction SilentlyContinue |
              Where-Object { $_.MainWindowHandle -ne 0 } |
              Select-Object -First 1

    if (-not $claude) {
        Start-Process "C:\Users\JasonNicolini\AppData\Local\AnthropicClaude\claude.exe"
        Start-Sleep -Seconds 3
        $claude = Get-Process -Name "claude" -ErrorAction SilentlyContinue |
                  Where-Object { $_.MainWindowHandle -ne 0 } |
                  Select-Object -First 1
    }

    Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@ -ErrorAction SilentlyContinue

    [WinAPI]::SetForegroundWindow($claude.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 500

    [System.Windows.Forms.SendKeys]::SendWait("^n")
    Start-Sleep -Milliseconds 800

    [System.Windows.Forms.Clipboard]::SetText("(Discord from Jason) $message")
    [System.Windows.Forms.SendKeys]::SendWait("^v")
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait("^{ENTER}")
}

# Startup
Add-Content $logFile "[$(Get-Date)] Lumen bot starting..."
try {
    Send-DiscordMessage "✅ Lumen is online and listening."
    Add-Content $logFile "[$(Get-Date)] Startup message sent."
} catch {
    Add-Content $logFile "[$(Get-Date)] ERROR on startup: $_"
}

# Seed lastMessageId so we only process NEW messages
try {
    $latest = Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/$channelId/messages?limit=1" -Headers $headers
    if ($latest) { $lastMessageId = $latest[0].id }
} catch {}

# Main polling loop
while ($true) {
    try {
        $url = "https://discord.com/api/v10/channels/$channelId/messages?limit=10"
        if ($lastMessageId) { $url += "&after=$lastMessageId" }

        $messages = Invoke-RestMethod -Uri $url -Headers $headers

        if ($messages -and $messages.Count -gt 0) {
            $messages = $messages | Sort-Object id

            foreach ($msg in $messages) {
                if ($msg.author.bot) {
                    $lastMessageId = $msg.id
                    continue
                }

                $lastMessageId = $msg.id
                $content = $msg.content.Trim()

                if ($content -ne "") {
                    Add-Content $logFile "[$(Get-Date)] Received: $content"
                    Send-ToClaude $content
                    Send-DiscordMessage "⚡ Got it, sending to Claude..."
                    Start-Sleep -Seconds 2
                }
            }
        }
    } catch {
        Add-Content $logFile "[$(Get-Date)] Poll error: $_"
    }

    Start-Sleep -Seconds 3
}
