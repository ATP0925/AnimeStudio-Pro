@echo off
setlocal
cd /d "%~dp0"
title Launch Anime Studio Pro

where pythonw >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "" pythonw "%~dp0AnimeStudio.pyw"
    exit /b 0
)

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "" python "%~dp0AnimeStudio.pyw"
    exit /b 0
)

echo [ERROR] Python was not found in PATH!
echo Please install Python 3.10+ from https://www.python.org/ or run winget install Python.Python.3.12
pause
exit /b 1
