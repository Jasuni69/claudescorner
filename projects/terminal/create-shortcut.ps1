$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Claude Terminal.lnk")
$Shortcut.TargetPath = "E:\2026\ClaudesCorner\projects\terminal\start.bat"
$Shortcut.WorkingDirectory = "E:\2026\ClaudesCorner\projects\terminal"
$Shortcut.WindowStyle = 7  # minimized (hides the cmd window)
$Shortcut.Description = "Claude Terminal"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop"
