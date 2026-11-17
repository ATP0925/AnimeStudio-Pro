import os
import sys
import ctypes
import random
import time
import subprocess
import threading
import anime_settings

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLPAPER_DIR = os.path.join(BASE_DIR, "wallpapers")
COLLECTION_DIR = os.path.join(WALLPAPER_DIR, "collection")
SONGS_DIR = os.path.join(BASE_DIR, "audio", "viral_songs")
ORIGINAL_VOICES_DIR = os.path.join(BASE_DIR, "audio", "original")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
OVERLAY_SCRIPT = os.path.join(SCRIPTS_DIR, "transition_overlay.py")

ANIME_CATALOG = {
    "01_Jujutsu_Kaisen": {
        "title": "Jujutsu Kaisen",
        "char": "Satoru Gojo & Sukuna",
        "song_name": "Lost in Paradise (ALI feat. AKLO)",
        "audio_file": "jjk_lost_in_paradise.mp3",
        "voice_file": "original/gojo_domain_expansion.mp3"
    },
    "02_Demon_Slayer": {
        "title": "Demon Slayer: Kimetsu no Yaiba",
        "char": "Tanjiro Kamado & Zenitsu",
        "song_name": "Infinity Castle Epic Theme Drop",
        "audio_file": "demon_slayer_infinity_theme.mp3",
        "voice_file": "original/zenitsu_thunder_breathing.mp3"
    },
    "03_One_Piece": {
        "title": "One Piece",
        "char": "Monkey D. Luffy (Gear 5)",
        "song_name": "Overtaken (The Legendary Walk Theme)",
        "audio_file": "one_piece_overtaken.mp3",
        "voice_file": "original/luffy_gear5.mp3"
    },
    "04_Attack_on_Titan": {
        "title": "Attack on Titan",
        "char": "Eren Yeager & Levi Ackerman",
        "song_name": "Shinzou wo Sasageyo! (Linked Horizon)",
        "audio_file": "aot_shinzou_wo_sasageyo.mp3",
        "voice_file": "original/eren_tatakae.mp3"
    },
    "05_Naruto_Shippuden": {
        "title": "Naruto Shippuden",
        "char": "Naruto Uzumaki & Sasuke Uchiha",
        "song_name": "Silhouette (KANA-BOON)",
        "audio_file": "naruto_silhouette.mp3",
        "voice_file": "original/itachi_amaterasu.mp3"
    },
    "06_Frieren": {
        "title": "Frieren: Beyond Journey's End",
        "char": "Frieren & Fern",
        "song_name": "Zoltraak Climax Symphony",
        "audio_file": "frieren_zoltraak_climax.mp3",
        "voice_file": "original/frieren_zoltraak.mp3"
    },
    "07_Solo_Leveling": {
        "title": "Solo Leveling",
        "char": "Sung Jin-Woo (Shadow Monarch)",
        "song_name": "Climax Battle (Ultra Instinct Anthem)",
        "audio_file": "dbz_ultra_instinct.mp3",
        "voice_file": "dbz_ultra_instinct.mp3"
    },
    "08_Cyberpunk_Edgerunners": {
        "title": "Cyberpunk: Edgerunners",
        "char": "Lucy & David Martinez",
        "song_name": "I Really Want to Stay at Your House",
        "audio_file": "cyberpunk_stay_at_your_house.mp3",
        "voice_file": "original/edgerunners_moon.mp3"
    },
    "09_Studio_Ghibli": {
        "title": "Studio Ghibli Masterpieces",
        "char": "Spirited Away & Howl's Castle",
        "song_name": "Merry-Go-Round of Life (Joe Hisaishi)",
        "audio_file": "ghibli_merry_go_round.mp3",
        "voice_file": "ghibli_merry_go_round.mp3"
    },
    "10_Makoto_Shinkai": {
        "title": "Makoto Shinkai Universe",
        "char": "Your Name & Suzume",
        "song_name": "Unravel (Tokyo Ghoul Anthem)",
        "audio_file": "tokyo_ghoul_unravel.mp3",
        "voice_file": "tokyo_ghoul_unravel.mp3"
    },
    "11_Fate_Series": {
        "title": "Fate Series: Unlimited Blade Works",
        "char": "Saber Artoria & Archer",
        "song_name": "Climax Battle (Ultra Instinct Anthem)",
        "audio_file": "dbz_ultra_instinct.mp3",
        "voice_file": "original/saber_excalibur.mp3"
    },
    "12_Custom_Wallpapers": {
        "title": "Custom Personal Wallpapers",
        "char": "Your Personal Collection",
        "song_name": "Custom Anime Music",
        "audio_file": "one_piece_overtaken.mp3",
        "voice_file": "original/luffy_gear5.mp3"
    },
    "13_Live_Anime_Stills": {
        "title": "Live Anime Video Wallpapers",
        "char": "Extracted Anime Masterpieces",
        "song_name": "Cyberpunk - Stay at Your House",
        "audio_file": "cyberpunk_stay_at_your_house.mp3",
        "voice_file": "original/edgerunners_moon.mp3"
    }
}

def get_all_available_tracks():
    tracks = {
        "jjk_lost_in_paradise.mp3": "Jujutsu Kaisen - Lost in Paradise (Song)",
        "demon_slayer_infinity_theme.mp3": "Demon Slayer - Infinity Castle (Song)",
        "one_piece_overtaken.mp3": "One Piece - Overtaken Walk Theme (Song)",
        "aot_shinzou_wo_sasageyo.mp3": "Attack on Titan - Shinzou wo Sasageyo (Song)",
        "naruto_silhouette.mp3": "Naruto Shippuden - Silhouette (Song)",
        "frieren_zoltraak_climax.mp3": "Frieren - Zoltraak Climax Symphony (Song)",
        "dbz_ultra_instinct.mp3": "Climax Battle - Ultra Instinct Theme (Song)",
        "cyberpunk_stay_at_your_house.mp3": "Cyberpunk - Stay at Your House (Song)",
        "ghibli_merry_go_round.mp3": "Studio Ghibli - Merry-Go-Round of Life (Song)",
        "tokyo_ghoul_unravel.mp3": "Tokyo Ghoul - Unravel (Song)",
        "original/gojo_domain_expansion.mp3": "Gojo Satoru - 'Domain Expansion: Infinite Void' (Voice)",
        "original/sukuna_domain_expansion.mp3": "Ryomen Sukuna - 'Domain Expansion: Malevolent Shrine' (Voice)",
        "original/zenitsu_thunder_breathing.mp3": "Zenitsu - 'Thunder Breathing First Form' (Voice)",
        "original/rengoku_umai.mp3": "Rengoku - 'Set Your Heart Ablaze / Umai' (Voice)",
        "original/luffy_gear5.mp3": "Luffy - 'Gear 5 Drums of Liberation Laugh' (Voice)",
        "original/eren_tatakae.mp3": "Eren Yeager - 'Tatakae Fight' (Voice)",
        "original/itachi_amaterasu.mp3": "Itachi Uchiha - 'Amaterasu' (Voice)",
        "original/frieren_zoltraak.mp3": "Frieren - 'Zoltraak Destruction Magic' (Voice)",
        "original/saber_excalibur.mp3": "Saber Artoria - 'Excalibur' (Voice)",
        "original/edgerunners_moon.mp3": "Lucy & David - 'Take Me to the Moon' (Voice)"
    }

    # Discover any newly added user MP3s in viral_songs
    if os.path.exists(SONGS_DIR):
        for f in os.listdir(SONGS_DIR):
            if f.endswith('.mp3') and f not in tracks:
                clean_name = os.path.splitext(f)[0].replace('_', ' ').title()
                tracks[f] = f"User Audio - {clean_name}"

    return tracks

_SHUFFLE_QUEUE = []

def get_short_path(path):
    if not path or not os.path.exists(path):
        return path
    try:
        buf = ctypes.create_unicode_buffer(500)
        ret = ctypes.windll.kernel32.GetShortPathNameW(os.path.abspath(path), buf, 500)
        return buf.value if ret > 0 else os.path.abspath(path)
    except Exception:
        return os.path.abspath(path)

def get_next_category(filter_choice="all"):
    global _SHUFFLE_QUEUE
    if filter_choice and filter_choice != "all" and filter_choice in ANIME_CATALOG:
        return filter_choice

    if not _SHUFFLE_QUEUE:
        categories = [k for k in ANIME_CATALOG.keys() if len(get_category_wallpapers(k)) > 0]
        if not categories:
            categories = list(ANIME_CATALOG.keys())
        random.shuffle(categories)
        _SHUFFLE_QUEUE = categories

    return _SHUFFLE_QUEUE.pop(0)

def get_category_wallpapers(category_name):
    folder_path = os.path.join(COLLECTION_DIR, category_name)
    if not os.path.exists(folder_path):
        return []
    valid = []
    valid_exts = ('.jpg', '.png', '.jpeg', '.webp', '.bmp', '.gif')
    if category_name == "12_Custom_Wallpapers":
        for root, _, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith(valid_exts):
                    valid.append(os.path.join(root, f))
    else:
        for f in os.listdir(folder_path):
            if f.lower().endswith(valid_exts):
                valid.append(os.path.join(folder_path, f))
    return valid

def set_wallpaper_win32(path):
    if not path or not os.path.exists(path):
        return False
    # If path is gif, webp, or bmp, cache as clean 24-bit RGB PNG for 100% Windows compatibility
    if path.lower().endswith(('.gif', '.webp', '.bmp')):
        try:
            from PIL import Image
            cache_dir = os.path.join(BASE_DIR, "wallpapers", ".cache")
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, os.path.splitext(os.path.basename(path))[0] + "_cached.png")
            with Image.open(path) as img:
                img.convert("RGB").save(cache_path, "PNG")
            path = cache_path
        except Exception:
            pass
    ret = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        os.path.abspath(path),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return ret == 1

def resolve_audio_path(track_key):
    if not track_key:
        return None
    if track_key.startswith("original/"):
        return os.path.join(BASE_DIR, "audio", track_key.replace("/", os.sep))
    p = os.path.join(SONGS_DIR, track_key)
    if os.path.exists(p):
        return p
    p_orig = os.path.join(ORIGINAL_VOICES_DIR, track_key)
    if os.path.exists(p_orig):
        return p_orig
    return None

_AUDIO_STOP_TIMER = None

def play_audio(audio_path, duration_limit=None):
    global _AUDIO_STOP_TIMER
    if not audio_path or not os.path.exists(audio_path):
        return False
    try:
        # Cancel any previous stop timer
        if _AUDIO_STOP_TIMER and _AUDIO_STOP_TIMER.is_alive():
            _AUDIO_STOP_TIMER.cancel()

        short_p = get_short_path(audio_path)
        mci = ctypes.windll.winmm.mciSendStringW
        mci("stop all", None, 0, None)
        mci("close all", None, 0, None)
        mci(f'open "{short_p}" type mpegvideo alias anime_auto_sound', None, 0, None)
        mci("play anime_auto_sound", None, 0, None)

        if duration_limit and duration_limit > 0:
            def timer_callback():
                stop_audio()
            _AUDIO_STOP_TIMER = threading.Timer(duration_limit, timer_callback)
            _AUDIO_STOP_TIMER.daemon = True
            _AUDIO_STOP_TIMER.start()

        return True
    except Exception as e:
        print("play_audio error:", e)
        return False

def stop_audio():
    global _AUDIO_STOP_TIMER
    if _AUDIO_STOP_TIMER and _AUDIO_STOP_TIMER.is_alive():
        _AUDIO_STOP_TIMER.cancel()
    try:
        mci = ctypes.windll.winmm.mciSendStringW
        mci("stop anime_auto_sound", None, 0, None)
        mci("close anime_auto_sound", None, 0, None)
        mci("stop all", None, 0, None)
        mci("close all", None, 0, None)
    except Exception:
        pass

def change_wallpaper_now(settings=None, force=False):
    if settings is None:
        settings = anime_settings.load_settings()

    # Guard: if auto mode is disabled and not forced manually, do nothing!
    if not force and not settings.get("auto_mode_enabled", True):
        stop_audio()
        return None, None, None

    anime_filter = settings.get("anime_filter", "all")
    category = get_next_category(anime_filter)
    meta = ANIME_CATALOG.get(category, {
        "title": category,
        "char": "Anime Hero",
        "song_name": "Anime Theme",
        "audio_file": "one_piece_overtaken.mp3",
        "voice_file": "original/luffy_gear5.mp3"
    })

    wallpapers = get_category_wallpapers(category)
    if not wallpapers:
        for cat in ANIME_CATALOG.keys():
            wps = get_category_wallpapers(cat)
            if wps:
                category = cat
                meta = ANIME_CATALOG[cat]
                wallpapers = wps
                break

    if not wallpapers:
        return None, None, None

    wp_path = random.choice(wallpapers)

    # STRICT AUDIO MODE: Only play if sound_enabled is True AND song_mode is not mute!
    song_mode = settings.get("song_mode", "mute")
    sound_enabled = settings.get("sound_enabled", False)
    display_song_name = "Audio Muted (Silent)"

    all_tracks = get_all_available_tracks()
    play_full = settings.get("play_full_song", False)
    trans_dur = settings.get("transition_duration", 5)

    if sound_enabled and song_mode != "mute":
        if song_mode == "match_anime":
            track_key = meta.get("audio_file", "one_piece_overtaken.mp3")
            display_song_name = meta.get("song_name", "Anime Theme")
        elif song_mode == "match_voice":
            track_key = meta.get("voice_file", "original/luffy_gear5.mp3")
            display_song_name = f"Voice Climax: {meta.get('char', 'Hero')}"
        elif song_mode == "specific_song":
            track_key = settings.get("specific_song", "one_piece_overtaken.mp3")
            display_song_name = all_tracks.get(track_key, track_key)
        elif song_mode == "shuffle_all":
            track_key = random.choice(list(all_tracks.keys()))
            display_song_name = all_tracks.get(track_key, track_key)
        else:
            track_key = meta.get("audio_file", "one_piece_overtaken.mp3")
            display_song_name = meta.get("song_name", "Anime Theme")

        audio_path = resolve_audio_path(track_key)
        limit = None if play_full else max(1, trans_dur)
        play_audio(audio_path, duration_limit=limit)
    else:
        # 100% SILENT
        stop_audio()

    show_visual = settings.get("show_visual_transition", False)

    # Set wallpaper immediately
    set_wallpaper_win32(wp_path)

    # Launch visual transition as an isolated separate process (no Tkinter thread crashes!)
    if show_visual and trans_dur > 0 and os.path.exists(OVERLAY_SCRIPT):
        try:
            python_exe = sys.executable
            if "python.exe" in python_exe.lower():
                pythonw_candidate = python_exe.lower().replace("python.exe", "pythonw.exe")
                if os.path.exists(pythonw_candidate):
                    python_exe = pythonw_candidate

            # Discover if any video transition loops exist
            video_path = ""
            transitions_dir = os.path.join(BASE_DIR, "videos", "transitions")
            if os.path.exists(transitions_dir):
                available_vids = [
                    os.path.join(transitions_dir, f) for f in os.listdir(transitions_dir)
                    if f.lower().endswith(('.mp4', '.webm', '.mkv', '.avi'))
                ]
                if available_vids:
                    cat_clean = category.lower().replace("_", "")
                    matched = [v for v in available_vids if cat_clean in os.path.basename(v).lower().replace("_", "")]
                    video_path = random.choice(matched) if matched else random.choice(available_vids)

            cmd = [
                python_exe,
                OVERLAY_SCRIPT,
                wp_path,
                meta.get("title", "Anime Masterpiece"),
                meta.get("char", "Hero"),
                display_song_name,
                str(trans_dur),
                video_path
            ]
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        except Exception as e:
            print("Overlay subprocess error:", e)

    # Register next change timestamp in settings
    anime_settings.register_next_change(settings.get("interval_seconds", 30))

    return wp_path, meta, display_song_name

if __name__ == "__main__":
    wp, m, s = change_wallpaper_now(force=True)
    if wp and m:
        print(f"Applied 4K Anime: {os.path.basename(wp)} -> {m['title']} | Audio: {s}")
