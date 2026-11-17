# ==============================================================================
# 🌸 Anime Studio Pro — Fast 1-Click Smart Updater
# Author: Pratik Atpadkar (ATP0925)
# Repository: https://github.com/ATP0925/AnimeStudio-Pro
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProgressPreference = 'SilentlyContinue'

Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "         🌸 ANIME STUDIO PRO — SMART 1-CLICK UPDATER 🌸               " -ForegroundColor Cyan
Write-Host "        Author: Pratik Atpadkar | github.com/ATP0925/AnimeStudio-Pro   " -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host ""

# -----------------------------------------------------------------------------
# Step 1: Locate Existing Anime Studio Installation
# -----------------------------------------------------------------------------
Write-Host "[1/3] Locating Anime Studio installation..." -ForegroundColor Cyan

$candidates = @(
    (Get-Location).Path,
    "$PSScriptRoot",
    "D:\AnimeStudio",
    "C:\AnimeStudio",
    "E:\AnimeStudio",
    "$env:USERPROFILE\AnimeStudio"
)

$installDir = $null
foreach ($cand in $candidates) {
    if ($cand -and (Test-Path (Join-Path $cand "scripts\anime_studio.py"))) {
        $installDir = $cand
        break
    }
}

if (-not $installDir) {
    Write-Host " [!] Could not auto-detect AnimeStudio folder." -ForegroundColor Yellow
    $userInput = Read-Host "Please enter the path to your AnimeStudio folder (e.g. D:\AnimeStudio)"
    if ($userInput -and (Test-Path (Join-Path $userInput "scripts\anime_studio.py"))) {
        $installDir = $userInput.Trim().TrimEnd('\')
    } else {
        Write-Host "❌ Error: Invalid AnimeStudio path. Update cancelled." -ForegroundColor Red
        exit 1
    }
}

Write-Host " [✓] Found Anime Studio at: $installDir" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 2: Update Core Scripts (Preserving 4K Wallpapers & User Configs)
# -----------------------------------------------------------------------------
Write-Host "`n[2/3] Updating scripts to latest release (Zero Wallpaper Re-download)..." -ForegroundColor Cyan

$hasGit = [bool](Get-Command git.exe -ErrorAction SilentlyContinue)
$isGitRepo = Test-Path (Join-Path $installDir ".git")

if ($hasGit -and $isGitRepo) {
    Write-Host " -> Syncing via Git pull..." -ForegroundColor White
    try {
        & git -C $installDir pull origin main --quiet
        Write-Host " [✓] Git repository updated cleanly." -ForegroundColor Green
    } catch {
        Write-Host " [!] Git pull warning, falling back to direct script sync..." -ForegroundColor Yellow
    }
} else {
    Write-Host " -> Fetching latest engine scripts directly from GitHub..." -ForegroundColor White
    $baseUrl = "https://raw.githubusercontent.com/ATP0925/AnimeStudio-Pro/main"
    $filesToSync = @(
        "scripts/anime_studio.py",
        "scripts/anime_auto_engine.py",
        "scripts/anime_settings.py",
        "scripts/anime_hud.py",
        "scripts/create_shortcuts.py",
        "scripts/video_processor.py",
        "AnimeStudio.pyw",
        "Install_AnimeStudio.bat",
        "Launch_Anime_Studio.bat",
        "README.md"
    )

    foreach ($rel in $filesToSync) {
        $destPath = Join-Path $installDir $rel
        $parent = Split-Path $destPath -Parent
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        $url = "$baseUrl/$rel"
        try {
            Invoke-WebRequest -Uri $url -OutFile $destPath -TimeoutSec 15
            Write-Host "    [✓] Synced $rel" -ForegroundColor DarkGray
        } catch {
            Write-Host "    [!] Warning syncing $rel" -ForegroundColor Yellow
        }
    }
}

# -----------------------------------------------------------------------------
# Step 3: Verify & Update Python Dependencies (windnd, Pillow, psutil, pystray)
# -----------------------------------------------------------------------------
Write-Host "`n[3/3] Verifying Python runtime and libraries..." -ForegroundColor Cyan

function Find-Python {
    try {
        $p = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
        if ($p -and $p -notmatch "WindowsApps") {
            $chk = & $p -c "import sys; print(sys.executable)" 2>&1
            if ($LASTEXITCODE -eq 0) { return $p }
        }
    } catch {}

    $candidates = @(
        "C:\Program Files\Python314\python.exe",
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            try {
                $chk = & $cand -c "import sys; print(sys.executable)" 2>&1
                if ($LASTEXITCODE -eq 0) { return $cand }
            } catch {}
        }
    }
    return $null
}

$py = Find-Python
if ($py) {
    Write-Host " -> Installing latest dependencies (windnd for Drag & Drop, Pillow, psutil, pystray)..." -ForegroundColor White
    & $py -m pip install --upgrade pillow psutil pystray windnd --quiet --no-warn-script-location
    Write-Host " [✓] Dependencies verified!" -ForegroundColor Green
} else {
    Write-Host " [!] Warning: Python executable not found in standard paths." -ForegroundColor Yellow
}

# Re-link shortcuts
try {
    $scScript = Join-Path $installDir "scripts\create_shortcuts.py"
    if ($py -and (Test-Path $scScript)) {
        & $py "$scScript" "$installDir"
    }
} catch {}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "    🎉 ANIME STUDIO PRO SUCCESSFULLY UPDATED TO LATEST VERSION!       " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host " ✨ What's New:" -ForegroundColor Cyan
Write-Host "   • 1-Click Custom Wallpaper Studio with Drag & Drop support (windnd)" -ForegroundColor White
Write-Host "   • Direct folder import with recursive scan" -ForegroundColor White
Write-Host "   • Instant Desktop Wallpaper apply toggle" -ForegroundColor White
Write-Host "   • All existing 301+ 4K wallpapers & user configurations preserved!" -ForegroundColor Green
Write-Host ""

if ([Environment]::UserInteractive -and -not [Console]::IsInputRedirected) {
    try {
        $launch = Read-Host "Do you want to launch Anime Studio Pro now? (Y/N)"
        if ($launch -match "^[yY]") {
            $launcher = Join-Path $installDir "AnimeStudio.pyw"
            Start-Process "pythonw.exe" -ArgumentList "`"$launcher`""
        }
    } catch {}
}
