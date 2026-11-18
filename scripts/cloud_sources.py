"""
Anime Studio Pro - Cloud Stream Sources Module
Author: Pratik Atpadkar (@ATP0925)
Zero-Disk Stream Engine for Online Anime Wallpapers.
"""

import os
import sys
import time
import json
import random
import ctypes
import tempfile
import requests
from PIL import Image

# Global constants per rules
HEADERS = {"User-Agent": "AnimeStudioPro/1.0"}
NETWORK_TIMEOUT = 10
MIN_IMAGE_BYTES = 100 * 1024        # 100 KB
MAX_IMAGE_BYTES = 25 * 1024 * 1024  # 25 MB

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")
SLOT_TRACKER_FILE = os.path.join(tempfile.gettempdir(), "anime_wp_current_slot.txt")

# In-memory history of last 20 used URLs (never repeated)
_RECENT_URLS = []
_LAST_API_CALL_TIME = 0.0

# Information about the last successfully streamed wallpaper
_LAST_STREAMED_INFO = {
    "path": None,
    "url": None,
    "source": None,
    "dimensions": (0, 0)
}


def _read_settings():
    """Safely loads settings without crashing."""
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _rate_limit_wait():
    """Enforces at least 3 seconds between outgoing API calls."""
    global _LAST_API_CALL_TIME
    now = time.time()
    elapsed = now - _LAST_API_CALL_TIME
    if elapsed < 3.0:
        time.sleep(3.0 - elapsed)
    _LAST_API_CALL_TIME = time.time()


# =====================================================================
# STEP 1: SOURCES IMPLEMENTATION (SFW, Landscape, Non-crashing)
# =====================================================================

def get_wallhaven_wallpaper():
    """
    Source: Wallhaven API
    SFW only, anime category, landscape 16:9, width >= 1920.
    """
    url = "https://wallhaven.cc/api/v1/search"
    params = {
        "q": "anime",
        "categories": "010",
        "purity": "100",
        "atleast": "1920x1080",
        "ratios": "16x9",
        "sorting": "random"
    }
    
    settings = _read_settings()
    api_key = settings.get("wallhaven_api_key") or settings.get("api_keys", {}).get("wallhaven")
    if api_key:
        params["apikey"] = api_key

    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=NETWORK_TIMEOUT)
        if r.status_code == 200:
            data = r.json().get("data", [])
            valid_candidates = []
            for item in data:
                path = item.get("path")
                dim_x = item.get("dimension_x", 0)
                dim_y = item.get("dimension_y", 0)
                if path:
                    # Enforce landscape requirement: width >= 1920, height >= 1080, width > height
                    if dim_x >= 1920 and dim_y >= 1080 and dim_x > dim_y:
                        valid_candidates.append(path)
                    elif dim_x == 0 and dim_y == 0:
                        valid_candidates.append(path)
            
            if valid_candidates:
                return random.choice(valid_candidates)
            elif data:
                first = data[0].get("path")
                if first:
                    return first
            return None
        else:
            print(f"Wallhaven error: Status {r.status_code} - {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Wallhaven error: {e}")
        return None


def get_konachan_wallpaper():
    """
    Source: Konachan API (SFW rating:safe)
    Landscape only: width >= 1920, height >= 1080, width > height.
    """
    url = "https://konachan.net/post.json"
    params = {
        "tags": "rating:safe order:random width:>=1920",
        "limit": 20
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=NETWORK_TIMEOUT)
        if r.status_code == 200:
            posts = r.json()
            if not isinstance(posts, list):
                print(f"Konachan error: Unexpected response format: {r.text[:200]}")
                return None
            valid = []
            for p in posts:
                # SFW only: rating must strictly be safe ('s')
                if p.get("rating") != "s":
                    continue
                w = p.get("width", 0)
                h = p.get("height", 0)
                file_url = p.get("file_url")
                if file_url and w >= 1920 and h >= 1080 and w > h:
                    if file_url.startswith("//"):
                        file_url = "https:" + file_url
                    valid.append(file_url)

            if valid:
                return random.choice(valid)
            return None
        else:
            print(f"Konachan error: Status {r.status_code} - {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Konachan error: {e}")
        return None


def get_reddit_wallpaper():
    """
    Source: Reddit (r/Animewallpaper)
    SFW only (skip over_18), only .jpg/.jpeg/.png, landscape preview >= 1920x1080.
    """
    url = "https://www.reddit.com/r/Animewallpaper/top.json?t=week&limit=50"
    try:
        r = requests.get(url, headers=HEADERS, timeout=NETWORK_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            children = data.get("data", {}).get("children", [])
            valid = []
            for child in children:
                post = child.get("data", {})
                if post.get("over_18", False):
                    continue
                img_url = post.get("url", "")
                if not any(img_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                    continue
                # Preview dimension check
                preview_images = post.get("preview", {}).get("images", [])
                if preview_images:
                    source = preview_images[0].get("source", {})
                    pw = source.get("width", 0)
                    ph = source.get("height", 0)
                    if pw >= 1920 and ph >= 1080 and pw > ph:
                        valid.append(img_url)
                else:
                    valid.append(img_url)
            if valid:
                return random.choice(valid)
            return None
        else:
            print(f"Reddit error: Status {r.status_code} - {r.text[:200]}")
            return None
    except Exception as e:
        print(f"Reddit error: {e}")
        return None


SOURCES = {
    "wallhaven": get_wallhaven_wallpaper,
    "konachan": get_konachan_wallpaper,
    "reddit": get_reddit_wallpaper
}


# =====================================================================
# STEP 2: PINTEREST (MANUAL ONLY - EXPERIMENTAL)
# =====================================================================

def set_from_pinterest_url(url):
    """
    Experimental Manual Pinterest Wallpaper Setter.
    - Replaces /236x/, /474x/, /564x/, /736x/ with /originals/
    - Tries .jpg, .png, .webp until status 200
    - If vertical (height > width), warns and rejects.
    """
    if not url:
        print("Pinterest error: Empty URL provided.")
        return False

    transformed = url
    for size_token in ["/236x/", "/474x/", "/564x/", "/736x/"]:
        if size_token in transformed:
            transformed = transformed.replace(size_token, "/originals/")

    # Strip existing extension
    base_no_ext = transformed
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        if base_no_ext.lower().endswith(ext):
            base_no_ext = base_no_ext[:-len(ext)]
            break

    working_url = None
    for test_ext in [".jpg", ".png", ".webp"]:
        candidate_url = base_no_ext + test_ext
        try:
            r = requests.head(candidate_url, headers=HEADERS, timeout=NETWORK_TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                working_url = candidate_url
                break
        except Exception:
            continue

    if not working_url:
        # Fall back to testing direct transformed URL
        try:
            r = requests.head(transformed, headers=HEADERS, timeout=NETWORK_TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                working_url = transformed
        except Exception:
            pass

    if not working_url:
        print(f"Pinterest error: Could not resolve valid high-resolution image at {url}")
        return False

    # Download to verify aspect ratio before setting
    return set_wallpaper_from_url(working_url, is_pinterest=True)


# =====================================================================
# STEP 3: DOWNLOAD AND SET WALLPAPER
# =====================================================================

def _get_next_temp_slot():
    """
    Alternates between %TEMP%/wp_a.jpg and %TEMP%/wp_b.jpg.
    Windows does not refresh the desktop wallpaper if the filename stays the same.
    """
    temp_dir = tempfile.gettempdir()
    path_a = os.path.join(temp_dir, "wp_a.jpg")
    path_b = os.path.join(temp_dir, "wp_b.jpg")

    current_slot = "b"
    if os.path.exists(SLOT_TRACKER_FILE):
        try:
            with open(SLOT_TRACKER_FILE, "r", encoding="utf-8") as f:
                current_slot = f.read().strip()
        except Exception:
            current_slot = "b"

    if current_slot == "a":
        next_slot = "b"
        next_path = path_b
    else:
        next_slot = "a"
        next_path = path_a

    return next_path, next_slot


def set_wallpaper_from_url(url, is_pinterest=False):
    """
    Downloads image to %TEMP%, alternates between wp_a.jpg and wp_b.jpg,
    validates file size (100KB - 25MB) and dimensions (width >= 1920, height >= 1080, width > height),
    and applies it via Windows SystemParametersInfoW.
    """
    if not url:
        return False

    target_path, next_slot = _get_next_temp_slot()

    try:
        r = requests.get(url, headers=HEADERS, timeout=NETWORK_TIMEOUT, stream=True)
        if r.status_code != 200:
            print(f"Download error: Status {r.status_code} - {r.text[:200]}")
            return False

        with open(target_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)

        # 2. Check file size: between 100 KB and 25 MB
        file_size = os.path.getsize(target_path)
        if file_size < MIN_IMAGE_BYTES or file_size > MAX_IMAGE_BYTES:
            print(f"Validation failed: File size {file_size} bytes out of bounds (100KB - 25MB).")
            if os.path.exists(target_path):
                os.remove(target_path)
            return False

        # Open with Pillow to confirm valid image and landscape
        with Image.open(target_path) as img:
            width, height = img.size
            if is_pinterest and height > width:
                print(f"Warning: Pinterest image is vertical ({width}x{height}). Landscape wallpaper required.")
                if os.path.exists(target_path):
                    os.remove(target_path)
                return False

            if width < 1920 or height < 1080 or width <= height:
                print(f"Validation failed: Image is {width}x{height}. Required: >=1920x1080 and landscape (width > height).")
                if os.path.exists(target_path):
                    os.remove(target_path)
                return False

        # 3. Set the wallpaper via Windows API
        abs_path = os.path.abspath(target_path)
        ret = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        if ret == 1 or ret != 0:
            # Update slot tracker
            try:
                with open(SLOT_TRACKER_FILE, "w", encoding="utf-8") as f:
                    f.write(next_slot)
            except Exception:
                pass

            _LAST_STREAMED_INFO["path"] = abs_path
            _LAST_STREAMED_INFO["url"] = url
            _LAST_STREAMED_INFO["dimensions"] = (width, height)
            return True
        else:
            print("SystemParametersInfoW returned 0 (failed to set desktop wallpaper).")
            return False

    except Exception as e:
        print(f"set_wallpaper_from_url exception: {e}")
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except Exception:
                pass
        return False


# =====================================================================
# STEP 4: FALLBACK CHAIN
# =====================================================================

def next_wallpaper(enabled_sources=None):
    """
    Fallback chain:
    Tries sources in order: wallhaven -> konachan -> reddit.
    First source that returns a valid URL and passes set_wallpaper_from_url() wins.
    If all fail, prints 'all sources failed' and returns False.
    Maintains last 20 used URLs and enforces 3s rate-limit between API calls.
    """
    global _RECENT_URLS

    if enabled_sources is None:
        settings = _read_settings()
        enabled_sources = settings.get("sources", {
            "wallhaven": True,
            "konachan": True,
            "reddit": False,
            "pinterest_manual": False
        })

    order = ["wallhaven", "konachan", "reddit"]

    for source_name in order:
        # Check if source is enabled
        if not enabled_sources.get(source_name, False):
            continue

        func = SOURCES.get(source_name)
        if not func:
            continue

        # Rate-limit safety: wait at least 3 seconds between API calls
        _rate_limit_wait()

        url = func()
        if not url:
            continue

        # Avoid repeating the last 20 used URLs
        if url in _RECENT_URLS:
            continue

        success = set_wallpaper_from_url(url)
        if success:
            _RECENT_URLS.append(url)
            if len(_RECENT_URLS) > 20:
                _RECENT_URLS.pop(0)
            _LAST_STREAMED_INFO["source"] = source_name
            return True

    print("all sources failed")
    return False


def get_last_streamed_info():
    """Returns metadata for the active streamed wallpaper."""
    return _LAST_STREAMED_INFO.copy()
