# PowerShell script to create a startup shortcut for TalkStream tray application

# Get the absolute paths
$scriptPath = $PSScriptRoot
$trayAppPath = Join-Path -Path $scriptPath -ChildPath "tray_app.py"
$pythonExe = Join-Path -Path $scriptPath -ChildPath ".venv\Scripts\pythonw.exe"

# Create a shortcut in the Windows startup folder
$startupFolder = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path -Path $startupFolder -ChildPath "TalkStream.lnk"

# Create a WScript.Shell object to create the shortcut
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)

# Configure the shortcut
$shortcut.TargetPath = $pythonExe
$shortcut.Arguments = "`"$trayAppPath`""
$shortcut.WorkingDirectory = $scriptPath
$shortcut.Description = "TalkStream Tray Application"
$shortcut.IconLocation = "$env:SystemRoot\System32\SHELL32.dll,175" # Default icon from system
$shortcut.WindowStyle = 7 # Minimized window

# Save the shortcut
$shortcut.Save()

# Verify the shortcut was created
if (Test-Path $shortcutPath) {
    Write-Host "Startup shortcut created successfully at: $shortcutPath" -ForegroundColor Green
    Write-Host "TalkStream will now start automatically when you log in to Windows." -ForegroundColor Green
} else {
    Write-Host "Failed to create startup shortcut." -ForegroundColor Red
}
