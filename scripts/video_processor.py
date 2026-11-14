import os
import sys
import json
import urllib.request
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(BASE_DIR, "videos", "transitions")
STILLS_DIR = os.path.join(BASE_DIR, "wallpapers", "collection", "13_Live_Anime_Stills")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(STILLS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

def extract_frames_from_video(video_path, max_frames=3):
    """Uses ffmpeg to extract crisp, high-resolution frames from video into STILLS_DIR."""
    if not os.path.exists(video_path):
        return []

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    output_pattern = os.path.join(STILLS_DIR, f"{base_name}_frame_%02d.png")

    # Extract 1 frame every 2 seconds, up to max_frames
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", "fps=0.5,scale=3840:-1:flags=lanczos",  # Scale up to 4K width with high-quality lanczos
        "-vframes", str(max_frames),
        "-q:v", "2",
        output_pattern
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        extracted = [
            os.path.join(STILLS_DIR, f)
            for f in os.listdir(STILLS_DIR)
            if f.startswith(base_name) and f.endswith(".png")
        ]
        return extracted
    except Exception as e:
        print(f"Frame extraction error on {base_name}: {e}")
        return []

def download_pixabay_anime_videos(api_key, count=15):
    """Fetches anime video loops from Pixabay API and extracts 4K wallpaper frames."""
    if not api_key:
        print("[!] No Pixabay API key provided.")
        return 0

    url = f"https://pixabay.com/api/videos/?key={api_key}&q=anime&video_type=animation&per_page={count}"
    req = urllib.request.Request(url, headers=HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        hits = data.get("hits", [])
        print(f"[✓] Pixabay returned {len(hits)} anime video hits!")

        downloaded_count = 0
        for i, hit in enumerate(hits):
            videos = hit.get("videos", {})
            # Pick highest available resolution: large -> medium -> small
            chosen_video = videos.get("large") or videos.get("medium") or videos.get("small")
            if not chosen_video:
                continue

            v_url = chosen_video.get("url")
            v_id = hit.get("id", i)
            tags = hit.get("tags", "anime_loop").replace(" ", "_").replace(",", "")[:30]
            filename = f"pixabay_{v_id}_{tags}.mp4"
            target_path = os.path.join(VIDEOS_DIR, filename)

            if not os.path.exists(target_path):
                print(f"[*] Downloading [{i+1}/{len(hits)}]: {filename}...")
                dl_req = urllib.request.Request(v_url, headers=HEADERS)
                with urllib.request.urlopen(dl_req, timeout=30) as src, open(target_path, "wb") as dst:
                    dst.write(src.read())
                downloaded_count += 1
            else:
                print(f"[✓] Already downloaded: {filename}")

            # Extract 4K wallpapers from this video
            frames = extract_frames_from_video(target_path, max_frames=3)
            print(f"    -> Extracted {len(frames)} 4K wallpaper frames into gallery.")

        return downloaded_count

    except Exception as e:
        print(f"[!] Pixabay API fetch failed: {e}")
        return 0

def process_all_existing_videos():
    """Scans VIDEOS_DIR and extracts 4K wallpaper frames for any videos without frames yet."""
    total_extracted = 0
    videos = [
        os.path.join(VIDEOS_DIR, f)
        for f in os.listdir(VIDEOS_DIR)
        if f.lower().endswith(('.mp4', '.webm', '.mkv', '.avi'))
    ]

    for v in videos:
        base_name = os.path.splitext(os.path.basename(v))[0]
        existing = [f for f in os.listdir(STILLS_DIR) if f.startswith(base_name)]
        if not existing:
            frames = extract_frames_from_video(v, max_frames=3)
            total_extracted += len(frames)
            print(f"[✓] Processed {os.path.basename(v)} -> {len(frames)} 4K frames extracted.")

    return total_extracted

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isalnum() and len(sys.argv[1]) > 10:
        key = sys.argv[1]
        print(f"Connecting to Pixabay with API Key...")
        download_pixabay_anime_videos(key)
    else:
        print("Scanning existing videos in videos/transitions...")
        c = process_all_existing_videos()
        print(f"Total new 4K frames extracted: {c}")

