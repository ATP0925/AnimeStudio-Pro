@echo off
setlocal EnableDelayedExpansion
title Anime Studio Pro - 1-Click Desktop Setup
cd /d "%~dp0"

echo ======================================================================
echo          🌸 ANIME STUDIO PRO — 1-CLICK DESKTOP SETUP 🌸              
echo                    Author: Pratik Atpadkar                           
echo ======================================================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python is NOT installed!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Verifying Python libraries (Pillow, psutil, pystray)...
python -m pip install --upgrade pip pillow psutil pystray --quiet

echo [2/3] Creating direct shortcuts on Device Desktop...
python "%~dp0scripts\create_shortcuts.py" "%~dp0."

echo [3/3] Configuration complete!
echo.
echo ======================================================================
echo    🎉 Success! '🌸 Anime Studio' is now on your Device's Desktop!
echo ======================================================================
echo.

set /p launch="Do you want to start Anime Studio Pro now? (Y/N): "
if /i "!launch!"=="Y" (
    start "" pythonw "%~dp0AnimeStudio.pyw"
)
exit /b 0
