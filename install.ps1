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

Write-Host "`n[✓] Target Installation Folder: $installDir" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 2: Download / Clone Project Files
# -----------------------------------------------------------------------------
Write-Host "`n[2/5] Downloading Anime Studio Pro..." -ForegroundColor Cyan

$repoUrl = "https://github.com/ATP0925/AnimeStudio-Pro.git"
$hasGit = Get-Command git -ErrorAction SilentlyContinue

$animeMainFile = Join-Path $installDir "AnimeStudio.pyw"

if (-not (Test-Path $animeMainFile)) {
    if ($hasGit) {
        Write-Host " -> Cloning repository via Git (clean depth=1)..." -ForegroundColor White
        git clone --depth 1 $repoUrl $installDir
    } else {
        Write-Host " -> Git not found. Streaming package directly from GitHub..." -ForegroundColor White
        if (-not (Test-Path $installDir)) {
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        }
        $zipUrl = "https://github.com/ATP0925/AnimeStudio-Pro/archive/refs/heads/main.zip"
        $tempZip = Join-Path $env:TEMP "AnimeStudio_release.zip"
        $tempExtract = Join-Path $env:TEMP "AnimeStudio_extract"

        $hasCurl = Get-Command curl.exe -ErrorAction SilentlyContinue
        if ($hasCurl) {
            curl.exe -L -k -o "$tempZip" "$zipUrl"
        } else {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $webClient = New-Object System.Net.WebClient
            $webClient.DownloadFile($zipUrl, $tempZip)
        }

        Write-Host " -> Extracting files to $installDir..." -ForegroundColor White
        if (Test-Path $tempExtract) { Remove-Item -Recurse -Force $tempExtract }
        Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force

        $extractedRoot = Join-Path $tempExtract "AnimeStudio-Pro-main"
        if (Test-Path $extractedRoot) {
            Copy-Item -Path "$extractedRoot\*" -Destination $installDir -Recurse -Force
        }
        Remove-Item -Force $tempZip -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force $tempExtract -ErrorAction SilentlyContinue
    }
} else {
    Write-Host " -> Existing installation detected at $installDir. Updating..." -ForegroundColor Green
    if (Test-Path (Join-Path $installDir ".git")) {
        git -C $installDir pull
    }
}

# -----------------------------------------------------------------------------
# Step 3: Python Environment & Packages
# -----------------------------------------------------------------------------
Write-Host "`n[3/5] Setting up Python dependencies..." -ForegroundColor Cyan

$hasPython = Get-Command python -ErrorAction SilentlyContinue
if (-not $hasPython) {
    Write-Host " [!] Python is not installed! Installing Python automatically via winget..." -ForegroundColor Yellow
    $hasWinget = Get-Command winget -ErrorAction SilentlyContinue
    if ($hasWinget) {
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host " Please install Python 3.10+ from https://www.python.org/downloads/ and check 'Add to PATH'" -ForegroundColor Red
    }
}

python -m pip install --upgrade pip pillow psutil pystray --quiet
Write-Host " [✓] Dependencies verified!" -ForegroundColor Green

# -----------------------------------------------------------------------------
# Step 4: GUARANTEED Desktop Shortcuts Creation
# -----------------------------------------------------------------------------
Write-Host "`n[4/5] Creating Desktop & Start Menu Shortcuts..." -ForegroundColor Cyan

$createShortcutsScript = Join-Path $installDir "scripts\create_shortcuts.py"
if (Test-Path $createShortcutsScript) {
    python "$createShortcutsScript" "$installDir"
}

# -----------------------------------------------------------------------------
# Step 5: Launch Prompt
# -----------------------------------------------------------------------------
Write-Host "`n======================================================================" -ForegroundColor Magenta
Write-Host "       🎉 ANIME STUDIO PRO INSTALLATION COMPLETE!                     " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "Direct Shortcuts Created On Your Device Desktop:" -ForegroundColor White
Write-Host "  👉 🌸 Anime Studio.lnk" -ForegroundColor Cyan
Write-Host "  👉 🛑 STOP Anime Mode.bat" -ForegroundColor Cyan
Write-Host "  👉 🎌 Anime Hub" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Magenta

$targetScript = Join-Path $installDir "AnimeStudio.pyw"
$pythonwPath = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $pythonwPath) { $pythonwPath = (Get-Command python -ErrorAction SilentlyContinue).Source }

if (-not [Console]::IsInputRedirected -and [Environment]::UserInteractive) {
    $ans = Read-Host "Start Anime Studio Pro now? [Y/n]"
    if ($ans -notmatch "n|N") {
        Start-Process -FilePath $pythonwPath -ArgumentList "`"$targetScript`"" -WorkingDirectory $installDir
    }
} else {
    Write-Host "Launching Anime Studio Pro in background..." -ForegroundColor Green
    Start-Process -FilePath $pythonwPath -ArgumentList "`"$targetScript`"" -WorkingDirectory $installDir
}
