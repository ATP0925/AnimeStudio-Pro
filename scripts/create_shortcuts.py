import os
import sys
import subprocess
import shutil

def create_all_desktop_shortcuts(base_dir=None):
    if not base_dir:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app_pyw = os.path.join(base_dir, "AnimeStudio.pyw")
    icon_path = os.path.join(base_dir, "anime_icon.ico")
    stop_script = os.path.join(base_dir, "scripts", "stop_anime.py")

    # Find all desktop directories (Local user, OneDrive, etc.)
    userprofile = os.environ.get("USERPROFILE", "")
    desktop_dirs = [
        os.path.join(userprofile, "Desktop"),
        os.path.join(userprofile, "OneDrive", "Desktop")
    ]

    # Deduplicate and filter existing
    valid_desktops = []
    for d in desktop_dirs:
        if d and os.path.exists(d) and d not in valid_desktops:
            valid_desktops.append(d)

    # In case neither was found, fallback to standard desktop
    if not valid_desktops and userprofile:
        d = os.path.join(userprofile, "Desktop")
        os.makedirs(d, exist_ok=True)
        valid_desktops.append(d)

    # Resolve pythonw.exe path
    python_dir = os.path.dirname(sys.executable)
    pythonw_candidate = os.path.join(python_dir, "pythonw.exe")
    if os.path.exists(pythonw_candidate):
        pythonw_exe = pythonw_candidate
    else:
        pythonw_exe = sys.executable

    print(f"Creating shortcuts using target: {app_pyw}")
    print(f"Python interpreter: {pythonw_exe}")

    for desk in valid_desktops:
        try:
            # 1. 🌸 Anime Studio.lnk
            ps_code = f"""
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut('{desk}\\🌸 Anime Studio.lnk')
$sc.TargetPath = '{pythonw_exe}'
$sc.Arguments = '"{app_pyw}"'
$sc.WorkingDirectory = '{base_dir}'
$sc.IconLocation = '{icon_path},0'
$sc.Description = 'Anime Studio Pro - 4K Wallpapers & Japanese Audio'
$sc.Save()
"""
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_code], check=True, stdout=subprocess.DEVNULL)
            print(f" [✓] Created '🌸 Anime Studio' on: {desk}")

            # 2. 🛑 STOP Anime Mode.bat
            stop_bat = os.path.join(desk, "🛑 STOP Anime Mode.bat")
            with open(stop_bat, "w", encoding="ascii") as f:
                f.write(f'@echo off\ntitle Emergency Stop Anime Mode\necho Stopping Anime Studio Pro...\n"{sys.executable}" "{stop_script}"\nexit /b 0\n')
            print(f" [✓] Created '🛑 STOP Anime Mode.bat' on: {desk}")

            # 3. 🎌 Anime Hub folder
            hub_dir = os.path.join(desk, "🎌 Anime Hub")
            os.makedirs(hub_dir, exist_ok=True)
            portals = {
                "⚡ Marin Anime (Direct Unblocked - No VPN).url": "https://marin.moe",
                "⚡ Miruro Anime (HiAnime Alternative - 1080p).url": "https://miruro.to",
                "🎬 Crunchyroll (Official Anime Streaming).url": "https://www.crunchyroll.com",
                "📺 Muse Anime (Free Legal Streaming - YouTube).url": "https://www.youtube.com/@MuseIndia",
                "🌸 Lofi Anime Radio (Relaxing Study Beats).url": "https://www.youtube.com/watch?v=jfKfPfyJRdk"
            }
            for name, url in portals.items():
                p_path = os.path.join(hub_dir, name)
                with open(p_path, "w", encoding="utf-8") as pf:
                    pf.write(f"[InternetShortcut]\nURL={url}\n")
            print(f" [✓] Created '🎌 Anime Hub' on: {desk}")

        except Exception as e:
            print(f" [!] Error creating shortcuts in {desk}: {e}")

    # Also Start Menu
    try:
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            start_menu = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Anime Studio Pro")
            os.makedirs(start_menu, exist_ok=True)
            ps_sm = f"""
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut('{start_menu}\\🌸 Anime Studio.lnk')
$sc.TargetPath = '{pythonw_exe}'
$sc.Arguments = '"{app_pyw}"'
$sc.WorkingDirectory = '{base_dir}'
$sc.IconLocation = '{icon_path},0'
$sc.Save()
"""
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_sm], check=True, stdout=subprocess.DEVNULL)
            print(" [✓] Added to Windows Start Menu!")
    except Exception as e:
        pass

if __name__ == "__main__":
    bdir = sys.argv[1] if len(sys.argv) > 1 else None
    create_all_desktop_shortcuts(bdir)
