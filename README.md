# 🌸 Anime Studio Pro — All-In-One Anime Desktop Suite

**Anime Studio Pro** is an enterprise-grade, aesthetic anime automation suite designed for Windows 10/11. It transforms your desktop into an immersive anime experience with ultra-crisp 4K/5K/8K widescreen wallpapers, synchronized viral theme songs and Japanese voice climaxes, full interval customization (5 seconds up to 1 Year+), built-in streaming portals, a floating mini-widget, and Windows System Tray integration.

---

## 🌟 Key Features

### 1. 🖼️ Curated 4K/5K/8K UHD Wallpaper Gallery (301+ Masterpieces)
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
  12. **Custom Wallpapers** (Import your own pictures easily)

### 2. ⏱️ Long-Term Scheduler (5 Seconds up to 1 Year+)
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
* **HiAnime** (Free 1080p HD Streaming)
* **Crunchyroll** (Official Dubs & Subs)
* **MangaDex** (Read Free Manga)
* **Muse Asia** (Legal Free YouTube Streaming)
* **Lofi Anime Radio** (24/7 Study & Relax Beats)
* **Toonworld** (Anime Episodes & Batch Downloads)

### 5. 🛡️ Windows System Tray & Floating Mini-HUD
* **System Tray Minimized Mode**: Closing the app window minimizes it to the Windows notification tray (near clock).
* **Floating Mini-HUD**: Draggable desktop widget showing clock, active anime, and countdown timer.
* **Emergency Kill Switch**: One click force-stops all wallpaper changes and mutes audio instantly.

---

## 🚀 How to Launch

1. Double-click **`🌸 Anime Studio`** on your Desktop.
2. Select your desired interval, audio mode, and anime filter.
3. Click **`💾 SAVE & APPLY`** or **`🎬 NEXT WALLPAPER`**.

---

## 📁 Directory Structure

```
C:\Users\atpad\AnimeSetup\
│
├── AnimeStudio.pyw           # Standalone Windowless Entry Point
├── anime_icon.ico            # Official High-Res Anime Application Icon
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
│       └── 12_Custom_Wallpapers\
│
└── scripts\
    ├── anime_studio.py       # Master GUI Application & System Tray Host
    ├── anime_auto_engine.py  # 5-Second Transition Overlay & Win32 API Engine
    ├── anime_settings.py     # Configuration, Conversion & Startup Manager
    └── stop_anime.py         # Emergency Process & Audio Termination Script
```

---
*Created with ❤️ for ultimate anime pair-programming and desktop aesthetics.*

