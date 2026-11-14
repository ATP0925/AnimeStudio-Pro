# ==============================================================================
# 🌸 Anime Studio Pro — Universal Windows Installer
# Author: Pratik Atpadkar (ATP0925)
# Repository: https://github.com/ATP0925/AnimeStudio-Pro
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "🌸 Anime Studio Pro — Universal Installer"

function Print-Banner {
    Clear-Host
    Write-Host "======================================================================" -ForegroundColor Magenta
    Write-Host "         🌸 ANIME STUDIO PRO — UNIVERSAL DRIVE INSTALLER 🌸           " -ForegroundColor Cyan
    Write-Host "                   Author: Pratik Atpadkar (ATP0925)                   " -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Magenta
    Write-Host ""
}

Print-Banner

# Step 1: Detect Available Drives
Write-Host "[1/6] Scanning available drives and free storage..." -ForegroundColor Cyan
$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 0 } | Select-Object Name, Root, @{Name="FreeGB";Expression={[math]::Round($_.Free / 1GB, 1)}}

Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Drive   Mount Path   Free Space" -ForegroundColor White
Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
foreach ($d in $drives) {
    Write-Host ("  {0}:      {1,-12} {2} GB Free" -f $d.Name, $d.Root, $d.FreeGB) -ForegroundColor Green
}
Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

# Determine recommended default drive (Prefer D: or E: if > 5GB, else C:)
$recommendedDrive = "C:"
$dDrive = $drives | Where-Object { $_.Name -eq "D" -and $_.FreeGB -ge 5 }
$eDrive = $drives | Where-Object { $_.Name -eq "E" -and $_.FreeGB -ge 5 }
if ($dDrive) { $recommendedDrive = "D:" }
elseif ($eDrive) { $recommendedDrive = "E:" }

$defaultPath = "$recommendedDrive\AnimeStudio"

Write-Host "Where would you like to install Anime Studio Pro?" -ForegroundColor Yellow
Write-Host "Press [ENTER] to use default: " -NoNewline -ForegroundColor White
Write-Host "$defaultPath" -ForegroundColor Cyan
$userChoice = Read-Host "Or enter target folder path (e.g., D:\AnimeStudio, E:\Games\AnimeStudio)"

$installDir = if ([string]::IsNullOrWhiteSpace($userChoice)) { $defaultPath } else { $userChoice.Trim().TrimEnd('\') }

Write-Host "`n[✓] Selected Installation Target: " -NoNewline -ForegroundColor White
Write-Host "$installDir" -ForegroundColor Green
Write-Host ""

# Step 2: Ensure Target Directory Exists
if (-not (Test-Path $installDir)) {
    Write-Host "[2/6] Creating installation directory at $installDir..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
} else {
    Write-Host "[2/6] Target directory exists: $installDir" -ForegroundColor Cyan
}

# Step 3: Download or Clone Repository
$repoUrl = "https://github.com/ATP0925/AnimeStudio-Pro.git"
$zipUrl = "https://github.com/ATP0925/AnimeStudio-Pro/archive/refs/heads/main.zip"

Write-Host "`n[3/6] Fetching Anime Studio Pro files..." -ForegroundColor Cyan
$hasGit = Get-Command git -ErrorAction SilentlyContinue

$animeStudioFile = Join-Path $installDir "AnimeStudio.pyw"
if (-not (Test-Path $animeStudioFile)) {
    if ($hasGit) {
        Write-Host " -> Git detected! Cloning repository directly..." -ForegroundColor Green
        git clone --depth 1 $repoUrl $installDir
    } else {
        Write-Host " -> Git not found. Downloading repository package via HTTPS..." -ForegroundColor Yellow
        $tempZip = Join-Path $env:TEMP "AnimeStudio_setup.zip"
        $tempExtract = Join-Path $env:TEMP "AnimeStudio_extract"

        Write-Host " -> Downloading from GitHub (this may take a moment for 4K wallpapers)..." -ForegroundColor White
        Invoke-WebRequest -Uri $zipUrl -OutFile $tempZip

        Write-Host " -> Extracting files into $installDir..." -ForegroundColor White
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
    Write-Host " -> Existing installation detected in $installDir. Skipping re-download." -ForegroundColor Green
}

# Step 4: Python & Dependencies Check
Write-Host "`n[4/6] Checking Python runtime..." -ForegroundColor Cyan
$hasPython = Get-Command python -ErrorAction SilentlyContinue
if (-not $hasPython) {
    Write-Host " [!] Python is not installed on this system!" -ForegroundColor Red
    Write-Host " Attempting automatic Python 3.12 installation via winget..." -ForegroundColor Yellow
    $hasWinget = Get-Command winget -ErrorAction SilentlyContinue
    if ($hasWinget) {
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host " Please download and install Python from: https://www.python.org/downloads/" -ForegroundColor Red
        Write-Host " Ensure you check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
        pause
    }
} else {
    Write-Host " [✓] Python detected: $((Get-Command python).Source)" -ForegroundColor Green
}

Write-Host " Installing required Python libraries (Pillow, psutil)..." -ForegroundColor Cyan
python -m pip install --upgrade pip pillow psutil pystray --quiet

# Step 5: Create Desktop Shortcuts
Write-Host "`n[5/6] Creating Desktop shortcuts..." -ForegroundColor Cyan

$desktopDir = [System.Environment]::GetFolderPath('Desktop')
if (Test-Path "$env:USERPROFILE\OneDrive\Desktop") {
    $desktopDir = "$env:USERPROFILE\OneDrive\Desktop"
}

$WshShell = New-Object -ComObject WScript.Shell
$iconPath = Join-Path $installDir "anime_icon.ico"
$targetScript = Join-Path $installDir "AnimeStudio.pyw"

# 1. Main Anime Studio Shortcut
$shortcutPath = Join-Path $desktopDir "🌸 Anime Studio.lnk"
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$pythonwPath = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $pythonwPath) {
    $pythonwPath = (Get-Command python -ErrorAction SilentlyContinue).Source
}
$shortcut.TargetPath = $pythonwPath
$shortcut.Arguments = "`"$targetScript`""
$shortcut.WorkingDirectory = $installDir
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}
$shortcut.Description = "Launch Anime Studio Pro (4K Wallpapers & Viral Audio)"
$shortcut.Save()
Write-Host " [✓] Created Desktop Shortcut: 🌸 Anime Studio.lnk" -ForegroundColor Green

# 2. Emergency Kill Switch Shortcut
$stopBatSrc = Join-Path $installDir "scripts\stop_anime.py"
$stopBatDst = Join-Path $desktopDir "🛑 STOP Anime Mode.bat"
$stopBatContent = @"
@echo off
title Emergency Stop Anime Mode
echo Stopping Anime Studio Pro and MCI Audio...
python "$stopBatSrc"
exit /b 0
"@
Set-Content -Path $stopBatDst -Value $stopBatContent -Encoding ASCII
Write-Host " [✓] Created Desktop Kill-Switch: 🛑 STOP Anime Mode.bat" -ForegroundColor Green

# 3. Create Anime Hub Folder on Desktop
$animeHubDir = Join-Path $desktopDir "🎌 Anime Hub"
if (-not (Test-Path $animeHubDir)) {
    New-Item -ItemType Directory -Path $animeHubDir -Force | Out-Null
}

# Create Anime Portals
$portals = @{
    "⚡ Miruro Anime (1080p Ad-Free).url" = "https://miruro.to"
    "⚡ Marin Anime (Direct Unblocked).url" = "https://marin.moe"
    "🎬 Crunchyroll (Official Streaming).url" = "https://www.crunchyroll.com"
    "📺 Muse India (YouTube Official).url" = "https://www.youtube.com/@MuseIndia"
    "🌸 Lofi Anime Radio (24x7 Beats).url" = "https://www.youtube.com/watch?v=jfKfPfyJRdk"
}

foreach ($item in $portals.GetEnumerator()) {
    $uPath = Join-Path $animeHubDir $item.Key
    $uContent = "[InternetShortcut]`r`nURL=$($item.Value)`r`n"
    [System.IO.File]::WriteAllText($uPath, $uContent)
}
Write-Host " [✓] Created Desktop Hub: 🎌 Anime Hub" -ForegroundColor Green

# Step 6: Installation Complete
Write-Host "`n======================================================================" -ForegroundColor Magenta
Write-Host "       🎉 ANIME STUDIO PRO SUCCESSFULLY INSTALLED TO $installDir!     " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "Desktop Shortcuts Ready:" -ForegroundColor White
Write-Host "  1. 🌸 Anime Studio.lnk    -> Launch Studio GUI" -ForegroundColor Cyan
Write-Host "  2. 🛑 STOP Anime Mode.bat  -> Stop & Mute All Immediately" -ForegroundColor Cyan
Write-Host "  3. 🎌 Anime Hub           -> Watch 1080p Anime Online" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

$runNow = Read-Host "Would you like to start Anime Studio Pro now? [Y/n]"
if ($runNow -notmatch "n|N") {
    Write-Host "Launching Anime Studio Pro..." -ForegroundColor Magenta
    Start-Process -FilePath $pythonwPath -ArgumentList "`"$targetScript`"" -WorkingDirectory $installDir
}
