import os
import urllib.request
import urllib.parse
import json
import concurrent.futures

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_WP_DIR = os.path.join(BASE_DIR, "wallpapers", "collection")
os.makedirs(BASE_WP_DIR, exist_ok=True)

CATEGORIES = [
    {"folder": "01_Jujutsu_Kaisen", "wh_q": "jujutsu kaisen", "tag": "jujutsu_kaisen"},
    {"folder": "02_Demon_Slayer", "wh_q": "demon slayer kimetsu no yaiba", "tag": "kimetsu_no_yaiba"},
    {"folder": "03_One_Piece", "wh_q": "one piece luffy", "tag": "one_piece"},
    {"folder": "04_Attack_on_Titan", "wh_q": "attack on titan", "tag": "shingeki_no_kyojin"},
    {"folder": "05_Naruto_Shippuden", "wh_q": "naruto shippuden itachi", "tag": "naruto"},
    {"folder": "06_Frieren", "wh_q": "frieren", "tag": "sousou_no_frieren"},
    {"folder": "07_Fate_Series", "wh_q": "fate stay night", "tag": "fate/stay_night"},
    {"folder": "08_Cyberpunk_Edgerunners", "wh_q": "cyberpunk edgerunners", "tag": "cyberpunk:_edgerunners"},
    {"folder": "09_Studio_Ghibli", "wh_q": "studio ghibli", "tag": "studio_ghibli"},
    {"folder": "10_Neo_Tokyo_Aesthetic", "wh_q": "anime aesthetic scenery", "tag": "scenery"}
]

def fetch_image_urls(wh_q, tag, limit=12):
    urls = []
    # Wallhaven
    try:
        url = f"https://wallhaven.cc/api/v1/search?q={urllib.parse.quote(wh_q)}&categories=110&purity=100&sorting=toplist"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode('utf-8'))
            for item in data.get('data', [])[:limit]:
                urls.append(item['path'])
    except Exception:
        pass

    # Konachan
    try:
        url = f"https://konachan.net/post.json?tags={urllib.parse.quote(tag)}&limit={limit}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode('utf-8'))
            for item in data:
                u = item.get('file_url')
                if u and item.get('width', 0) >= item.get('height', 0):
                    urls.append(u)
    except Exception:
        pass

    return list(dict.fromkeys(urls))[:12]

def download_one(url, dest_path):
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read()
            with open(dest_path, "wb") as f:
                f.write(content)
        return True
    except Exception:
        return False

download_tasks = []
print("Gathering top anime wallpaper URLs...")
for cat in CATEGORIES:
    cat_dir = os.path.join(BASE_WP_DIR, cat["folder"])
    os.makedirs(cat_dir, exist_ok=True)
    urls = fetch_image_urls(cat["wh_q"], cat["tag"], limit=10)
    for i, u in enumerate(urls):
        ext = os.path.splitext(u)[1].split('?')[0]
        if not ext or ext.lower() not in ('.jpg', '.png', '.jpeg'):
            ext = '.jpg'
        dest = os.path.join(cat_dir, f"{cat['folder']}_{i+1:02d}{ext}")
        download_tasks.append((u, dest))

print(f"Total target files to download: {len(download_tasks)}. Starting parallel threads...")

success = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(download_one, u, p) for u, p in download_tasks]
    for f in concurrent.futures.as_completed(futures):
        if f.result():
            success += 1

print(f"Parallel download complete! Successfully saved {success} wallpapers.")

