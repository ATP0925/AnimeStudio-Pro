import os
import sys
import psutil
import ctypes
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
PID_FILE = os.path.join(CONFIG_DIR, "app.pid")
RESTORE_FLAG = os.path.join(CONFIG_DIR, "restore_signal.flag")

def kill_everything_anime():
    print("=" * 60)
    print(" 🛑 ANIME STUDIO PRO: EMERGENCY KILL SWITCH INITIATED")
    print("=" * 60)

    # 1. Instantly mute & close all Windows MCI audio devices
    try:
        mci = ctypes.windll.winmm.mciSendStringW
        mci("stop anime_auto_sound", None, 0, None)
        mci("close anime_auto_sound", None, 0, None)
        mci("stop all", None, 0, None)
        mci("close all", None, 0, None)
        print("[✓] All Windows audio devices stopped and closed.")
    except Exception as e:
        print("[!] Audio close error:", e)

    # 2. Persist STOPPED state in settings.json
    try:
        if os.path.exists(SETTINGS_FILE):
            import json
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["auto_mode_enabled"] = False
            data["sound_enabled"] = False
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("[✓] settings.json saved: auto_mode_enabled=False, sound_enabled=False")
    except Exception as e:
        print("[!] Settings save error:", e)

    # 3. Terminate all related processes
    current_pid = os.getpid()
    parent_pid = os.getppid() if hasattr(os, 'getppid') else None
    target_keywords = [
        'anime_hud', 'anime_auto_engine',
        'anime_control_center', 'anime_engine', 'animestudio',
        'anime_studio', 'transition_overlay', 'cycle_wallpaper'
    ]

    killed_count = 0
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            pid = p.info['pid']
            if pid == current_pid or pid == parent_pid:
                continue

            cmdline = ' '.join(p.info['cmdline'] or []).lower()
            if 'stop_anime' in cmdline:
                continue

            is_anime_related = any(k in cmdline for k in target_keywords)

            if is_anime_related:
                print(f"[!] Force-killing PID {pid} ({p.info['name']})...")
                try:
                    p.kill()
                except:
                    pass
                try:
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                except:
                    pass
                killed_count += 1
        except Exception:
            pass

    # 4. Cleanup lock and signal files
    for fl in [PID_FILE, RESTORE_FLAG]:
        if os.path.exists(fl):
            try:
                os.remove(fl)
                print(f"[✓] Removed {os.path.basename(fl)}")
            except:
                pass

    print(f"\n[✓] Finished. {killed_count} processes terminated.")
    print("=" * 60)
    print(" ALL ANIME BACKGROUND PROCESSES & SONGS ARE 100% STOPPED.")
    print("=" * 60)

if __name__ == "__main__":
    kill_everything_anime()
