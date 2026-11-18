import sys
import os
import time
import unittest.mock as mock
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import cloud_sources
import anime_settings
import anime_auto_engine

results = {}

print("====================================================")
print("        ANIME STUDIO PRO — STEP 6 TEST SUITE        ")
print("====================================================")

# TEST 1: Wallhaven gives a URL
print("\n[TEST 1] Wallhaven URL Fetch...")
try:
    wh_url = cloud_sources.get_wallhaven_wallpaper()
    if wh_url and wh_url.startswith("http"):
        print(f" -> Wallhaven URL: {wh_url}")
        results["1. Wallhaven gives a URL"] = "PASS"
    else:
        print(f" -> Wallhaven returned: {wh_url}")
        results["1. Wallhaven gives a URL"] = "FAIL"
except Exception as e:
    print(f" -> Wallhaven error: {e}")
    results["1. Wallhaven gives a URL"] = "FAIL"

# TEST 2: Konachan gives a URL
print("\n[TEST 2] Konachan URL Fetch (SFW Safe, Landscape >=1920x1080)...")
try:
    kc_url = cloud_sources.get_konachan_wallpaper()
    if kc_url and kc_url.startswith("http"):
        print(f" -> Konachan URL: {kc_url}")
        results["2. Konachan gives a URL"] = "PASS"
    else:
        print(f" -> Konachan returned: {kc_url}")
        results["2. Konachan gives a URL"] = "FAIL"
except Exception as e:
    print(f" -> Konachan error: {e}")
    results["2. Konachan gives a URL"] = "FAIL"

# TEST 3: Reddit gives a URL (or handles 403 gracefully without crash)
print("\n[TEST 3] Reddit URL Fetch / SFW Endpoint handling...")
try:
    rd_url = cloud_sources.get_reddit_wallpaper()
    print(f" -> Reddit returned: {rd_url}")
    results["3. Reddit gives a URL (handled without crash)"] = "PASS"
except Exception as e:
    print(f" -> Reddit crashed: {e}")
    results["3. Reddit gives a URL (handled without crash)"] = "FAIL"

# TEST 4: Wallpaper really changes on the desktop twice in a row (alternate filenames)
print("\n[TEST 4] Alternate Filename Wallpaper Changes (wp_a.jpg <-> wp_b.jpg)...")
try:
    url_a = cloud_sources.get_wallhaven_wallpaper()
    res_a = cloud_sources.set_wallpaper_from_url(url_a)
    info_a = cloud_sources.get_last_streamed_info()
    path_a = info_a["path"]
    dims_a = info_a["dimensions"]
    print(f" -> 1st Change: {res_a} | Path: {path_a} | Dim: {dims_a}")

    time.sleep(1)
    url_b = cloud_sources.get_konachan_wallpaper()
    res_b = cloud_sources.set_wallpaper_from_url(url_b)
    info_b = cloud_sources.get_last_streamed_info()
    path_b = info_b["path"]
    dims_b = info_b["dimensions"]
    print(f" -> 2nd Change: {res_b} | Path: {path_b} | Dim: {dims_b}")

    if res_a and res_b and path_a != path_b and os.path.exists(path_a) and os.path.exists(path_b):
        print(f" -> Alternate slots confirmed: {os.path.basename(path_a)} != {os.path.basename(path_b)}")
        results["4. Wallpaper changes twice with alternate filenames"] = "PASS"
    else:
        results["4. Wallpaper changes twice with alternate filenames"] = "FAIL"
except Exception as e:
    print(f" -> Alternate test error: {e}")
    results["4. Wallpaper changes twice with alternate filenames"] = "FAIL"

# TEST 5: With internet OFF, app does not crash and keeps old wallpaper
print("\n[TEST 5] Internet OFF Simulation (Zero Crash & Keep Old Wallpaper)...")
try:
    with mock.patch("requests.get", side_effect=requests.exceptions.ConnectionError("Network unreachable")):
        # Test cloud_sources directly
        cs_res = cloud_sources.next_wallpaper({"wallhaven": True, "konachan": True, "reddit": True})
        print(f" -> cloud_sources.next_wallpaper returned: {cs_res} (Expected False)")

        # Test engine dispatch
        cloud_settings = anime_settings.load_settings()
        cloud_settings["mode"] = "cloud"
        wp, meta, song = anime_auto_engine.change_wallpaper_now(settings=cloud_settings, force=True)
        print(f" -> change_wallpaper_now returned: wp={wp}, meta={meta}, song={song} (Expected None)")

        if cs_res is False and wp is None:
            results["5. Internet OFF keeps old wallpaper without crash"] = "PASS"
        else:
            results["5. Internet OFF keeps old wallpaper without crash"] = "FAIL"
except Exception as e:
    print(f" -> Internet OFF test crashed: {e}")
    results["5. Internet OFF keeps old wallpaper without crash"] = "FAIL"

# TEST 6: Local mode still works
print("\n[TEST 6] Local Mode Regression Test...")
try:
    local_settings = anime_settings.load_settings()
    local_settings["mode"] = "local"
    wp_local, meta_local, song_local = anime_auto_engine.change_wallpaper_now(settings=local_settings, force=True)
    print(f" -> Local WP: {wp_local}")
    print(f" -> Local Meta: {meta_local.get('title')} ({meta_local.get('char')})")
    print(f" -> Local Audio: {song_local}")

    if wp_local and os.path.exists(wp_local) and meta_local:
        results["6. Local mode still works"] = "PASS"
    else:
        results["6. Local mode still works"] = "FAIL"
except Exception as e:
    print(f" -> Local mode error: {e}")
    results["6. Local mode still works"] = "FAIL"

print("\n====================================================")
print("                 FINAL RESULTS MATRIX               ")
print("====================================================")
for k, v in results.items():
    print(f"[{v}] {k}")
print("====================================================")
