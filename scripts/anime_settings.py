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
    "mode": "local",
    "interval_minutes": 10,
    "sources": {
        "wallhaven": True,
        "konachan": True,
        "reddit": False,
        "pinterest_manual": False
    },
    "interval_value": 30,
    "interval_unit": "seconds",
    "interval_seconds": 30,
    "last_change_timestamp": time.time(),
    "next_change_timestamp": time.time() + 30,
    "song_mode": "mute",
    "specific_song": "one_piece_overtaken.mp3",
    "anime_filter": "all",
    "show_visual_transition": False,
    "transition_duration": 5,
    "play_full_song": False,
    "sound_enabled": False,
    "auto_mode_enabled": True,
    "run_at_startup": False,
    "minimize_to_tray_on_close": False,
    "favorites": [],
    "history": []
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
        if settings.get("mode") == "cloud":
            interval_seconds = settings.get("interval_minutes", 10) * 60
        else:
            interval_seconds = settings.get("interval_seconds", 30)
    settings["last_change_timestamp"] = now
    settings["next_change_timestamp"] = now + interval_seconds
    save_settings(settings)
    return settings


# ==============================================================================
# FAVORITES & BOOKMARKS SYSTEM
# ==============================================================================

def get_favorites():
    settings = load_settings()
    favs = settings.get("favorites", [])
    valid = []
    for p in favs:
        if p and os.path.exists(p):
            valid.append(os.path.abspath(p))
    return valid

def add_favorite(path):
    if not path or not os.path.exists(path):
        return False
    abs_p = os.path.abspath(path)
    settings = load_settings()
    favs = settings.get("favorites", [])
    if abs_p not in favs:
        favs.append(abs_p)
        settings["favorites"] = favs
        save_settings(settings)
    return True

def remove_favorite(path):
    if not path:
        return False
    abs_p = os.path.abspath(path)
    settings = load_settings()
    favs = settings.get("favorites", [])
    changed = False
    new_favs = []
    for p in favs:
        if os.path.abspath(p) == abs_p:
            changed = True
        else:
            new_favs.append(p)
    if changed:
        settings["favorites"] = new_favs
        save_settings(settings)
    return True

def is_favorite(path):
    if not path:
        return False
    abs_p = os.path.abspath(path)
    settings = load_settings()
    favs = [os.path.abspath(p) for p in settings.get("favorites", []) if p]
    return abs_p in favs

def toggle_favorite(path):
    if is_favorite(path):
        remove_favorite(path)
        return False
    else:
        add_favorite(path)
        return True


# ==============================================================================
# DESKTOP WALLPAPER HISTORY & UNDO
# ==============================================================================

def get_history():
    settings = load_settings()
    hist = settings.get("history", [])
    return [os.path.abspath(p) for p in hist if p and os.path.exists(p)]

def push_history(path):
    if not path or not os.path.exists(path):
        return
    abs_p = os.path.abspath(path)
    settings = load_settings()
    hist = settings.get("history", [])
    if hist and os.path.abspath(hist[-1]) == abs_p:
        return
    hist.append(abs_p)
    if len(hist) > 50:
        hist = hist[-50:]
    settings["history"] = hist
    save_settings(settings)

def pop_history():
    """Pops the current wallpaper and returns the previous one for instant 1-click undo."""
    settings = load_settings()
    hist = settings.get("history", [])
    if len(hist) >= 2:
        hist.pop()  # remove currently active
        prev = hist[-1]
        settings["history"] = hist
        save_settings(settings)
        if os.path.exists(prev):
            return prev
    elif len(hist) == 1 and os.path.exists(hist[0]):
        return hist[0]
    return None

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
