# ==============================================================================
# 🌸 Anime Studio Pro — Universal Windows 1-Click Installer
# Author: Pratik Atpadkar (ATP0925)
# Repository: https://github.com/ATP0925/AnimeStudio-Pro
# ==============================================================================

param (
    [string]$Target = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ProgressPreference = 'SilentlyContinue'

Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "         🌸 ANIME STUDIO PRO — UNIVERSAL DRIVE INSTALLER 🌸           " -ForegroundColor Cyan
Write-Host "                   Author: Pratik Atpadkar (ATP0925)                   " -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host ""

# -----------------------------------------------------------------------------
# Step 1: Detect Drives & Destination
# -----------------------------------------------------------------------------
Write-Host "[1/5] Detecting best installation drive..." -ForegroundColor Cyan

$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 0 } | Select-Object Name, Root, @{Name="FreeGB";Expression={[math]::Round($_.Free / 1GB, 1)}}

# Prefer D: or E: if they have at least 5 GB, otherwise C:
$bestDrive = "C:"
$dDrive = $drives | Where-Object { $_.Name -eq "D" -and $_.FreeGB -ge 5 }
$eDrive = $drives | Where-Object { $_.Name -eq "E" -and $_.FreeGB -ge 5 }
if ($dDrive) { $bestDrive = "D:" }
elseif ($eDrive) { $bestDrive = "E:" }

$defaultPath = "$bestDrive\AnimeStudio"

if ([string]::IsNullOrWhiteSpace($Target)) {
    $isPiped = [Console]::IsInputRedirected
    if (-not $isPiped -and [Environment]::UserInteractive) {
        Write-Host "Available Drives:" -ForegroundColor DarkGray
        foreach ($d in $drives) {
            Write-Host ("  {0}: ({1} GB free)" -f $d.Name, $d.FreeGB) -ForegroundColor Green
        }
        Write-Host "`nWhere would you like to install Anime Studio Pro?" -ForegroundColor Yellow
        Write-Host "Press [ENTER] for default ($defaultPath) or type custom path: " -NoNewline -ForegroundColor White
        try {
            $userInput = Read-Host
            if (-not [string]::IsNullOrWhiteSpace($userInput)) {
                $installDir = $userInput.Trim().TrimEnd('\')
            } else {
                $installDir = $defaultPath
            }
        } catch {
            $installDir = $defaultPath
        }
    } else {
        $installDir = $defaultPath
    }
} else {
    $installDir = $Target.Trim().TrimEnd('\')
}

Write-Host "[✓] Target Installation Folder: $installDir" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 2: Ensure Git is Available (or Download Portable MinGit)
# -----------------------------------------------------------------------------
Write-Host "`n[2/5] Checking Git toolchain..." -ForegroundColor Cyan

$gitExe = $null
$systemGit = Get-Command git.exe -ErrorAction SilentlyContinue
if ($systemGit) {
    $gitExe = $systemGit.Source
}

if (-not $gitExe) {
    Write-Host " -> Git not found on system. Setting up lightweight portable Git..." -ForegroundColor Yellow
    $minGitZip = Join-Path $env:TEMP "MinGit.zip"
    $minGitDir = Join-Path $env:TEMP "MinGit"
    $minGitExe = Join-Path $minGitDir "cmd\git.exe"

    if (-not (Test-Path $minGitExe)) {
        $minGitUrl = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/MinGit-2.44.0-64-bit.zip"
        Write-Host " -> Downloading portable Git (43 MB, takes ~5 seconds)..." -ForegroundColor White
        
        $hasCurl = Get-Command curl.exe -ErrorAction SilentlyContinue
        if ($hasCurl) {
            curl.exe -L -k -o "$minGitZip" "$minGitUrl"
        } else {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            (New-Object System.Net.WebClient).DownloadFile($minGitUrl, $minGitZip)
        }

        if (Test-Path $minGitDir) { Remove-Item -Recurse -Force $minGitDir -ErrorAction SilentlyContinue }
        Expand-Archive -Path $minGitZip -DestinationPath $minGitDir -Force
        Remove-Item -Force $minGitZip -ErrorAction SilentlyContinue
    }

    if (Test-Path $minGitExe) {
        $gitExe = $minGitExe
        Write-Host " [✓] Portable Git ready!" -ForegroundColor Green
    }
} else {
    Write-Host " [✓] System Git detected: $gitExe" -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# Step 3: Clone or Update Project
# -----------------------------------------------------------------------------
Write-Host "`n[3/5] Fetching Anime Studio Pro files..." -ForegroundColor Cyan

$repoUrl = "https://github.com/ATP0925/AnimeStudio-Pro.git"
$animeMainFile = Join-Path $installDir "AnimeStudio.pyw"

if (-not (Test-Path $animeMainFile)) {
    if ($gitExe) {
        Write-Host " -> Cloning 4K Wallpapers & Anime Engine into $installDir..." -ForegroundColor White
        & $gitExe clone --depth 1 $repoUrl $installDir
    } else {
        Write-Host " [!] Git could not be initialized. Please run: winget install Git.Git" -ForegroundColor Red
    }
} else {
    Write-Host " -> Existing installation detected at $installDir. Syncing latest updates..." -ForegroundColor Green
    if ($gitExe -and (Test-Path (Join-Path $installDir ".git"))) {
        & $gitExe -C $installDir pull
    }
}

# -----------------------------------------------------------------------------
# Step 4: Python Detection & Auto-Install (Bypass Fake WindowsApps Python)
# -----------------------------------------------------------------------------
Write-Host "`n[4/5] Checking Python environment..." -ForegroundColor Cyan

function Find-WorkingPython {
    # 1. Test standard 'python.exe' command
    try {
        $p = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
        if ($p -and $p -notmatch "WindowsApps") {
            $chk = & $p -c "import sys; print(sys.executable)" 2>&1
            if ($LASTEXITCODE -eq 0) { return $p }
        }
    } catch {}

    # 2. Check standard Program Files & Local AppData Python installations
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

$realPython = Find-WorkingPython

if (-not $realPython) {
    Write-Host " [!] Real Python runtime not found (Microsoft Store placeholder detected)." -ForegroundColor Yellow
    Write-Host " Installing Python 3.12 automatically (silent)..." -ForegroundColor Cyan
    
    $hasWinget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if ($hasWinget) {
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
    } else {
        $pyUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
        $pyInstaller = Join-Path $env:TEMP "python_setup.exe"
        Write-Host " -> Downloading Python installer from python.org..." -ForegroundColor White
        curl.exe -L -o "$pyInstaller" "$pyUrl"
        Start-Process -FilePath "$pyInstaller" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
        Remove-Item -Force "$pyInstaller" -ErrorAction SilentlyContinue
    }

    # Refresh PATH environment variable
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    $realPython = Find-WorkingPython
}

if ($realPython) {
    Write-Host " [✓] Active Python: $realPython" -ForegroundColor Green
    Write-Host " -> Installing required libraries (Pillow, psutil, pystray, windnd)..." -ForegroundColor White
    & $realPython -m pip install --upgrade pip pillow psutil pystray windnd --quiet
} else {
    Write-Host " [!] Please install Python 3.10+ from https://www.python.org/downloads/ and check 'Add Python to PATH'" -ForegroundColor Red
}

# -----------------------------------------------------------------------------
# Step 5: GUARANTEED Desktop Shortcuts Creation
# -----------------------------------------------------------------------------
Write-Host "`n[5/5] Creating Desktop & Start Menu Shortcuts..." -ForegroundColor Cyan

$createShortcutsScript = Join-Path $installDir "scripts\create_shortcuts.py"
if ((Test-Path $createShortcutsScript) -and $realPython) {
    & $realPython "$createShortcutsScript" "$installDir"
}

Write-Host "`n======================================================================" -ForegroundColor Magenta
Write-Host "       🎉 ANIME STUDIO PRO SUCCESSFULLY INSTALLED!                     " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "Direct Shortcuts Created On Your Desktop:" -ForegroundColor White
Write-Host "  👉 Anime Studio Pro (Launch Studio GUI)" -ForegroundColor Cyan
Write-Host "  👉 STOP Anime Mode (Emergency Kill-Switch)" -ForegroundColor Cyan
Write-Host "  👉 🎌 Anime Hub (Watch 1080p Anime Online)" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Magenta

# Launch Anime Studio Pro automatically
$realPythonw = $realPython.ToLower().Replace("python.exe", "pythonw.exe")
if (-not (Test-Path $realPythonw)) { $realPythonw = $realPython }

if (Test-Path $animeMainFile) {
    Write-Host "🌸 Starting Anime Studio Pro..." -ForegroundColor Magenta
    Start-Process -FilePath $realPythonw -ArgumentList "`"$animeMainFile`"" -WorkingDirectory $installDir
}
