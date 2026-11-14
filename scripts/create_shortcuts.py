import os
import sys
import subprocess

def create_all_desktop_shortcuts(base_dir=None):
    if not base_dir:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    base_dir = os.path.abspath(base_dir)
    app_pyw = os.path.join(base_dir, "AnimeStudio.pyw")
    icon_path = os.path.join(base_dir, "anime_icon.ico")
    stop_script = os.path.join(base_dir, "scripts", "stop_anime.py")

    userprofile = os.environ.get("USERPROFILE", "")
    desktop_dirs = [
        os.path.join(userprofile, "Desktop"),
        os.path.join(userprofile, "OneDrive", "Desktop")
    ]

    valid_desktops = []
    for d in desktop_dirs:
        if d and os.path.exists(d) and d not in valid_desktops:
            valid_desktops.append(d)

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

    print(f"Target app: {app_pyw}")
    print(f"Python interpreter: {pythonw_exe}")

    icon_clause = f"$sc.IconLocation = '{icon_path},0';" if os.path.exists(icon_path) else ""

    for desk in valid_desktops:
        # 1. Anime Studio Shortcut (Use clean ASCII filename to avoid ?? unicode errors)
        shortcut_names = ["Anime Studio Pro.lnk", "🌸 Anime Studio.lnk"]
        for sc_name in shortcut_names:
            try:
                ps_code = f"""
$ws = New-Object -ComObject WScript.Shell;
$sc = $ws.CreateShortcut('{desk}\\{sc_name}');
$sc.TargetPath = '{pythonw_exe}';
$sc.Arguments = '"{app_pyw}"';
$sc.WorkingDirectory = '{base_dir}';
{icon_clause}
$sc.Description = 'Anime Studio Pro - 4K Wallpapers & Japanese Audio';
$sc.Save();
"""
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f" [✓] Created shortcut: {desk}\\{sc_name}")
            except Exception:
                pass

        # 2. STOP Anime Mode.bat
        stop_bat_names = ["STOP Anime Mode.bat", "🛑 STOP Anime Mode.bat"]
        for sb_name in stop_bat_names:
            try:
                sb_path = os.path.join(desk, sb_name)
                with open(sb_path, "w", encoding="ascii", errors="ignore") as f:
                    f.write(f'@echo off\ntitle Emergency Stop Anime Mode\necho Stopping Anime Studio Pro...\n"{sys.executable}" "{stop_script}"\nexit /b 0\n')
                print(f" [✓] Created stop script: {desk}\\{sb_name}")
            except Exception:
                pass

        # 3. Anime Hub folder
        hub_dir = os.path.join(desk, "🎌 Anime Hub")
        try:
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
            print(f" [✓] Created Anime Hub on: {desk}")
        except Exception:
            pass

    # Start Menu Programs
    try:
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            start_menu = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs\Anime Studio Pro")
            os.makedirs(start_menu, exist_ok=True)
            ps_sm = f"""
$ws = New-Object -ComObject WScript.Shell;
$sc = $ws.CreateShortcut('{start_menu}\\Anime Studio Pro.lnk');
$sc.TargetPath = '{pythonw_exe}';
$sc.Arguments = '"{app_pyw}"';
$sc.WorkingDirectory = '{base_dir}';
{icon_clause}
$sc.Save();
"""
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_sm], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(" [✓] Added to Windows Start Menu!")
    except Exception:
        pass

if __name__ == "__main__":
    bdir = sys.argv[1] if len(sys.argv) > 1 else None
    create_all_desktop_shortcuts(bdir)
