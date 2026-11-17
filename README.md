# 🌸 Anime Studio Pro — All-In-One Anime Desktop Suite

**Author:** [Pratik Atpadkar (ATP0925)](https://github.com/ATP0925)  
**Repository:** [https://github.com/ATP0925/AnimeStudio-Pro](https://github.com/ATP0925/AnimeStudio-Pro)

**Anime Studio Pro** is a fully portable, aesthetic anime automation suite designed for Windows 10/11. It transforms your desktop into an immersive anime experience with ultra-crisp 4K/5K/8K widescreen wallpapers, synchronized viral theme songs and Japanese voice climaxes, full interval customization (5 seconds up to 1 Year+), built-in streaming portals, a floating mini-widget, and Windows System Tray integration.

---

## 🚀 Quick Install (Any Drive: C:, D:, E:, etc.)

Anime Studio Pro is **100% portable**. You can install and run it on **any drive or custom folder** without breaking paths or shortcuts.

### Method 1: 1-Line Universal PowerShell Installer (Recommended)
Open PowerShell (Win + X $\rightarrow$ Terminal or PowerShell) and paste:
```powershell
irm https://raw.githubusercontent.com/ATP0925/AnimeStudio-Pro/main/install.ps1 | iex
```
* **Drive Selection**: The installer automatically displays all connected drives (`C:`, `D:`, `E:`, etc.) and their free space, allowing you to choose your preferred target.
* **Automatic Setup**: It configures Python dependencies (`Pillow`, `psutil`, `pystray`), creates high-res Desktop shortcuts, and sets up the emergency stop button.

---

### Method 2: Git Clone to Any Drive
```powershell
# Example: Clone to D: drive
git clone https://github.com/ATP0925/AnimeStudio-Pro.git D:\AnimeStudio
cd D:\AnimeStudio
.\Install_AnimeStudio.bat
```

---

### Method 3: Direct ZIP Download
1. Click **Code $\rightarrow$ Download ZIP** on GitHub (or download latest release).
2. Extract the folder to any drive (e.g., `D:\AnimeStudio` or `E:\AnimeStudio`).
3. Double-click **`Install_AnimeStudio.bat`** to create Desktop shortcuts and install dependencies.

---

## 🔄 Fast 1-Click Update (Zero Wallpaper Re-download)

If you already have Anime Studio Pro installed and want the latest features (e.g. Custom Wallpaper Studio with Drag & Drop):

### 1-Line Universal PowerShell Update (Recommended)
Open PowerShell and run:
```powershell
irm https://raw.githubusercontent.com/ATP0925/AnimeStudio-Pro/main/update.ps1 | iex
```
* **Lightning Fast (~3 seconds)**: Syncs only updated scripts and dependencies (`windnd`).
* **100% Safe**: Never re-downloads the 301+ 4K wallpapers, touches existing audio, or overwrites your personal custom files.

### Offline / Local Update
Double-click **`Update_AnimeStudio.bat`** inside your `AnimeStudio` folder.

---

## 🌟 Key Features

### 1. 🎨 1-Click Custom Wallpaper Studio (Drag & Drop + Folders)
* **Instant Drag & Drop**: Drag and drop any image, GIF, video, or entire folder directly into Anime Studio from Windows File Explorer.
* **1-Click Apply**: Instantly set any imported wallpaper as your active Windows desktop background with zero delay.
* **Format Versatility**: Supports PNG, JPG, JPEG, WEBP, BMP, animated GIFs, and video loops (`.mp4`, `.webm`, `.mkv`).
* **Visual Gallery & Management**: Interactive thumbnail grid showing all your personal wallpapers with 1-click "Set as Desktop" and delete controls.
* **Batch Folder Import**: Import full folders of anime wallpapers in one click with recursive directory scanning.

### 2. 🖼️ Curated 4K/5K/8K UHD Wallpaper Gallery (301+ Masterpieces)
* **Zero Low-Quality / Cheap Art**: All blurry, low-res, non-anime, or vertical phone wallpapers have been purged.
* **11 Core Anime Categories**:
  1. **Jujutsu Kaisen** (Satoru Gojo Unlimited Void, Sukuna Malevolent Shrine)
  2. **Demon Slayer** (Tanjiro Hinokami Kagura, Infinity Castle 4K)
  3. **One Piece** (Luffy Gear 5 Full Moon, Wano Climax)
  4. **Attack on Titan** (Levi Ackerman Forest Chase, The Rumbling)
  5. **Naruto Shippuden** (Sage Mode Naruto, Susanoo Itachi, Final Valley)
  6. **Frieren: Beyond Journey's End** (Zoltraak Destruction Magic 4K/6K)
  7. **Solo Leveling** (Sung Jin-Woo Shadow Monarch 4K/8K)
  8. **Cyberpunk: Edgerunners** (Lucy on the Moon, Night City)
  9. **Studio Ghibli Masterpieces** (Spirited Away, Howl's Moving Castle 4K)
  10. **Makoto Shinkai Universe** (Your Name, Suzume, Weathering With You 4K)
  11. **Fate Series** (Saber Artoria Excalibur 4K)
  12. **Custom Wallpapers** (Instant personal studio with drag & drop)
  13. **Live Anime Stills** (Automated 4K frame extraction from video loops)

### 3. ⏱️ Long-Term Scheduler (5 Seconds up to 1 Year+)
* **Unlimited Customization**: Set rotation interval in Seconds, Minutes, Hours, Days, Weeks, Months, or Years!
* **Quick Presets**:
  * *Short*: `10s` | `30s` | `1m` | `5m` | `15m` | `30m`
  * *Long*: `1 Hour` | `6 Hours` | `1 Day` | `1 Week` | `1 Month` | `1 Year`
* **Real-Time Date & Time Preview**: Shows the exact calendar date and clock time of your next wallpaper change.
* **Reboot & Sleep Persistence**: Target timestamps are saved to disk; your schedule remains intact across Windows reboots, sleep, and hibernate.
* **Startup Auto-Run**: Optional toggle to launch automatically with Windows.

### 3. 🎵 Authentic Anime Audio Studio
* **Viral Theme Anthems**:
  * *One Piece* $\rightarrow$ **Overtaken** (Legendary Walk Theme)
  * *Naruto* $\rightarrow$ **Silhouette** (KANA-BOON)
  * *Jujutsu Kaisen* $\rightarrow$ **Lost in Paradise** (ALI feat. AKLO)
  * *Demon Slayer* $\rightarrow$ **Infinity Castle Epic Theme**
  * *Attack on Titan* $\rightarrow$ **Shinzou wo Sasageyo!**
  * *Frieren* $\rightarrow$ **Zoltraak Climax Symphony**
  * *Cyberpunk* $\rightarrow$ **I Really Want to Stay at Your House**
  * *Studio Ghibli* $\rightarrow$ **Merry-Go-Round of Life**
  * *Tokyo Ghoul / Shinkai* $\rightarrow$ **Unravel**
  * *Solo Leveling / Fate* $\rightarrow$ **Ultra Instinct Climax Anthem**
* **Original Japanese Voice Dialogue**:
  * Gojo: *Domain Expansion (Infinite Void)*
  * Sukuna: *Domain Expansion (Malevolent Shrine)*
  * Zenitsu: *Thunder Breathing First Form*
  * Luffy: *Gear 5 Drums of Liberation Laugh*
  * Itachi: *Amaterasu*
  * Eren: *Tatakae (Fight)*
  * Frieren: *Zoltraak Destruction Magic*
  * Saber: *Excalibur*
* **Import Custom MP3s**: Easily add any custom song to your library.
* **Playback Modes**: Dynamic Matching, Voice Climax, Specific Track Lock, Shuffle All, or Silent Mode.

### 4. 🌐 Built-In Anime Web Portals
One-click fast links to stream anime and read manga:
* **Miruro Anime** (1080p Ad-Free Streaming, HiAnime Alternative)
* **Marin Anime** (Direct Unblocked Streaming)
* **Crunchyroll** (Official Dubs & Subs)
* **Muse India** (Legal Free YouTube Streaming)
* **Lofi Anime Radio** (24/7 Study & Relax Beats)
* **MangaDex** (Read Free Manga)

### 5. 🛡️ Windows System Tray & Floating Mini-HUD
* **System Tray Minimized Mode**: Closing the app window minimizes it to the Windows notification tray (near clock).
* **Floating Mini-HUD**: Draggable desktop widget showing clock, active anime, and countdown timer.
* **Emergency Kill Switch**: `🛑 STOP Anime Mode.bat` force-stops all wallpaper changes and mutes audio instantly.

---

## 📁 Portable Directory Structure

```
<ANY_DRIVE>\AnimeStudio\
│
├── AnimeStudio.pyw           # Standalone Windowless Entry Point
├── anime_icon.ico            # Official High-Res Anime Application Icon
├── install.ps1               # Universal 1-Click Online Installer
├── Install_AnimeStudio.bat   # 1-Click Offline Setup & Shortcut Creator
├── Launch_Anime_Studio.bat   # Portable Launcher Batch Script
├── launch_studio.vbs         # Silent Background Launcher
├── README.md                 # Complete Project Documentation
│
├── config\
│   ├── settings.json         # Persistent User Configuration
│   └── app.pid               # Single-Instance Lockfile
│
├── audio\
│   ├── viral_songs\          # 10 Signature Anime Theme Songs & User MP3s
│   └── original\             # 10 Authentic Japanese Voice Climaxes
│
├── wallpapers\
│   └── collection\           # 301+ Curated 4K/5K/8K UHD Anime Wallpapers
│       ├── 01_Jujutsu_Kaisen\
│       ├── 02_Demon_Slayer\
│       ├── 03_One_Piece\
│       ├── 04_Attack_on_Titan\
│       ├── 05_Naruto_Shippuden\
│       ├── 06_Frieren\
│       ├── 07_Solo_Leveling\
│       ├── 08_Cyberpunk_Edgerunners\
│       ├── 09_Studio_Ghibli\
│       ├── 10_Makoto_Shinkai\
│       ├── 11_Fate_Series\
│       ├── 12_Custom_Wallpapers\
│       └── 13_Live_Anime_Stills\
│
└── scripts\
    ├── anime_studio.py       # Master GUI Application & System Tray Host
    ├── anime_auto_engine.py  # 5-Second Transition Overlay & Win32 API Engine
    ├── anime_settings.py     # Configuration, Conversion & Startup Manager
    ├── stop_anime.py         # Emergency Process & Audio Termination Script
    ├── transition_overlay.py # Smooth Fade & Hardware Video Transition Player
    └── video_processor.py    # 4K Video Frame Extractor & Transition Manager
```

---
*Created with ❤️ by **Pratik Atpadkar** for ultimate anime pair-programming and desktop aesthetics.*
