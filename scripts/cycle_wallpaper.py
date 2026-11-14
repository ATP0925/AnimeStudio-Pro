import os
import ctypes
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLPAPER_DIR = os.path.join(BASE_DIR, "wallpapers")
STATE_FILE = os.path.join(BASE_DIR, "current_wallpaper.txt")

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

def get_wallpapers():
    valid_exts = (".png", ".jpg", ".jpeg")
    files = [os.path.join(WALLPAPER_DIR, f) for f in os.listdir(WALLPAPER_DIR) if f.lower().endswith(valid_exts)]
    files.sort()
    return files

def set_wallpaper(path):
    ret = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return ret == 1

def cycle():
    wallpapers = get_wallpapers()
    if not wallpapers:
        print("No wallpapers found!")
        return None
    
    current_idx = 0
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                last_path = f.read().strip()
            if last_path in wallpapers:
                current_idx = (wallpapers.index(last_path) + 1) % len(wallpapers)
        except Exception:
            current_idx = 0
            
    chosen = wallpapers[current_idx]
    if set_wallpaper(chosen):
        with open(STATE_FILE, "w") as f:
            f.write(chosen)
        name = os.path.basename(chosen)
        print(f"Applied wallpaper: {name}")
        return chosen
    else:
        print("Failed to apply wallpaper.")
        return None

if __name__ == "__main__":
    cycle()
