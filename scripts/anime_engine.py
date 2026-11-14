import os
import ctypes
import random
import urllib.request
import urllib.parse
import json

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLPAPER_DIR = os.path.join(BASE_DIR, "wallpapers")
COLLECTION_DIR = os.path.join(WALLPAPER_DIR, "collection")
STREAMED_DIR = os.path.join(WALLPAPER_DIR, "streamed")
AUDIO_DIR = os.path.join(BASE_DIR, "audio", "original")
STATE_FILE = os.path.join(BASE_DIR, "current_anime_index.txt")

os.makedirs(STREAMED_DIR, exist_ok=True)

ANIME_ROSTER = [
    {
        "id": "gojo",
        "anime": "Jujutsu Kaisen (呪術廻戦)",
        "character": "Satoru Gojo (五条 悟)",
        "dialogue_jp": "領域展開…「無量空処」",
        "dialogue_romaji": "Ryouiki Tenkai: Muryoukuusho",
        "dialogue_en": "Domain Expansion: Infinite Void",
        "folder": "01_Jujutsu_Kaisen",
        "audio": os.path.join(AUDIO_DIR, "gojo_domain_expansion.mp3"),
        "search_terms": ("satoru gojo", "gojou_satoru")
    },
    {
        "id": "zenitsu",
        "anime": "Demon Slayer (鬼滅の刃)",
        "character": "Zenitsu Agatsuma (我妻 善逸)",
        "dialogue_jp": "雷の呼吸 壱ノ型 霹靂一閃！",
        "dialogue_romaji": "Kaminari no Kokyuu, Ichi no kata: Hekireki Issen!",
        "dialogue_en": "Thunder Breathing, First Form: Thunderclap and Flash!",
        "folder": "02_Demon_Slayer",
        "audio": os.path.join(AUDIO_DIR, "zenitsu_thunder_breathing.mp3"),
        "search_terms": ("zenitsu agatsuma", "agatsuma_zenitsu")
    },
    {
        "id": "luffy",
        "anime": "One Piece (ワンピース)",
        "character": "Monkey D. Luffy - Gear 5 (ルフィ)",
        "dialogue_jp": "アッハッハッハ！ これがオレの最高地点だ！「ギア５」！",
        "dialogue_romaji": "Ahahaha! Kore ga ore no saikou chiten da! Gear 5!",
        "dialogue_en": "Ahahaha! This is my peak! Drums of Liberation!",
        "folder": "03_One_Piece",
        "audio": os.path.join(AUDIO_DIR, "luffy_gear5.mp3"),
        "search_terms": ("monkey d luffy", "monkey_d._luffy")
    },
    {
        "id": "eren",
        "anime": "Attack on Titan (進撃の巨人)",
        "character": "Eren Yeager (エレン・イェーガー)",
        "dialogue_jp": "戦え、戦え！ 勝てなきゃ死ぬ、勝てば生きる！",
        "dialogue_romaji": "Tatakae, tatakae! Katenakya shinu, kateba ikiru!",
        "dialogue_en": "Fight, fight! If you lose, you die. If you win, you live!",
        "folder": "04_Attack_on_Titan",
        "audio": os.path.join(AUDIO_DIR, "eren_tatakae.mp3"),
        "search_terms": ("eren yeager", "eren_yeager")
    },
    {
        "id": "itachi",
        "anime": "Naruto Shippuden (NARUTO -ナルト- 疾風伝)",
        "character": "Itachi Uchiha (うちは イタチ)",
        "dialogue_jp": "天照 (アマテラス) … 万華鏡写輪眼",
        "dialogue_romaji": "Amaterasu... Mangekyou Sharingan",
        "dialogue_en": "Amaterasu... Black inextinguishable flames",
        "folder": "05_Naruto_Shippuden",
        "audio": os.path.join(AUDIO_DIR, "itachi_amaterasu.mp3"),
        "search_terms": ("itachi uchiha", "uchiha_itachi")
    },
    {
        "id": "frieren",
        "anime": "Frieren: Beyond Journey's End (葬送のフリーレン)",
        "character": "Frieren (フリーレン)",
        "dialogue_jp": "アウラ、自害しろ。… ゾルトラーク！",
        "dialogue_romaji": "Aura, jigai shiro. ... Zoltraak!",
        "dialogue_en": "Aura, kill yourself. ... Zoltraak!",
        "folder": "06_Frieren",
        "audio": os.path.join(AUDIO_DIR, "frieren_zoltraak.mp3"),
        "search_terms": ("frieren", "frieren")
    },
    {
        "id": "saber",
        "anime": "Fate / Stay Night (フェイト/ステイナイト)",
        "character": "Saber Artoria Pendragon (セイバー)",
        "dialogue_jp": "約束された勝利の剣…「エクス・カリバー」！",
        "dialogue_romaji": "Yakusokusareta Shouri no Ken: Ex-calibur!",
        "dialogue_en": "Sword of Promised Victory: Excalibur!",
        "folder": "07_Fate_Series",
        "audio": os.path.join(AUDIO_DIR, "saber_excalibur.mp3"),
        "search_terms": ("saber fate", "saber")
    },
    {
        "id": "edgerunners",
        "anime": "Cyberpunk: Edgerunners (サイバーパンク エッジランナーズ)",
        "character": "Lucy (ルーシー)",
        "dialogue_jp": "月へ連れて行ってあげる。約束だよ。",
        "dialogue_romaji": "Tsuki e tsurete itte ageru. Yakusoku da yo.",
        "dialogue_en": "I'll take you to the moon. It's a promise.",
        "folder": "08_Cyberpunk_Edgerunners",
        "audio": os.path.join(AUDIO_DIR, "edgerunners_moon.mp3"),
        "search_terms": ("cyberpunk edgerunners", "lucy_(cyberpunk)")
    },
    {
        "id": "rengoku",
        "anime": "Demon Slayer: Mugen Train (無限列車編)",
        "character": "Kyojuro Rengoku (煉獄 杏寿郎)",
        "dialogue_jp": "うまい！うまい！ 心を燃やせ！",
        "dialogue_romaji": "Umai! Umai! Kokoro wo moyase!",
        "dialogue_en": "Delicious! Delicious! Set your heart ablaze!",
        "folder": "02_Demon_Slayer",
        "audio": os.path.join(AUDIO_DIR, "rengoku_umai.mp3"),
        "search_terms": ("kyojuro rengoku", "rengoku_kyoujurou")
    },
    {
        "id": "sukuna",
        "anime": "Jujutsu Kaisen (呪術廻戦)",
        "character": "Ryomen Sukuna (両面 宿儺)",
        "dialogue_jp": "領域展開…「伏魔御廚子」",
        "dialogue_romaji": "Ryouiki Tenkai: Fukuma Mizushi",
        "dialogue_en": "Domain Expansion: Malevolent Shrine",
        "folder": "01_Jujutsu_Kaisen",
        "audio": os.path.join(AUDIO_DIR, "sukuna_domain_expansion.mp3"),
        "search_terms": ("ryomen sukuna", "ryoumen_sukuna")
    }
]

def get_local_wallpaper_for_anime(folder_name):
    cat_dir = os.path.join(COLLECTION_DIR, folder_name)
    if os.path.exists(cat_dir):
        valid = [os.path.join(cat_dir, f) for f in os.listdir(cat_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))]
        if valid:
            return random.choice(valid)
    return None

def fetch_wallhaven(query):
    try:
        encoded_q = urllib.parse.quote(query)
        base_url = f"https://wallhaven.cc/api/v1/search?q={encoded_q}&categories=110&purity=100"
        req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            last_page = data.get('meta', {}).get('last_page', 1)
            items = data.get('data', [])

        if items:
            if last_page > 1:
                random_page = random.randint(1, min(last_page, 20))
                page_url = f"{base_url}&page={random_page}"
                req_page = urllib.request.Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_page, timeout=5) as resp:
                    page_data = json.loads(resp.read().decode('utf-8'))
                    items = page_data.get('data', items)
            if items:
                return random.choice(items)['path']
    except Exception:
        pass
    return None

def fetch_konachan(tag):
    try:
        page = random.randint(1, 15)
        url = f"https://konachan.net/post.json?tags={urllib.parse.quote(tag)}&limit=15&page={page}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                wide = [x for x in data if x.get('width', 0) >= x.get('height', 0) and x.get('file_url')]
                chosen = random.choice(wide) if wide else random.choice(data)
                return chosen.get('file_url')
    except Exception:
        pass
    return None

def stream_online_wallpaper(item):
    wallhaven_q, tag_q = item["search_terms"]
    url = fetch_wallhaven(wallhaven_q)
    if not url:
        url = fetch_konachan(tag_q)

    if not url:
        return get_local_wallpaper_for_anime(item["folder"])

    try:
        ext = os.path.splitext(url)[1].split('?')[0]
        if not ext or ext.lower() not in ('.jpg', '.png', '.jpeg'):
            ext = '.jpg'
        fname = f"{item['id']}_05M_stream_{random.randint(1000, 9999)}{ext}"
        dest = os.path.join(STREAMED_DIR, fname)

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(dest, "wb") as f:
                f.write(data)

        return dest
    except Exception:
        return get_local_wallpaper_for_anime(item["folder"])

def set_wallpaper(path):
    if not path or not os.path.exists(path):
        return False
    ret = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        path,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    return ret == 1

def play_audio(audio_path):
    if not os.path.exists(audio_path):
        return False
    try:
        mci = ctypes.windll.winmm.mciSendStringW
        mci("close anime_dialogue", None, 0, None)
        mci(f'open "{audio_path}" type mpegvideo alias anime_dialogue', None, 0, None)
        mci("play anime_dialogue", None, 0, None)
        return True
    except Exception:
        return False

def activate_anime(index_or_id, stream_cloud=False, play_sound_flag=True):
    if isinstance(index_or_id, str):
        found = [i for i, x in enumerate(ANIME_ROSTER) if x["id"] == index_or_id]
        idx = found[0] if found else 0
    else:
        idx = index_or_id % len(ANIME_ROSTER)

    item = ANIME_ROSTER[idx]

    if stream_cloud:
        wp_path = stream_online_wallpaper(item)
    else:
        wp_path = get_local_wallpaper_for_anime(item["folder"])
        if not wp_path:
            wp_path = stream_online_wallpaper(item)

    if wp_path:
        set_wallpaper(wp_path)

    if play_sound_flag:
        play_audio(item["audio"])

    try:
        with open(STATE_FILE, "w") as f:
            f.write(str(idx))
    except Exception:
        pass

    return item, wp_path

def cycle_next(stream_cloud=False, play_sound_flag=True):
    current_idx = 0
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                current_idx = int(f.read().strip())
        except Exception:
            current_idx = 0

    next_idx = (current_idx + 1) % len(ANIME_ROSTER)
    return activate_anime(next_idx, stream_cloud=stream_cloud, play_sound_flag=play_sound_flag)

if __name__ == "__main__":
    item, wp = cycle_next(stream_cloud=False, play_sound_flag=True)
    print("=" * 65)
    print(f"ANIME:            {item['anime']}")
    print(f"CHARACTER:        {item['character']}")
    print(f"DIALOGUE AUDIO:   {os.path.basename(item['audio'])}")
    print(f"APPLIED WALLPAPER:{os.path.basename(wp)}")
    print("=" * 65)
