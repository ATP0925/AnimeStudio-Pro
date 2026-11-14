@echo off
setlocal EnableDelayedExpansion
title Anime Studio Pro - Setup & Shortcut Creator
cd /d "%~dp0"

echo ======================================================================
echo          🌸 ANIME STUDIO PRO — 1-CLICK SYSTEM INSTALLER 🌸           
echo                    Author: Pratik Atpadkar                           
echo ======================================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python is NOT installed on this machine!
    echo Please install Python 3.10+ and check 'Add Python to PATH'.
    pause
    exit /b 1
)

echo [1/3] Installing/Verifying Python dependencies...
python -m pip install --upgrade pip pillow psutil pystray --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [!] Warning: pip install encountered an issue, proceeding anyway...
)

:: 2. Create Desktop Shortcuts
echo [2/3] Setting up Desktop shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$desk = [System.Environment]::GetFolderPath('Desktop'); " ^
    "if (Test-Path \"$env:USERPROFILE\OneDrive\Desktop\") { $desk = \"$env:USERPROFILE\OneDrive\Desktop\" }; " ^
    "$sc = $ws.CreateShortcut(\"$desk\🌸 Anime Studio.lnk\"); " ^
    "$pyw = (Get-Command pythonw -ErrorAction SilentlyContinue).Source; " ^
    "if (-not $pyw) { $pyw = (Get-Command python).Source }; " ^
    "$sc.TargetPath = $pyw; " ^
    "$sc.Arguments = '\"%~dp0AnimeStudio.pyw\"'; " ^
    "$sc.WorkingDirectory = '%~dp0'; " ^
    "$sc.IconLocation = '%~dp0anime_icon.ico,0'; " ^
    "$sc.Description = 'Anime Studio Pro - 4K Wallpapers & Japanese Audio'; " ^
    "$sc.Save(); " ^
    "$stopBat = \"@echo off`r`ntitle Emergency Stop Anime Mode`r`npython `\"%~dp0scripts\stop_anime.py`\"`r`nexit /b 0\"; " ^
    "Set-Content -Path \"$desk\🛑 STOP Anime Mode.bat\" -Value $stopBat -Encoding ASCII; " ^
    "Write-Host '[✓] Desktop shortcuts successfully created!' -ForegroundColor Green"

echo [3/3] Configuration complete!
echo.
echo ======================================================================
echo    🎉 Setup Complete! You can now launch '🌸 Anime Studio' from Desktop.
echo ======================================================================
echo.

set /p launch="Do you want to launch Anime Studio Pro now? (Y/N): "
if /i "!launch!"=="Y" (
    start "" pythonw "%~dp0AnimeStudio.pyw"
)
exit /b 0
