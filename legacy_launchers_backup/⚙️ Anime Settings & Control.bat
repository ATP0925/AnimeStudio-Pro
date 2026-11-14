@echo off
title Anime Dashboard Settings ^& Control Center
color 0B
echo ========================================================
echo   ⚙️ OPENING ANIME SETTINGS ^& CONTROL CENTER...
echo ========================================================
start "" "pythonw" "%~dp0..\scripts\anime_control_center.py"
echo.
echo Control Center is open! You can:
echo  - Change timer (10s, 30s, 1m, 5m, custom)
echo  - Pick a specific viral song or auto-match anime
echo  - Filter to a single anime or shuffle all
echo  - Toggle 5-second cinematic transitions
echo ========================================================
timeout /t 3 >nul

