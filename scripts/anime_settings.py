import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

UNIT_MULTIPLIERS = {
    "seconds": 1,
    "minutes": 60,
    "hours": 3600,
    "days": 86400,
    "weeks": 604800,
    "months": 2592000,   # 30 days
    "years": 31536000    # 365 days
}

DEFAULT_SETTINGS = {
    "interval_value": 30,
    "interval_unit": "seconds",
    "interval_seconds": 30,
    "last_change_timestamp": time.time(),
    "next_change_timestamp": time.time() + 30,
    "song_mode": "match_anime",
    "specific_song": "one_piece_overtaken.mp3",
    "anime_filter": "all",
    "show_visual_transition": True,
    "transition_duration": 5,
    "play_full_song": False,
    "sound_enabled": True,
    "auto_mode_enabled": True,
    "run_at_startup": False
}

def convert_to_seconds(value, unit):
    mult = UNIT_MULTIPLIERS.get(unit.lower(), 1)
    try:
        val = float(value)
        if val <= 0:
            val = 5
        return int(val * mult)
    except:
        return 30

def format_seconds_to_human(seconds):
    if seconds <= 0:
        return "0s"
    s = int(seconds)
    years = s // 31536000
    s %= 31536000
    months = s // 2592000
    s %= 2592000
    days = s // 86400
    s %= 86400
    hours = s // 3600
    s %= 3600
    minutes = s // 60
    secs = s % 60

    parts = []
    if years > 0:
        parts.append(f"{years} yr" + ("s" if years > 1 else ""))
    if months > 0:
        parts.append(f"{months} mo" + ("s" if months > 1 else ""))
    if days > 0:
        parts.append(f"{days} d")
    if hours > 0 and len(parts) < 2:
        parts.append(f"{hours} h")
    if minutes > 0 and len(parts) < 2:
        parts.append(f"{minutes} m")
    if secs > 0 and len(parts) < 2:
        parts.append(f"{secs} s")

    return " ".join(parts[:2]) if parts else "0s"

def load_settings():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def update_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings

def register_next_change(interval_seconds=None):
    settings = load_settings()
    now = time.time()
    if interval_seconds is None:
        interval_seconds = settings.get("interval_seconds", 30)
    settings["last_change_timestamp"] = now
    settings["next_change_timestamp"] = now + interval_seconds
    save_settings(settings)
    return settings

def set_windows_startup(enable=True):
    startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_path = os.path.join(startup_dir, "Anime_Auto_HUD.lnk")
    if enable:
        try:
            import win32com.client
            ws = win32com.client.Dispatch("WScript.Shell")
            sc = ws.CreateShortcut(shortcut_path)
            sc.TargetPath = sys.executable.replace("python.exe", "pythonw.exe")
            sc.Arguments = f'"{os.path.join(SCRIPTS_DIR, "anime_hud.py")}"'
            sc.WorkingDirectory = SCRIPTS_DIR
            sc.Description = "Anime Auto HUD & Scheduled Wallpaper Changer"
            sc.Save()
            update_setting("run_at_startup", True)
            return True
        except Exception as e:
            print("Error creating startup shortcut:", e)
            return False
    else:
        if os.path.exists(shortcut_path):
            try:
                os.remove(shortcut_path)
            except:
                pass
        update_setting("run_at_startup", False)
        return True

if __name__ == "__main__":
    print("Loaded settings:", load_settings())
