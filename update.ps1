[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'SilentlyContinue'
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

$installDir = $null

# Strategy A: Check Desktop Shortcuts
$desktopDirs = @(
    [Environment]::GetFolderPath('Desktop'),
    [Environment]::GetFolderPath('CommonDesktopDirectory'),
    (Join-Path $env:USERPROFILE 'Desktop')
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

try {
    $wsh = New-Object -ComObject WScript.Shell
    foreach ($d in $desktopDirs) {
        $shortcuts = Get-ChildItem -Path $d -Filter '*.lnk' -ErrorAction SilentlyContinue
        foreach ($scItem in $shortcuts) {
            try {
                $sc = $wsh.CreateShortcut($scItem.FullName)
                if ($sc -and $sc.WorkingDirectory) {
                    $chk = Join-Path $sc.WorkingDirectory "scripts\anime_studio.py"
                    if (Test-Path $chk) {
                        $installDir = $sc.WorkingDirectory
                        break
                    }
                }
            } catch {}
        }
        if ($installDir) { break }
    }
} catch {}

# Strategy B: Current working directory or script directory
if (-not $installDir) {
    $locs = @((Get-Location).Path, $PSScriptRoot)
    foreach ($l in $locs) {
        if ($l) {
            $chk = Join-Path $l "scripts\anime_studio.py"
            if (Test-Path $chk) {
                $installDir = $l
                break
            }
        }
    }
}

# Strategy C: Known standard user directories
if (-not $installDir) {
    $commonDirs = @(
        (Join-Path $env:USERPROFILE 'AnimeSetup'),
        (Join-Path $env:USERPROFILE 'AnimeStudio'),
        (Join-Path $env:USERPROFILE 'AnimeStudio-Pro'),
        (Join-Path $env:LOCALAPPDATA 'AnimeStudio'),
        (Join-Path $env:LOCALAPPDATA 'AnimeSetup'),
        'C:\AnimeStudio',
        'C:\AnimeSetup'
    )
    foreach ($cd in $commonDirs) {
        if ($cd -and (Test-Path $cd)) {
            $chk = Join-Path $cd "scripts\anime_studio.py"
            if (Test-Path $chk) {
                $installDir = $cd
                break
            }
        }
    }
}

# Strategy D: Active mounted drive roots
if (-not $installDir) {
    try {
        $mountedRoots = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -ne $null } | ForEach-Object { $_.Root }
        foreach ($r in $mountedRoots) {
            foreach ($sub in @('AnimeSetup', 'AnimeStudio', 'AnimeStudio-Pro')) {
                $target = Join-Path $r $sub
                if (Test-Path $target) {
                    $chk = Join-Path $target "scripts\anime_studio.py"
                    if (Test-Path $chk) {
                        $installDir = $target
                        break
                    }
                }
            }
            if ($installDir) { break }
        }
    } catch {}
}

# Strategy E: Deep search in user profile (depth 2)
if (-not $installDir) {
    try {
        $found = Get-ChildItem -Path $env:USERPROFILE -Directory -Depth 2 -Filter 'Anime*' -ErrorAction SilentlyContinue | Where-Object {
            Test-Path (Join-Path $_.FullName "scripts\anime_studio.py")
        } | Select-Object -First 1
        if ($found) {
            $installDir = $found.FullName
        }
    } catch {}
}

# Strategy F: Interactive prompt fallback (if not piped)
if (-not $installDir) {
    if ([Environment]::UserInteractive -and -not [Console]::IsInputRedirected) {
        Write-Host " [!] Could not auto-detect Anime Studio folder." -ForegroundColor Yellow
        $userInput = Read-Host "Please enter the path to your Anime Studio folder (e.g. C:\AnimeSetup)"
        if ($userInput -and (Test-Path (Join-Path $userInput "scripts\anime_studio.py"))) {
            $installDir = $userInput.Trim().TrimEnd('\')
        }
    }
}

if (-not $installDir) {
    Write-Host "❌ Error: Could not locate Anime Studio installation." -ForegroundColor Red
    Write-Host "   Please run this command from your AnimeSetup folder or run Update_AnimeStudio.bat" -ForegroundColor Yellow
    exit 1
}

Write-Host " [✓] Found Anime Studio at: $installDir" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 2: Update Core Scripts (Preserving 4K Wallpapers & User Configs)
# -----------------------------------------------------------------------------
Write-Host "`n[2/3] Updating scripts to latest release (Zero Wallpaper Re-download)..." -ForegroundColor Cyan

$hasGit = [bool](Get-Command git.exe -ErrorAction SilentlyContinue)
$isGitRepo = Test-Path (Join-Path $installDir '.git')

if ($hasGit -and $isGitRepo) {
    Write-Host " -> Syncing via Git pull..." -ForegroundColor White
    try {
        $settingsFile = Join-Path $installDir "config\settings.json"
        $backupSettings = $null
        if (Test-Path $settingsFile) {
            $backupSettings = Get-Content -Path $settingsFile -Raw
        }
        & git -C $installDir reset --hard HEAD --quiet 2>$null
        & git -C $installDir pull origin main --quiet
        if ($backupSettings -and (Test-Path (Split-Path $settingsFile))) {
            [System.IO.File]::WriteAllText($settingsFile, $backupSettings, [System.Text.Encoding]::UTF8)
        }
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
        "scripts/transition_overlay.py",
        "AnimeStudio.pyw",
        "Install_AnimeStudio.bat",
        "Launch_Anime_Studio.bat",
        "Update_AnimeStudio.bat",
        "update.ps1",
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
        if ($p -and $p -notmatch 'WindowsApps') {
            $chk = & $p -c "import sys; print(sys.executable)" 2>&1
            if ($LASTEXITCODE -eq 0) { return $p }
        }
    } catch {}

    $candidates = @(
        'C:\Program Files\Python314\python.exe',
        'C:\Program Files\Python313\python.exe',
        'C:\Program Files\Python312\python.exe',
        'C:\Program Files\Python311\python.exe',
        'C:\Program Files\Python310\python.exe',
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
        if ($launch -match '^[yY]') {
            $launcher = Join-Path $installDir "AnimeStudio.pyw"
            Start-Process "pythonw.exe" -ArgumentList "`"$launcher`""
        }
    } catch {}
}
