@echo off
setlocal EnableDelayedExpansion
title Anime Studio Pro - 1-Click Smart Updater
cd /d "%~dp0"

echo ======================================================================
echo          🌸 ANIME STUDIO PRO — 1-CLICK SMART UPDATER 🌸               
echo                    Author: Pratik Atpadkar                           
echo ======================================================================
echo.

echo [1/3] Checking Git status...
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    if exist ".git" (
        echo  -^> Pulling latest engine scripts from GitHub...
        git pull origin main
        goto PIP_UPDATE
    )
)

echo  -^> Updating via PowerShell smart updater...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1"
goto FINISHED

:PIP_UPDATE
echo.
echo [2/3] Verifying Python libraries (windnd, Pillow, psutil, pystray)...
python -m pip install --upgrade pillow psutil pystray windnd --quiet --no-warn-script-location

echo.
echo [3/3] Updating Desktop shortcuts...
python "%~dp0scripts\create_shortcuts.py" "%~dp0."

echo.
echo ======================================================================
echo    🎉 Success! Anime Studio Pro is updated to the latest version!
echo    All 301+ 4K wallpapers and personal settings were preserved.
echo ======================================================================
echo.

set /p launch="Do you want to start Anime Studio Pro now? (Y/N): "
if /i "!launch!"=="Y" (
    start "" pythonw "%~dp0AnimeStudio.pyw"
)

:FINISHED
exit /b 0
