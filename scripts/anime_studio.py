import os
import sys
import time
import atexit
import threading
import subprocess
import webbrowser
import shutil
import ctypes
import psutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Set High-DPI Awareness on Windows for crystal-sharp text and graphics
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    import windnd
    HAS_WINDND = True
except Exception:
    HAS_WINDND = False

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
PID_FILE = os.path.join(CONFIG_DIR, "app.pid")
ICON_PATH = os.path.join(BASE_DIR, "anime_icon.ico")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# Single-Instance Enforcement via PID
os.makedirs(CONFIG_DIR, exist_ok=True)
RESTORE_SIGNAL_FILE = os.path.join(CONFIG_DIR, "restore_signal.flag")
if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE, "r") as f:
            content_pid = f.read().strip()
        if content_pid.isdigit():
            old_pid = int(content_pid)
            if psutil.pid_exists(old_pid) and old_pid != os.getpid():
                p = psutil.Process(old_pid)
                cmdline = ' '.join(p.cmdline() or []).lower()
                if "animestudio" in cmdline or "anime_studio" in cmdline:
                    with open(RESTORE_SIGNAL_FILE, "w") as rf:
                        rf.write("restore")
                    sys.exit(0)
    except:
        pass

with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

atexit.register(lambda: os.remove(PID_FILE) if os.path.exists(PID_FILE) else None)

import pystray
from pystray import MenuItem as item

import anime_settings
import anime_auto_engine

# Streaming & Web Portals Catalog
PORTALS = [
    ("📺 Bilibili Anime (Bstation)", "100% Free 1080p HD Anime Streaming (Zero ISP Blocks in India)", "https://www.bilibili.tv/en", "#00f5d4"),
    ("🎬 Crunchyroll Anime", "Official Free Anime Streaming, Dubs & Subs", "https://www.crunchyroll.com", "#ffbe0b"),
    ("📺 Muse Asia Anime", "Official 100% Free Anime Streaming on YouTube", "https://www.youtube.com/@MuseAsia/videos", "#ff0055"),
    ("📺 Ani-One Asia Anime", "Legal Full Episode Anime Streaming on YouTube", "https://www.youtube.com/@AniOneAsia/videos", "#00b4d8"),
    ("📥 Toonworld (Hindi Anime)", "Full Anime Episodes in Hindi Dub & English Subs", "https://toonworld4all.me", "#38b000"),
    ("📖 MangaDex", "Read Millions of Manga Online Free", "https://mangadex.org", "#ff70a6"),
    ("⚡ HiAnime (Needs Secure DNS)", "Free 1080p Anime (Enable Cloudflare DNS in Chrome)", "https://hianime.to", "#7209b7"),
    ("🌸 Lofi Anime Radio", "24/7 Relaxing Anime Beats to Study/Relax", "https://www.youtube.com/watch?v=jfKfPfyJRdk", "#a2d2ff")
]

def add_hover(widget, normal_bg, hover_bg, normal_fg=None, hover_fg=None):
    """Add smooth hover effects to buttons and cards."""
    def on_enter(e):
        try:
            widget.config(bg=hover_bg)
            if hover_fg:
                widget.config(fg=hover_fg)
        except Exception:
            pass
    def on_leave(e):
        try:
            widget.config(bg=normal_bg)
            if normal_fg:
                widget.config(fg=normal_fg)
        except Exception:
            pass
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

class AnimeStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌸 Anime Studio Pro — 4K Desktop Suite")
        self.root.geometry("980x690")
        self.root.minsize(920, 640)
        self.root.configure(bg="#0c0a18")

        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except:
                pass

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(10, (sw - 980) // 2)
        y = max(10, (sh - 690) // 2)
        self.root.geometry(f"980x690+{x}+{y}")

        self.settings = anime_settings.load_settings()
        self.auto_change_enabled = self.settings.get("auto_mode_enabled", True)
        self.sound_enabled = self.settings.get("sound_enabled", False)
        self.animation_enabled = self.settings.get("show_visual_transition", False)
        self.is_changing = False

        # Reset past schedule on startup so it doesn't immediately change on boot
        now = time.time()
        if self.settings.get("next_change_timestamp", 0) <= now:
            interval = max(5, self.settings.get("interval_seconds", 30))
            self.settings["next_change_timestamp"] = now + interval
            anime_settings.save_settings(self.settings)

        self.active_wallpaper_path = None
        self.active_meta = None
        self.active_song_title = "None"
        self.active_preview_img = None
        self.active_res = "4K UHD"

        self.mini_hud_window = None
        self.show_mini_hud = False
        self.tray_icon = None

        self.apply_immediately_var = tk.BooleanVar(value=True)
        self.filter_to_custom_var = tk.BooleanVar(value=True)
        self.custom_wallpapers_list = []
        self.custom_img_refs = []
        self.gal_current_page = 0
        self.gal_page_size = 24

        # In-memory thumbnail cache for ultra-fast navigation
        self.thumb_cache = {}

        # Configure dark ttk theme
        self.setup_ttk_styles()

        self.setup_ui()
        self.setup_system_tray()

        # Setup Drag & Drop Hook
        if HAS_WINDND:
            try:
                windnd.hook_dropfiles(self.root, func=self.handle_drag_drop_files, force_unicode=True)
            except Exception as e:
                print("Drag and drop hook warning:", e)

        self.show_tab("dashboard")

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_clicked)

        # Background loops
        self.check_restore_signal()
        self.update_timer_loop()

        # Initial display
        self.refresh_current_display()

    def setup_ttk_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure(
            "TCombobox",
            fieldbackground="#16122a",
            background="#251e44",
            foreground="#ffffff",
            darkcolor="#16122a",
            lightcolor="#251e44",
            arrowcolor="#00f5d4"
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#16122a")],
            selectbackground=[("readonly", "#251e44")],
            selectforeground=[("readonly", "#00f5d4")]
        )
        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background="#251e44",
            darkcolor="#16122a",
            lightcolor="#251e44",
            troughcolor="#0c0a18",
            bordercolor="#0c0a18",
            arrowcolor="#00f5d4"
        )

    def get_thumbnail(self, path, size=(160, 90)):
        key = (path, size)
        if key in self.thumb_cache:
            return self.thumb_cache[key]
        try:
            im = Image.open(path)
            im.thumbnail(size, Image.Resampling.LANCZOS)
            tk_im = ImageTk.PhotoImage(im)
            self.thumb_cache[key] = tk_im
            return tk_im
        except Exception:
            return None

    # ========================== UI SETUP ==========================
    def setup_ui(self):
        self.main_container = tk.Frame(self.root, bg="#0c0a18")
        self.main_container.pack(fill="both", expand=True)

        # --- LEFT SIDEBAR ---
        self.sidebar = tk.Frame(self.main_container, bg="#110d22", width=225)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Branding Header
        brand_frame = tk.Frame(self.sidebar, bg="#110d22", pady=18, padx=12)
        brand_frame.pack(fill="x")

        lbl_logo = tk.Label(
            brand_frame,
            text="🌸 ANIME STUDIO",
            font=("Segoe UI", 13, "bold"),
            fg="#00f5d4",
            bg="#110d22"
        )
        lbl_logo.pack()

        badge_row = tk.Frame(brand_frame, bg="#110d22")
        badge_row.pack(pady=(2, 0))

        lbl_badge = tk.Label(
            badge_row,
            text="PRO SUITE",
            font=("Segoe UI", 7, "bold"),
            fg="#ffe600",
            bg="#20173d",
            padx=5,
            pady=1
        )
        lbl_badge.pack(side="left", padx=2)

        lbl_v = tk.Label(
            badge_row,
            text="v2.5 ULTRA",
            font=("Segoe UI", 7, "bold"),
            fg="#ff0055",
            bg="#20173d",
            padx=5,
            pady=1
        )
        lbl_v.pack(side="left", padx=2)

        # Navigation Divider Line
        tk.Frame(self.sidebar, bg="#231a44", height=1).pack(fill="x", padx=12, pady=(0, 8))

        # Navigation Buttons
        self.nav_buttons = {}
        navs = [
            ("dashboard", "🏠  Dashboard"),
            ("custom", "🎨  Custom Wallpapers"),
            ("gallery", "🖼️  4K Wallpaper Gallery"),
            ("timer", "⏱️  Timer & Schedule"),
            ("audio", "🎵  Music & Japanese Voice"),
            ("portals", "🌐  Anime Portals"),
            ("settings", "⚙️  Preferences & Updates")
        ]

        for tab_id, tab_label in navs:
            btn = tk.Button(
                self.sidebar,
                text=f"  {tab_label}",
                font=("Segoe UI", 9, "bold"),
                bg="#110d22",
                fg="#b8b5cb",
                activebackground="#1d163a",
                activeforeground="#00f5d4",
                relief="flat",
                anchor="w",
                padx=12,
                pady=9,
                cursor="hand2",
                command=lambda tid=tab_id: self.show_tab(tid)
            )
            btn.pack(fill="x", padx=8, pady=2)
            add_hover(btn, normal_bg="#110d22", hover_bg="#1d163a", normal_fg="#b8b5cb", hover_fg="#ffffff")
            self.nav_buttons[tab_id] = btn

        # Status & Stats Card at Bottom of Sidebar
        status_box = tk.Frame(self.sidebar, bg="#17112e", padx=10, pady=12, highlightbackground="#2d2252", highlightthickness=1)
        status_box.pack(side="bottom", fill="x", padx=10, pady=14)

        self.lbl_status_badge = tk.Label(
            status_box,
            text="🟢 AUTO-MODE: ON" if self.auto_change_enabled else "🔴 AUTO-MODE: PAUSED",
            font=("Segoe UI", 8, "bold"),
            fg="#00f5d4" if self.auto_change_enabled else "#ff5964",
            bg="#17112e"
        )
        self.lbl_status_badge.pack(anchor="w")

        self.lbl_sidebar_timer = tk.Label(
            status_box,
            text="⏳ Next in: Calculating...",
            font=("Segoe UI", 7, "bold"),
            fg="#ffe600",
            bg="#17112e"
        )
        self.lbl_sidebar_timer.pack(anchor="w", pady=(3, 0))

        self.lbl_sound_badge = tk.Label(
            status_box,
            text="🔊 SOUND: ON" if self.sound_enabled else "🔇 SOUND: MUTED",
            font=("Segoe UI", 7, "bold"),
            fg="#ff0055" if self.sound_enabled else "#00f5d4",
            bg="#17112e"
        )
        self.lbl_sound_badge.pack(anchor="w", pady=(3, 0))

        tk.Label(
            status_box,
            text="🖼️ 301+ UHD 4K Wallpapers",
            font=("Segoe UI", 7),
            fg="#8d88ab",
            bg="#17112e"
        ).pack(anchor="w", pady=(2, 0))

        # --- RIGHT CONTENT CONTAINER ---
        self.content_area = tk.Frame(self.main_container, bg="#0c0a18", padx=16, pady=14)
        self.content_area.pack(side="right", fill="both", expand=True)

        self.tabs = {}
        self.build_dashboard_tab()
        self.build_custom_tab()
        self.build_gallery_tab()
        self.build_timer_tab()
        self.build_audio_tab()
        self.build_portals_tab()
        self.build_settings_tab()

    def show_tab(self, tab_id):
        for tid, frame in self.tabs.items():
            frame.pack_forget()
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.config(bg="#ff0055", fg="#ffffff")
                add_hover(btn, normal_bg="#ff0055", hover_bg="#e0004c", normal_fg="#ffffff", hover_fg="#ffffff")
            else:
                btn.config(bg="#110d22", fg="#b8b5cb")
                add_hover(btn, normal_bg="#110d22", hover_bg="#1d163a", normal_fg="#b8b5cb", hover_fg="#ffffff")

        if tab_id in self.tabs:
            self.tabs[tab_id].pack(fill="both", expand=True)
            if tab_id == "custom":
                self.refresh_custom_wallpapers_grid()
            elif tab_id == "gallery":
                self.load_gallery_thumbnails()

    # ========================== TAB 1: DASHBOARD ==========================
    def build_dashboard_tab(self):
        tab = tk.Frame(self.content_area, bg="#0c0a18")
        self.tabs["dashboard"] = tab

        # Top Header Bar
        top_row = tk.Frame(tab, bg="#0c0a18")
        top_row.pack(fill="x", pady=(0, 10))

        lbl_head = tk.Label(top_row, text="DASHBOARD & LIVE MONITOR", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0c0a18")
        lbl_head.pack(side="left")

        self.btn_master_sound = tk.Button(
            top_row,
            text="🔇 SOUND: MUTED (Silent)" if not self.sound_enabled else "🔊 SOUND: ACTIVE",
            font=("Segoe UI", 8, "bold"),
            bg="#1f183d" if not self.sound_enabled else "#ff0055",
            fg="#00f5d4" if not self.sound_enabled else "#ffffff",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=3,
            command=self.toggle_master_sound
        )
        self.btn_master_sound.pack(side="right", padx=(8, 0))
        add_hover(self.btn_master_sound, "#1f183d", "#2d2358")

        stats_badge = tk.Label(
            top_row,
            text="✨ 4K/5K/8K ULTRA HIGH-RES",
            font=("Segoe UI", 8, "bold"),
            fg="#ffe600",
            bg="#181232",
            padx=10,
            pady=3
        )
        stats_badge.pack(side="right")

        # Two Main Hero Cards Grid
        grid_frame = tk.Frame(tab, bg="#0c0a18")
        grid_frame.pack(fill="both", expand=True)

        # --- LEFT HERO CARD: 4K PREVIEW ---
        preview_card = tk.Frame(grid_frame, bg="#16122a", padx=14, pady=12, highlightbackground="#00f5d4", highlightthickness=1)
        preview_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        p_header = tk.Frame(preview_card, bg="#16122a")
        p_header.pack(fill="x")

        lbl_p_title = tk.Label(p_header, text="ACTIVE DESKTOP WALLPAPER", font=("Segoe UI", 8, "bold"), fg="#00f5d4", bg="#16122a")
        lbl_p_title.pack(side="left")

        self.lbl_active_res = tk.Label(p_header, text="3840x2160 UHD 4K", font=("Segoe UI", 7, "bold"), fg="#00f5d4", bg="#20173d", padx=6, pady=1)
        self.lbl_active_res.pack(side="right")

        self.lbl_preview_canvas = tk.Label(
            preview_card,
            bg="#0c0817",
            text="Loading 4K Preview...",
            fg="#b8b5cb",
            width=36,
            height=11,
            cursor="hand2"
        )
        self.lbl_preview_canvas.pack(fill="both", expand=True, pady=8)
        self.lbl_preview_canvas.bind("<Button-1>", lambda e: self.open_active_file())

        preview_footer = tk.Frame(preview_card, bg="#16122a")
        preview_footer.pack(fill="x")

        self.lbl_active_wp_name = tk.Label(
            preview_footer,
            text="4k_anime_masterpiece.png",
            font=("Segoe UI", 8, "italic"),
            fg="#b8b5cb",
            bg="#16122a",
            wraplength=280,
            justify="left"
        )
        self.lbl_active_wp_name.pack(side="left")

        btn_open_file = tk.Button(
            preview_footer,
            text="📂 Open File",
            font=("Segoe UI", 7, "bold"),
            bg="#20173d",
            fg="#00f5d4",
            relief="flat",
            cursor="hand2",
            padx=6,
            pady=2,
            command=self.open_active_file
        )
        btn_open_file.pack(side="right")
        add_hover(btn_open_file, "#20173d", "#2d2054")

        # --- RIGHT HERO CARD: ANIME THEME & AUDIO ---
        info_card = tk.Frame(grid_frame, bg="#16122a", padx=16, pady=12, highlightbackground="#ff0055", highlightthickness=1)
        info_card.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(info_card, text="ANIME THEME & AUDIO TRACK", font=("Segoe UI", 8, "bold"), fg="#ff0055", bg="#16122a").pack(anchor="w")

        self.lbl_active_anime = tk.Label(info_card, text="One Piece", font=("Segoe UI", 14, "bold"), fg="#ffe600", bg="#16122a")
        self.lbl_active_anime.pack(anchor="w", pady=(4, 0))

        self.lbl_active_char = tk.Label(info_card, text="Monkey D. Luffy (Gear 5 Drums of Liberation)", font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#16122a")
        self.lbl_active_char.pack(anchor="w", pady=(1, 8))

        # Audio Box with live equalizer text
        audio_box = tk.Frame(info_card, bg="#0c0817", padx=12, pady=10, highlightbackground="#2d224e", highlightthickness=1)
        audio_box.pack(fill="x", pady=4)

        aud_top = tk.Frame(audio_box, bg="#0c0817")
        aud_top.pack(fill="x")

        tk.Label(aud_top, text="🎵 SOUNDTRACK / VOICE:", font=("Segoe UI", 7, "bold"), fg="#ffbe0b", bg="#0c0817").pack(side="left")
        self.lbl_eq_icon = tk.Label(aud_top, text="[ ılı.lıllılı.ıllı ]", font=("Segoe UI", 7, "bold"), fg="#00f5d4", bg="#0c0817")
        self.lbl_eq_icon.pack(side="right")

        self.lbl_active_song = tk.Label(
            audio_box,
            text="Overtaken (The Legendary Walk Theme)",
            font=("Segoe UI", 9, "bold"),
            fg="#ffffff",
            bg="#0c0817",
            wraplength=280,
            justify="left"
        )
        self.lbl_active_song.pack(anchor="w", pady=(4, 6))

        aud_ctrls = tk.Frame(audio_box, bg="#0c0817")
        aud_ctrls.pack(fill="x")

        btn_play_audio = tk.Button(
            aud_ctrls,
            text="▶️ Play Track",
            font=("Segoe UI", 7, "bold"),
            bg="#2a9d8f",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.play_current_active_audio
        )
        btn_play_audio.pack(side="left", padx=(0, 4))
        add_hover(btn_play_audio, "#2a9d8f", "#34b8a7")

        btn_stop_audio = tk.Button(
            aud_ctrls,
            text="⏹️ Stop Sound",
            font=("Segoe UI", 7),
            bg="#3b3754",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=anime_auto_engine.stop_audio
        )
        btn_stop_audio.pack(side="left")
        add_hover(btn_stop_audio, "#3b3754", "#4a456a")

        # Quick Theme Filter Row inside Info Card
        tk.Label(info_card, text="Quick Anime Switcher:", font=("Segoe UI", 8, "bold"), fg="#b8b5cb", bg="#16122a").pack(anchor="w", pady=(10, 2))
        self.dash_filter_combo = ttk.Combobox(info_card, state="readonly", font=("Segoe UI", 8))
        self.dash_filter_options = [("🌐 All Anime (Balanced Shuffle)", "all")]
        for k, v in anime_auto_engine.ANIME_CATALOG.items():
            self.dash_filter_options.append((f"{v['title']} ({v['char']})", k))
        self.dash_filter_combo['values'] = [opt[0] for opt in self.dash_filter_options]
        cur_filter = self.settings.get("anime_filter", "all")
        for i, opt in enumerate(self.dash_filter_options):
            if opt[1] == cur_filter:
                self.dash_filter_combo.current(i)
                break
        if not self.dash_filter_combo.get():
            self.dash_filter_combo.current(0)
        self.dash_filter_combo.bind("<<ComboboxSelected>>", self.on_dash_filter_changed)
        self.dash_filter_combo.pack(fill="x")

        # Countdown & Progress Section
        timer_box = tk.Frame(tab, bg="#16122a", padx=14, pady=10, highlightbackground="#3d2c60", highlightthickness=1)
        timer_box.pack(fill="x", pady=(10, 8))

        time_row = tk.Frame(timer_box, bg="#16122a")
        time_row.pack(fill="x")

        self.lbl_dash_timer = tk.Label(time_row, text="⏳ Next 4K Wallpaper: Calculating...", font=("Segoe UI", 10, "bold"), fg="#ffe600", bg="#16122a")
        self.lbl_dash_timer.pack(side="left")

        self.lbl_dash_next_date = tk.Label(time_row, text="📅 Scheduled at: --", font=("Segoe UI", 8), fg="#00f5d4", bg="#16122a")
        self.lbl_dash_next_date.pack(side="right")

        self.canvas_dash_prog = tk.Canvas(timer_box, height=8, bg="#0c0817", highlightthickness=0)
        self.canvas_dash_prog.pack(fill="x", pady=(6, 2))
        self.rect_dash_prog = self.canvas_dash_prog.create_rectangle(0, 0, 500, 8, fill="#00f5d4", width=0)

        # Quick Controls Row
        ctrl_row = tk.Frame(tab, bg="#0c0a17")
        ctrl_row.pack(fill="x", pady=(4, 0))

        btn_next = tk.Button(
            ctrl_row,
            text="🎬 NEXT WALLPAPER (TRANSITION)",
            font=("Segoe UI", 9, "bold"),
            bg="#ff0055",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
            command=self.trigger_change_now
        )
        btn_next.pack(side="left", expand=True, fill="x", padx=2)
        add_hover(btn_next, "#ff0055", "#e0004c")

        self.btn_pause = tk.Button(
            ctrl_row,
            text="⏸️ PAUSE AUTO" if self.auto_change_enabled else "▶️ RESUME AUTO",
            font=("Segoe UI", 9, "bold"),
            bg="#2a9d8f" if self.auto_change_enabled else "#e63946",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
            command=self.toggle_pause
        )
        self.btn_pause.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_hud_toggle = tk.Button(
            ctrl_row,
            text="🪟 SHOW MINI-HUD",
            font=("Segoe UI", 9, "bold"),
            bg="#7209b7",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
            command=self.toggle_mini_hud
        )
        self.btn_hud_toggle.pack(side="left", expand=True, fill="x", padx=2)
        add_hover(self.btn_hud_toggle, "#7209b7", "#8415d1")

        self.btn_quick_sound = tk.Button(
            ctrl_row,
            text="🔇 MUTE AUDIO" if self.sound_enabled else "🔊 ENABLE SOUND",
            font=("Segoe UI", 9, "bold"),
            bg="#4a4e69" if self.sound_enabled else "#20173d",
            fg="#ffffff" if self.sound_enabled else "#00f5d4",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
            command=self.toggle_master_sound
        )
        self.btn_quick_sound.pack(side="left", expand=True, fill="x", padx=2)
        add_hover(self.btn_quick_sound, "#20173d", "#2d2054")

        btn_random = tk.Button(
            ctrl_row,
            text="🎲 RANDOM 4K",
            font=("Segoe UI", 9, "bold"),
            bg="#3a0ca3",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
            command=self.trigger_random_wallpaper
        )
        btn_random.pack(side="left", expand=True, fill="x", padx=2)
        add_hover(btn_random, "#3a0ca3", "#4c16cb")

        btn_add_custom_dash = tk.Button(
            tab,
            text="🎨 + ADD / IMPORT CUSTOM WALLPAPERS (DRAG & DROP READY)",
            font=("Segoe UI", 9, "bold"),
            bg="#00b4d8",
            fg="#0c0817",
            activebackground="#00f5d4",
            activeforeground="#0c0817",
            relief="flat",
            cursor="hand2",
            pady=8,
            command=lambda: self.show_tab("custom")
        )
        btn_add_custom_dash.pack(fill="x", pady=(8, 0))
        add_hover(btn_add_custom_dash, "#00b4d8", "#00f5d4")

    def on_dash_filter_changed(self, event=None):
        idx = self.dash_filter_combo.current()
        if 0 <= idx < len(self.dash_filter_options):
            cat_id = self.dash_filter_options[idx][1]
            anime_settings.update_setting("anime_filter", cat_id)
            self.settings["anime_filter"] = cat_id
            self.trigger_change_now()

    def open_active_file(self):
        if self.active_wallpaper_path and os.path.exists(self.active_wallpaper_path):
            try:
                os.startfile(self.active_wallpaper_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def trigger_random_wallpaper(self):
        cur_settings = anime_settings.load_settings()
        cur_settings["anime_filter"] = "all"
        self.trigger_change_now()

    def toggle_master_sound(self):
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            anime_auto_engine.stop_audio()
            anime_settings.update_setting("sound_enabled", False)
            anime_settings.update_setting("song_mode", "mute")
            self.btn_master_sound.config(text="🔇 SOUND: MUTED (Silent)", bg="#1f183d", fg="#00f5d4")
            self.lbl_sound_badge.config(text="🔇 SOUND: MUTED", fg="#00f5d4")
            self.btn_quick_sound.config(text="🔊 ENABLE SOUND", bg="#20173d", fg="#00f5d4")
            self.lbl_active_song.config(text="Audio Muted (Silent Mode)")
            self.lbl_eq_icon.config(text="[ 🔇 MUTED ]", fg="#8d88ab")
        else:
            anime_settings.update_setting("sound_enabled", True)
            anime_settings.update_setting("song_mode", "match_anime")
            self.btn_master_sound.config(text="🔊 SOUND: ACTIVE", bg="#ff0055", fg="#ffffff")
            self.lbl_sound_badge.config(text="🔊 SOUND: ON", fg="#ff0055")
            self.btn_quick_sound.config(text="🔇 MUTE AUDIO", bg="#4a4e69", fg="#ffffff")
            self.lbl_eq_icon.config(text="[ ılı.lıllılı.ıllı ]", fg="#00f5d4")
            self.play_current_active_audio()

    def play_current_active_audio(self):
        if not self.sound_enabled:
            messagebox.showinfo("Audio Muted", "Sound is currently MUTED.\nClick 'ENABLE SOUND' on the dashboard if you want sound effects.")
            return
        if self.active_song_title and self.active_song_title != "None" and "Muted" not in self.active_song_title:
            track_p = anime_auto_engine.resolve_audio_path(self.active_song_title)
            if track_p:
                anime_auto_engine.play_audio(track_p, duration_limit=15)


    # ========================== TAB 2: CUSTOM WALLPAPERS ==========================
    def build_custom_tab(self):
        tab = tk.Frame(self.content_area, bg="#0c0a17")
        self.tabs["custom"] = tab

        header_row = tk.Frame(tab, bg="#0c0a17")
        header_row.pack(fill="x", pady=(0, 4))

        tk.Label(header_row, text="🎨 CUSTOM ANIME WALLPAPER STUDIO", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0c0a17").pack(side="left")

        dnd_badge = "✨ Drag & Drop Ready" if HAS_WINDND else "📁 File Picker Ready"
        tk.Label(header_row, text=dnd_badge, font=("Segoe UI", 8, "bold"), fg="#00f5d4", bg="#16122a", padx=8, pady=2).pack(side="right")

        tk.Label(tab, text="Drag & drop anime images, GIFs, videos, or folders directly into this window, or use the quick buttons below.", font=("Segoe UI", 8), fg="#b8b5cb", bg="#0c0a17").pack(anchor="w", pady=(0, 8))

        # --- DROP & IMPORT HERO CARD ---
        self.drop_card = tk.Frame(tab, bg="#16122a", padx=14, pady=10, highlightbackground="#00b4d8", highlightthickness=1)
        self.drop_card.pack(fill="x", pady=(0, 8))

        # Visual Drop Box Area with Interactive Hover Effect
        self.drop_box = tk.Frame(self.drop_card, bg="#0d091a", padx=12, pady=12, highlightbackground="#3d2c60", highlightthickness=1, cursor="hand2")
        self.drop_box.pack(fill="x", pady=(0, 6))
        self.drop_box.bind("<Button-1>", lambda e: self.import_custom_images())

        lbl_drop_icon = tk.Label(self.drop_box, text="📂 DRAG & DROP ANIME WALLPAPERS & VIDEOS HERE", font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#0d091a", cursor="hand2")
        lbl_drop_icon.pack()
        lbl_drop_icon.bind("<Button-1>", lambda e: self.import_custom_images())

        lbl_drop_hint = tk.Label(self.drop_box, text="Supports PNG, JPG, JPEG, WEBP, GIF, BMP, MP4, WEBM • Click anywhere in this box to browse files", font=("Segoe UI", 8), fg="#b8b5cb", bg="#0d091a", cursor="hand2")
        lbl_drop_hint.pack(pady=(2, 0))
        lbl_drop_hint.bind("<Button-1>", lambda e: self.import_custom_images())

        def on_drop_enter(e):
            self.drop_box.config(bg="#1a1435", highlightbackground="#00f5d4")
            lbl_drop_icon.config(bg="#1a1435", fg="#ffe600")
            lbl_drop_hint.config(bg="#1a1435", fg="#ffffff")

        def on_drop_leave(e):
            self.drop_box.config(bg="#0d091a", highlightbackground="#3d2c60")
            lbl_drop_icon.config(bg="#0d091a", fg="#00f5d4")
            lbl_drop_hint.config(bg="#0d091a", fg="#b8b5cb")

        self.drop_box.bind("<Enter>", on_drop_enter)
        self.drop_box.bind("<Leave>", on_drop_leave)

        # Action Buttons Row
        act_row = tk.Frame(self.drop_card, bg="#16122a")
        act_row.pack(fill="x", pady=2)

        btn_add_img = tk.Button(act_row, text="🖼️ + Add Images / GIFs", font=("Segoe UI", 8, "bold"), bg="#7209b7", fg="#ffffff", relief="flat", cursor="hand2", padx=10, pady=4, command=self.import_custom_images)
        btn_add_img.pack(side="left", padx=2)
        add_hover(btn_add_img, "#7209b7", "#8415d1")

        btn_add_folder = tk.Button(act_row, text="📁 + Add Entire Folder", font=("Segoe UI", 8, "bold"), bg="#3a0ca3", fg="#ffffff", relief="flat", cursor="hand2", padx=10, pady=4, command=self.import_custom_folder)
        btn_add_folder.pack(side="left", padx=2)
        add_hover(btn_add_folder, "#3a0ca3", "#4c16cb")

        btn_add_vid = tk.Button(act_row, text="🎬 + Add Video Loop (4K)", font=("Segoe UI", 8, "bold"), bg="#ff0055", fg="#ffffff", relief="flat", cursor="hand2", padx=10, pady=4, command=self.import_custom_video)
        btn_add_vid.pack(side="left", padx=2)
        add_hover(btn_add_vid, "#ff0055", "#e0004c")

        btn_open_exp = tk.Button(act_row, text="📂 Open Folder in Explorer", font=("Segoe UI", 8), bg="#221e3b", fg="#00f5d4", relief="flat", cursor="hand2", padx=8, pady=4, command=self.open_custom_folder_explorer)
        btn_open_exp.pack(side="right", padx=2)
        add_hover(btn_open_exp, "#221e3b", "#2f2a52")

        # Options Checkboxes Row
        opts_row = tk.Frame(self.drop_card, bg="#16122a")
        opts_row.pack(fill="x", pady=(4, 0))

        chk_apply = tk.Checkbutton(opts_row, text="Set as Desktop Wallpaper Immediately on Import", variable=self.apply_immediately_var, font=("Segoe UI", 8), fg="#ffffff", bg="#16122a", selectcolor="#0c0817", activebackground="#16122a", activeforeground="#ffffff")
        chk_apply.pack(side="left")

        chk_filter = tk.Checkbutton(opts_row, text="Lock Rotation to Custom Wallpapers", variable=self.filter_to_custom_var, font=("Segoe UI", 8), fg="#b8b5cb", bg="#16122a", selectcolor="#0c0817", activebackground="#16122a", activeforeground="#ffffff")
        chk_filter.pack(side="left", padx=16)

        # Gallery Header Row
        gal_head_row = tk.Frame(tab, bg="#0c0a17")
        gal_head_row.pack(fill="x", pady=(4, 2))

        self.lbl_custom_count = tk.Label(gal_head_row, text="📁 YOUR CUSTOM WALLPAPERS (0 Installed)", font=("Segoe UI", 9, "bold"), fg="#ffe600", bg="#0c0a17")
        self.lbl_custom_count.pack(side="left")

        btn_refresh_custom = tk.Button(gal_head_row, text="🔄 Refresh", font=("Segoe UI", 7, "bold"), bg="#1f183d", fg="#00f5d4", relief="flat", cursor="hand2", padx=8, pady=2, command=self.refresh_custom_wallpapers_grid)
        btn_refresh_custom.pack(side="right")
        add_hover(btn_refresh_custom, "#1f183d", "#2d2358")

        # Scrollable Custom Grid
        self.custom_scroll_canvas = tk.Canvas(tab, bg="#0c0a17", highlightthickness=0)
        custom_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.custom_scroll_canvas.yview)
        self.custom_grid_frame = tk.Frame(self.custom_scroll_canvas, bg="#0c0a17")

        self.custom_grid_frame.bind(
            "<Configure>",
            lambda e: self.custom_scroll_canvas.configure(scrollregion=self.custom_scroll_canvas.bbox("all"))
        )

        self.custom_scroll_window = self.custom_scroll_canvas.create_window((0, 0), window=self.custom_grid_frame, anchor="nw")
        self.custom_scroll_canvas.configure(yscrollcommand=custom_scrollbar.set)

        self.custom_scroll_canvas.pack(side="left", fill="both", expand=True)
        custom_scrollbar.pack(side="right", fill="y")

        self.custom_scroll_canvas.bind('<Configure>', lambda e: self.custom_scroll_canvas.itemconfig(self.custom_scroll_window, width=e.width))

    def refresh_custom_wallpapers_grid(self):
        if not hasattr(self, "custom_grid_frame"):
            return

        for widget in self.custom_grid_frame.winfo_children():
            widget.destroy()

        self.custom_img_refs = []
        self.gal_current_page = 0
        self.gal_page_size = 24
        wps = anime_auto_engine.get_category_wallpapers("12_Custom_Wallpapers")
        self.custom_wallpapers_list = wps

        count_text = f"📁 YOUR CUSTOM WALLPAPERS ({len(wps)} Installed)"
        if hasattr(self, "lbl_custom_count"):
            self.lbl_custom_count.config(text=count_text)

        if not wps:
            empty_card = tk.Frame(self.custom_grid_frame, bg="#16122a", padx=24, pady=24, highlightbackground="#3d2c60", highlightthickness=1)
            empty_card.pack(fill="x", pady=16, padx=10)

            tk.Label(empty_card, text="🌸 No Custom Wallpapers Added Yet", font=("Segoe UI", 11, "bold"), fg="#ffffff", bg="#16122a").pack()
            tk.Label(empty_card, text="Drag & drop any anime image, GIF, or folder here, or click '+ Add Images / GIFs' above.\nThey will immediately appear here and can be applied to your desktop with 1 click!", font=("Segoe UI", 8), fg="#b8b5cb", bg="#16122a", justify="center").pack(pady=6)

            btn_quick_add = tk.Button(empty_card, text="➕ Browse & Add Anime Wallpaper Now", font=("Segoe UI", 8, "bold"), bg="#00b4d8", fg="#0c0817", relief="flat", cursor="hand2", padx=12, pady=5, command=self.import_custom_images)
            btn_quick_add.pack(pady=(4, 0))
            add_hover(btn_quick_add, "#00b4d8", "#00f5d4")
            return

        cols = 3
        for idx, wp_path in enumerate(wps):
            r = idx // cols
            c = idx % cols

            is_active = (self.active_wallpaper_path and os.path.abspath(wp_path) == os.path.abspath(self.active_wallpaper_path))
            border_color = "#00f5d4" if is_active else "#2d224e"
            border_thick = 2 if is_active else 1

            card = tk.Frame(self.custom_grid_frame, bg="#16122a", padx=8, pady=8, highlightbackground=border_color, highlightthickness=border_thick)
            card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            self.custom_grid_frame.grid_columnconfigure(c, weight=1)

            if is_active:
                tk.Label(card, text="⭐ ACTIVE DESKTOP", font=("Segoe UI", 7, "bold"), fg="#0c0817", bg="#00f5d4", padx=4).pack(anchor="w", pady=(0, 4))

            lbl_thumb = tk.Label(card, bg="#0c0817", width=22, height=7, cursor="hand2")
            lbl_thumb.pack(fill="x")

            tk_im = self.get_thumbnail(wp_path, size=(180, 100))
            if tk_im:
                self.custom_img_refs.append(tk_im)
                lbl_thumb.config(image=tk_im)
            else:
                lbl_thumb.config(text="Anime WP", fg="#00f5d4")

            lbl_thumb.bind("<Button-1>", lambda e, p=wp_path: self.apply_specific_wallpaper(p))
            lbl_thumb.bind("<Double-Button-1>", lambda e, p=wp_path: self.apply_specific_wallpaper(p))

            base = os.path.basename(wp_path)
            short_name = (base[:22] + "...") if len(base) > 25 else base
            lbl_name = tk.Label(card, text=short_name, font=("Segoe UI", 8, "italic"), fg="#ffffff", bg="#16122a")
            lbl_name.pack(anchor="w", pady=(4, 2))

            btn_box = tk.Frame(card, bg="#16122a")
            btn_box.pack(fill="x", pady=(2, 0))

            btn_set = tk.Button(btn_box, text="🚀 Set Desktop", font=("Segoe UI", 7, "bold"), bg="#2a9d8f", fg="#ffffff", relief="flat", cursor="hand2", padx=6, pady=2, command=lambda p=wp_path: self.apply_specific_wallpaper(p))
            btn_set.pack(side="left", expand=True, fill="x", padx=(0, 2))
            add_hover(btn_set, "#2a9d8f", "#34b8a7")

            btn_del = tk.Button(btn_box, text="🗑️", font=("Segoe UI", 7), bg="#4a1525", fg="#ff4d6d", relief="flat", cursor="hand2", padx=4, pady=2, command=lambda p=wp_path: self.delete_custom_wallpaper(p))
            btn_del.pack(side="right")
            add_hover(btn_del, "#4a1525", "#6b1e35")

    def delete_custom_wallpaper(self, path):
        fname = os.path.basename(path)
        if messagebox.askyesno("Delete Wallpaper", f"Are you sure you want to remove '{fname}' from custom wallpapers?"):
            try:
                if os.path.exists(path):
                    os.remove(path)
                self.refresh_custom_wallpapers_grid()
                self.load_gallery_thumbnails()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")

    def open_custom_folder_explorer(self):
        dest_dir = os.path.join(BASE_DIR, "wallpapers", "collection", "12_Custom_Wallpapers")
        os.makedirs(dest_dir, exist_ok=True)
        os.startfile(dest_dir)

    def handle_drag_drop_files(self, filenames):
        if not filenames:
            return

        valid_img_exts = ('.jpg', '.png', '.jpeg', '.webp', '.bmp', '.gif')
        valid_vid_exts = ('.mp4', '.webm', '.mkv', '.avi')

        dest_dir = os.path.join(BASE_DIR, "wallpapers", "collection", "12_Custom_Wallpapers")
        os.makedirs(dest_dir, exist_ok=True)

        imported_files = []
        video_count = 0

        for item in filenames:
            if isinstance(item, bytes):
                try:
                    item_path = item.decode('utf-8')
                except Exception:
                    item_path = item.decode('mbcs', errors='ignore')
            else:
                item_path = str(item)

            item_path = item_path.strip().strip('"')
            if not os.path.exists(item_path):
                continue

            if os.path.isdir(item_path):
                for root, _, files in os.walk(item_path):
                    for f in files:
                        p = os.path.join(root, f)
                        if f.lower().endswith(valid_img_exts):
                            try:
                                tgt = os.path.join(dest_dir, f)
                                shutil.copy2(p, tgt)
                                imported_files.append(tgt)
                            except Exception:
                                pass
                        elif f.lower().endswith(valid_vid_exts):
                            try:
                                import video_processor
                                vid_dest = os.path.join(BASE_DIR, "videos", "transitions", f)
                                shutil.copy2(p, vid_dest)
                                frames = video_processor.extract_frames_from_video(vid_dest, max_frames=3)
                                for fr in frames:
                                    tgt = os.path.join(dest_dir, os.path.basename(fr))
                                    shutil.copy2(fr, tgt)
                                    imported_files.append(tgt)
                                video_count += 1
                            except Exception:
                                pass
            elif os.path.isfile(item_path):
                f = os.path.basename(item_path)
                if item_path.lower().endswith(valid_img_exts):
                    try:
                        tgt = os.path.join(dest_dir, f)
                        shutil.copy2(item_path, tgt)
                        imported_files.append(tgt)
                    except Exception:
                        pass
                elif item_path.lower().endswith(valid_vid_exts):
                    try:
                        import video_processor
                        vid_dest = os.path.join(BASE_DIR, "videos", "transitions", f)
                        shutil.copy2(item_path, vid_dest)
                        frames = video_processor.extract_frames_from_video(vid_dest, max_frames=3)
                        for fr in frames:
                            tgt = os.path.join(dest_dir, os.path.basename(fr))
                            shutil.copy2(fr, tgt)
                            imported_files.append(tgt)
                        video_count += 1
                    except Exception:
                        pass

        if not imported_files and video_count == 0:
            messagebox.showwarning("Import", "No supported image, GIF, or video files found.")
            return

        self.refresh_custom_wallpapers_grid()
        self.load_gallery_thumbnails()
        self.show_tab("custom")

        if self.apply_immediately_var.get() and imported_files:
            first_wp = imported_files[0]
            self.apply_specific_wallpaper(first_wp)

        if self.filter_to_custom_var.get():
            anime_settings.update_setting("anime_filter", "12_Custom_Wallpapers")

        msg = f"🎉 Successfully added {len(imported_files)} custom wallpaper(s)!"
        if video_count > 0:
            msg += f"\n🎬 Extracted 4K frames from {video_count} video loop(s)."
        if self.apply_immediately_var.get() and imported_files:
            msg += f"\n🚀 Desktop wallpaper set to: {os.path.basename(imported_files[0])}"
        messagebox.showinfo("Wallpapers Added", msg)

    def import_custom_images(self):
        files = filedialog.askopenfilenames(
            title="Select Anime Wallpapers or GIFs to Add",
            filetypes=[
                ("Image & Animated Files", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"),
                ("All Files", "*.*")
            ]
        )
        if files:
            self.handle_drag_drop_files(files)

    def import_custom_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Anime Wallpapers")
        if folder:
            self.handle_drag_drop_files([folder])

    def import_custom_video(self):
        files = filedialog.askopenfilenames(
            title="Select Anime Video Loops (4K Frame Extraction)",
            filetypes=[
                ("Video Files", "*.mp4 *.webm *.mkv *.avi"),
                ("All Files", "*.*")
            ]
        )
        if files:
            self.handle_drag_drop_files(files)

    # ========================== TAB 3: 4K WALLPAPER GALLERY (EXPANDED GRID) ==========================
    def build_gallery_tab(self):
        tab = tk.Frame(self.content_area, bg="#0c0a17")
        self.tabs["gallery"] = tab

        tk.Label(tab, text="🖼️ 4K UHD ANIME WALLPAPER GALLERY", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0c0a17").pack(anchor="w", pady=(0, 4))
        tk.Label(tab, text="Browse 301+ pristine 4K/5K/8K widescreen masterpieces. Click any thumbnail to apply immediately to your desktop.", font=("Segoe UI", 8), fg="#b8b5cb", bg="#0c0a17").pack(anchor="w", pady=(0, 8))

        # Top Control Card
        top_card = tk.Frame(tab, bg="#16122a", padx=12, pady=10, highlightbackground="#ffe600", highlightthickness=1)
        top_card.pack(fill="x", pady=(0, 8))

        cat_row = tk.Frame(top_card, bg="#16122a")
        cat_row.pack(fill="x")

        tk.Label(cat_row, text="Select Anime Series:", font=("Segoe UI", 8, "bold"), fg="#ffe600", bg="#16122a").pack(side="left")

        self.gallery_cat_options = [("🌐 All Anime Universes (301+ Masterpieces)", "all")]
        for k, v in anime_auto_engine.ANIME_CATALOG.items():
            count = len(anime_auto_engine.get_category_wallpapers(k))
            self.gallery_cat_options.append((f"{v['title']} ({count} Wallpapers)", k))

        self.gallery_combo = ttk.Combobox(cat_row, values=[opt[0] for opt in self.gallery_cat_options], state="readonly", width=42, font=("Segoe UI", 8))
        cur_cat = self.settings.get("anime_filter", "all")
        for i, opt in enumerate(self.gallery_cat_options):
            if opt[1] == cur_cat:
                self.gallery_combo.current(i)
                break
        if not self.gallery_combo.get():
            self.gallery_combo.current(0)
        self.gallery_combo.bind("<<ComboboxSelected>>", lambda e: self.load_gallery_thumbnails())
        self.gallery_combo.pack(side="left", padx=6)

        btn_lock_cat = tk.Button(cat_row, text="Lock Rotation to Series", font=("Segoe UI", 8, "bold"), bg="#2a9d8f", fg="#ffffff", relief="flat", cursor="hand2", padx=8, pady=2, command=self.save_gallery_filter)
        btn_lock_cat.pack(side="left", padx=2)
        add_hover(btn_lock_cat, "#2a9d8f", "#34b8a7")

        btn_open_folder = tk.Button(cat_row, text="📁 Open in Explorer", font=("Segoe UI", 8), bg="#221e3b", fg="#00f5d4", relief="flat", cursor="hand2", padx=8, pady=2, command=lambda: os.startfile(os.path.join(BASE_DIR, "wallpapers", "collection")))
        btn_open_folder.pack(side="right")
        add_hover(btn_open_folder, "#221e3b", "#2f2a52")

        # Pagination & Status Row
        pag_row = tk.Frame(tab, bg="#0c0a17")
        pag_row.pack(fill="x", pady=(2, 4))

        self.btn_gal_prev = tk.Button(pag_row, text="◀ Prev Page", font=("Segoe UI", 8, "bold"), bg="#1f183d", fg="#00f5d4", relief="flat", cursor="hand2", padx=10, pady=2, command=self.gallery_prev_page)
        self.btn_gal_prev.pack(side="left")
        add_hover(self.btn_gal_prev, "#1f183d", "#2d2358")

        self.lbl_gal_status = tk.Label(pag_row, text="Showing wallpapers...", font=("Segoe UI", 8, "bold"), fg="#ffe600", bg="#0c0a17")
        self.lbl_gal_status.pack(side="left", padx=12)

        self.btn_gal_next = tk.Button(pag_row, text="Next Page ▶", font=("Segoe UI", 8, "bold"), bg="#1f183d", fg="#00f5d4", relief="flat", cursor="hand2", padx=10, pady=2, command=self.gallery_next_page)
        self.btn_gal_next.pack(side="left")
        add_hover(self.btn_gal_next, "#1f183d", "#2d2358")

        # Scrollable Gallery Grid Canvas
        self.gal_canvas = tk.Canvas(tab, bg="#0c0a17", highlightthickness=0)
        gal_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.gal_canvas.yview)
        self.gal_grid_frame = tk.Frame(self.gal_canvas, bg="#0c0a17")

        self.gal_grid_frame.bind(
            "<Configure>",
            lambda e: self.gal_canvas.configure(scrollregion=self.gal_canvas.bbox("all"))
        )
        self.gal_scroll_window = self.gal_canvas.create_window((0, 0), window=self.gal_grid_frame, anchor="nw")
        self.gal_canvas.configure(yscrollcommand=gal_scrollbar.set)

        self.gal_canvas.pack(side="left", fill="both", expand=True)
        gal_scrollbar.pack(side="right", fill="y")
        self.gal_canvas.bind('<Configure>', lambda e: self.gal_canvas.itemconfig(self.gal_scroll_window, width=e.width))

    def gallery_prev_page(self):
        if self.gal_current_page > 0:
            self.gal_current_page -= 1
            self.load_gallery_thumbnails(reset_page=False)

    def gallery_next_page(self):
        self.gal_current_page += 1
        self.load_gallery_thumbnails(reset_page=False)

    def load_gallery_thumbnails(self, reset_page=True):
        if not hasattr(self, "gal_grid_frame"):
            return

        if reset_page:
            self.gal_current_page = 0

        for widget in self.gal_grid_frame.winfo_children():
            widget.destroy()

        idx = self.gallery_combo.current()
        cat_id = self.gallery_cat_options[idx][1] if (0 <= idx < len(self.gallery_cat_options)) else "all"

        wps = []
        if cat_id == "all":
            for k in anime_auto_engine.ANIME_CATALOG.keys():
                wps.extend(anime_auto_engine.get_category_wallpapers(k))
        else:
            wps = anime_auto_engine.get_category_wallpapers(cat_id)

        total_wps = len(wps)
        total_pages = max(1, (total_wps + self.gal_page_size - 1) // self.gal_page_size)
        if self.gal_current_page >= total_pages:
            self.gal_current_page = total_pages - 1
        if self.gal_current_page < 0:
            self.gal_current_page = 0

        start_idx = self.gal_current_page * self.gal_page_size
        end_idx = min(start_idx + self.gal_page_size, total_wps)
        display_wps = wps[start_idx:end_idx]

        if hasattr(self, "lbl_gal_status"):
            self.lbl_gal_status.config(
                text=f"Page {self.gal_current_page + 1} of {total_pages} (Showing {start_idx + 1}-{end_idx} of {total_wps} Wallpapers)"
            )
        if hasattr(self, "btn_gal_prev"):
            self.btn_gal_prev.config(state="normal" if self.gal_current_page > 0 else "disabled")
        if hasattr(self, "btn_gal_next"):
            self.btn_gal_next.config(state="normal" if self.gal_current_page < total_pages - 1 else "disabled")

        self.gallery_img_refs = []
        cols = 4

        for i, wp_path in enumerate(display_wps):
            r = i // cols
            c = i % cols

            is_active = (self.active_wallpaper_path and os.path.abspath(wp_path) == os.path.abspath(self.active_wallpaper_path))
            border_c = "#00f5d4" if is_active else "#281e42"
            border_th = 2 if is_active else 1

            card = tk.Frame(self.gal_grid_frame, bg="#16122a", padx=6, pady=6, highlightbackground=border_c, highlightthickness=border_th)
            card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
            self.gal_grid_frame.grid_columnconfigure(c, weight=1)

            lbl_thumb = tk.Label(card, bg="#0c0817", width=18, height=6, cursor="hand2")
            lbl_thumb.pack(fill="x")

            tk_im = self.get_thumbnail(wp_path, size=(160, 90))
            if tk_im:
                self.gallery_img_refs.append(tk_im)
                lbl_thumb.config(image=tk_im)
            else:
                lbl_thumb.config(text="4K Anime", fg="#00f5d4")

            lbl_thumb.bind("<Button-1>", lambda e, p=wp_path: self.apply_specific_wallpaper(p))
            lbl_thumb.bind("<Double-Button-1>", lambda e, p=wp_path: self.apply_specific_wallpaper(p))

            base = os.path.basename(wp_path)
            short_name = (base[:16] + "...") if len(base) > 19 else base
            tk.Label(card, text=short_name, font=("Segoe UI", 7, "italic"), fg="#b8b5cb", bg="#16122a").pack(anchor="w", pady=(2, 2))

            btn_apply = tk.Button(card, text="🚀 Set Desktop", font=("Segoe UI", 7, "bold"), bg="#2a9d8f", fg="#ffffff", relief="flat", cursor="hand2", pady=1, command=lambda p=wp_path: self.apply_specific_wallpaper(p))
            btn_apply.pack(fill="x")
            add_hover(btn_apply, "#2a9d8f", "#34b8a7")

    def apply_specific_wallpaper(self, path):
        anime_auto_engine.set_wallpaper_win32(path)
        self.active_wallpaper_path = path
        self.refresh_current_display()
        # Refresh borders
        if hasattr(self, "refresh_custom_wallpapers_grid"):
            self.refresh_custom_wallpapers_grid()
        messagebox.showinfo("Applied", f"Wallpaper applied to desktop:\n{os.path.basename(path)}")

    def save_gallery_filter(self):
        idx = self.gallery_combo.current()
        cat_id = self.gallery_cat_options[idx][1] if (0 <= idx < len(self.gallery_cat_options)) else "all"
        anime_settings.update_setting("anime_filter", cat_id)
        self.settings["anime_filter"] = cat_id
        messagebox.showinfo("Theme Applied", f"Active Anime Theme Filter set to:\n{self.gallery_cat_options[idx][0]}")

    # ========================== TAB 4: TIMER & SCHEDULE ==========================
    def build_timer_tab(self):
        tab = tk.Frame(self.content_area, bg="#0c0a17")
        self.tabs["timer"] = tab

        tk.Label(tab, text="⏱️ TIMER & LONG-TERM SCHEDULER", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0c0a17").pack(anchor="w", pady=(0, 4))
        tk.Label(tab, text="Set wallpaper rotation intervals from 5 seconds up to 1 Year+. Persists across computer reboots.", font=("Segoe UI", 8), fg="#b8b5cb", bg="#0c0a17").pack(anchor="w", pady=(0, 8))

        card = tk.Frame(tab, bg="#16122a", padx=16, pady=14, highlightbackground="#00f5d4", highlightthickness=1)
        card.pack(fill="x", pady=4)

        # Quick Short Presets
        tk.Label(card, text="Quick Short Presets:", font=("Segoe UI", 8, "bold"), fg="#00f5d4", bg="#16122a").pack(anchor="w")
        row_s = tk.Frame(card, bg="#16122a")
        row_s.pack(fill="x", pady=(3, 8))
        for lbl, v, u in [("10s", 10, "seconds"), ("30s", 30, "seconds"), ("1m", 1, "minutes"), ("5m", 5, "minutes"), ("15m", 15, "minutes"), ("30m", 30, "minutes")]:
            b = tk.Button(row_s, text=lbl, font=("Segoe UI", 7, "bold"), bg="#1f1a38", fg="#00f5d4", relief="flat", cursor="hand2", padx=8, pady=3,
                          command=lambda val=v, unt=u: self.set_timer_preset(val, unt))
            b.pack(side="left", padx=2)
            add_hover(b, "#1f1a38", "#2c2452")

        # Quick Long Presets
        tk.Label(card, text="Quick Long Presets (Days, Months, Years):", font=("Segoe UI", 8, "bold"), fg="#ffe600", bg="#16122a").pack(anchor="w")
        row_l = tk.Frame(card, bg="#16122a")
        row_l.pack(fill="x", pady=(3, 10))
        for lbl, v, u in [("1 Hour", 1, "hours"), ("6 Hours", 6, "hours"), ("1 Day", 1, "days"), ("1 Week", 1, "weeks"), ("1 Month", 1, "months"), ("1 Year", 1, "years")]:
            b = tk.Button(row_l, text=lbl, font=("Segoe UI", 7, "bold"), bg="#2d1b4e", fg="#ffe600", relief="flat", cursor="hand2", padx=8, pady=3,
                          command=lambda val=v, unt=u: self.set_timer_preset(val, unt))
            b.pack(side="left", padx=2)
            add_hover(b, "#2d1b4e", "#3f266d")

        # Custom Input
        custom_frame = tk.Frame(card, bg="#16122a")
        custom_frame.pack(fill="x", pady=(4, 6))

        tk.Label(custom_frame, text="Exact Custom Duration:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#16122a").pack(side="left")
        self.timer_val_var = tk.StringVar(value=str(self.settings.get("interval_value", 30)))
        self.timer_val_var.trace_add("write", lambda *a: self.update_timer_preview())

        self.entry_timer_val = tk.Entry(custom_frame, textvariable=self.timer_val_var, font=("Segoe UI", 9, "bold"), width=8, bg="#0c0817", fg="#00f5d4", insertbackground="#ffffff")
        self.entry_timer_val.pack(side="left", padx=8)

        self.timer_unit_combo = ttk.Combobox(custom_frame, values=["Seconds", "Minutes", "Hours", "Days", "Weeks", "Months", "Years"], state="readonly", width=10, font=("Segoe UI", 8, "bold"))
        cur_u = self.settings.get("interval_unit", "seconds").capitalize()
        self.timer_unit_combo.set(cur_u if cur_u in self.timer_unit_combo['values'] else "Seconds")
        self.timer_unit_combo.bind("<<ComboboxSelected>>", lambda e: self.update_timer_preview())
        self.timer_unit_combo.pack(side="left")

        # Live Target Date Preview
        self.lbl_timer_target = tk.Label(card, text="📅 Next Change Scheduled: Calculating...", font=("Segoe UI", 9, "bold"), fg="#ffbe0b", bg="#16122a")
        self.lbl_timer_target.pack(anchor="w", pady=(8, 4))

        # Windows Startup Toggle
        self.startup_var = tk.BooleanVar(value=self.settings.get("run_at_startup", False))
        chk_start = tk.Checkbutton(
            card,
            text="🚀 Start Anime Studio with Windows (Keeps schedule active 24/7 across months/years)",
            variable=self.startup_var,
            font=("Segoe UI", 8, "bold"),
            fg="#00f5d4",
            bg="#16122a",
            selectcolor="#16122a",
            activebackground="#16122a",
            activeforeground="#ffe600"
        )
        chk_start.pack(anchor="w", pady=(6, 2))

        btn_save_timer = tk.Button(
            card,
            text="💾 SAVE & APPLY SCHEDULE",
            font=("Segoe UI", 9, "bold"),
            bg="#2a9d8f",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=7,
            command=self.save_timer_schedule
        )
        btn_save_timer.pack(fill="x", pady=(10, 0))
        add_hover(btn_save_timer, "#2a9d8f", "#34b8a7")

    def set_timer_preset(self, val, unit):
        self.timer_val_var.set(str(val))
        self.timer_unit_combo.set(unit.capitalize())
        self.update_timer_preview()

    def update_timer_preview(self):
        try:
            val = float(self.timer_val_var.get())
            unit = self.timer_unit_combo.get().lower()
            secs = anime_settings.convert_to_seconds(val, unit)
            human_str = anime_settings.format_seconds_to_human(secs)

            target_ts = time.time() + secs
            target_str = time.strftime("%a, %b %d, %Y at %I:%M:%S %p", time.localtime(target_ts))
            self.lbl_timer_target.config(text=f"📅 Next Change: {target_str} (Every {human_str})")
        except:
            self.lbl_timer_target.config(text="📅 Enter a valid number")

    def save_timer_schedule(self):
        try:
            val = float(self.timer_val_var.get())
            if val <= 0:
                val = 5
        except:
            val = 30

        unit = self.timer_unit_combo.get().lower()
        secs = anime_settings.convert_to_seconds(val, unit)
        now = time.time()

        anime_settings.update_setting("interval_value", val)
        anime_settings.update_setting("interval_unit", unit)
        anime_settings.update_setting("interval_seconds", secs)
        anime_settings.update_setting("last_change_timestamp", now)
        anime_settings.update_setting("next_change_timestamp", now + secs)

        is_startup = self.startup_var.get()
        anime_settings.set_windows_startup(is_startup)

        human_time = anime_settings.format_seconds_to_human(secs)
        messagebox.showinfo("Schedule Applied", f"Wallpaper rotation schedule updated!\n\nInterval: Every {human_time}\nStartup Active: {is_startup}")

    # ========================== TAB 5: AUDIO & MUSIC ==========================
    def build_audio_tab(self):
        tab = tk.Frame(self.content_area, bg="#0c0a17")
        self.tabs["audio"] = tab

        tk.Label(tab, text="🎵 MUSIC & VOICE STUDIO", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0c0a17").pack(anchor="w", pady=(0, 4))
        tk.Label(tab, text="Choose viral anthems, authentic Japanese character dialogue, or import personal MP3s.", font=("Segoe UI", 8), fg="#b8b5cb", bg="#0c0a17").pack(anchor="w", pady=(0, 8))

        card = tk.Frame(tab, bg="#16122a", padx=16, pady=12, highlightbackground="#7209b7", highlightthickness=1)
        card.pack(fill="x", pady=4)

        self.audio_mode_var = tk.StringVar(value=self.settings.get("song_mode", "match_anime"))

        modes = [
            ("Dynamic: Anime Viral Themes (Overtaken, Silhouette, Lost in Paradise, etc.)", "match_anime"),
            ("Dynamic: Original Japanese Voice Climax (Gojo Domain, Zenitsu Thunder, Gear 5)", "match_voice"),
            ("Lock to Specific Audio Track (Select below)", "specific_song"),
            ("Shuffle All Tracks Randomly", "shuffle_all"),
            ("Silent / Mute (Wallpapers only, No sound)", "mute")
        ]

        for text, val in modes:
            tk.Radiobutton(
                card, text=text, value=val, variable=self.audio_mode_var,
                font=("Segoe UI", 8), bg="#16122a", fg="#ffffff", selectcolor="#7209b7",
                activebackground="#16122a", activeforeground="#ffe600", anchor="w"
            ).pack(fill="x", pady=1)

        picker_row = tk.Frame(card, bg="#16122a")
        picker_row.pack(fill="x", pady=(8, 4))

        tk.Label(picker_row, text="Track List:", font=("Segoe UI", 8, "bold"), fg="#b8b5cb", bg="#16122a").pack(side="left")

        self.tracks_dict = anime_auto_engine.get_all_available_tracks()
        self.track_keys = list(self.tracks_dict.keys())

        self.audio_combo = ttk.Combobox(picker_row, values=[self.tracks_dict[k] for k in self.track_keys], state="readonly", width=42, font=("Segoe UI", 8))
        cur_track = self.settings.get("specific_song", "one_piece_overtaken.mp3")
        for i, k in enumerate(self.track_keys):
            if k == cur_track:
                self.audio_combo.current(i)
                break
        if not self.audio_combo.get() and self.track_keys:
            self.audio_combo.current(0)
        self.audio_combo.pack(side="left", padx=6)

        btn_import_mp3 = tk.Button(
            picker_row,
            text="+ Import MP3",
            font=("Segoe UI", 8, "bold"),
            bg="#2a9d8f",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=2,
            command=self.import_mp3_action
        )
        btn_import_mp3.pack(side="left")
        add_hover(btn_import_mp3, "#2a9d8f", "#34b8a7")

        self.play_full_song_var = tk.BooleanVar(value=self.settings.get("play_full_song", False))
        chk_full = tk.Checkbutton(
            card,
            text="🎵 Play Full Song in Background (Keep playing after transition finishes)",
            variable=self.play_full_song_var,
            font=("Segoe UI", 8),
            fg="#b8b5cb",
            bg="#16122a",
            selectcolor="#16122a",
            activebackground="#16122a",
            activeforeground="#00f5d4"
        )
        chk_full.pack(anchor="w", pady=(6, 2))

        test_row = tk.Frame(card, bg="#16122a")
        test_row.pack(fill="x", pady=(8, 2))

        btn_play = tk.Button(test_row, text="▶️ Preview Selected Track", font=("Segoe UI", 8, "bold"), bg="#3a0ca3", fg="#ffffff", relief="flat", cursor="hand2", padx=10, pady=3, command=self.preview_selected_audio)
        btn_play.pack(side="left", padx=(0, 4))
        add_hover(btn_play, "#3a0ca3", "#4c16cb")

        btn_stop = tk.Button(test_row, text="⏹️ Stop Preview", font=("Segoe UI", 8), bg="#4a4e69", fg="#ffffff", relief="flat", cursor="hand2", padx=10, pady=3, command=anime_auto_engine.stop_audio)
        btn_stop.pack(side="left")
        add_hover(btn_stop, "#4a4e69", "#5c6082")

        btn_save_audio = tk.Button(card, text="💾 SAVE & APPLY AUDIO SETTINGS", font=("Segoe UI", 9, "bold"), bg="#2a9d8f", fg="#ffffff", relief="flat", cursor="hand2", pady=7, command=self.save_audio_settings)
        btn_save_audio.pack(fill="x", pady=(10, 0))
        add_hover(btn_save_audio, "#2a9d8f", "#34b8a7")

    def import_mp3_action(self):
        file_path = filedialog.askopenfilename(title="Select Custom Audio File", filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a")])
        if file_path:
            dest_dir = os.path.join(BASE_DIR, "audio", "viral_songs")
            os.makedirs(dest_dir, exist_ok=True)
            fname = os.path.basename(file_path)
            dest_path = os.path.join(dest_dir, fname)
            try:
                shutil.copy2(file_path, dest_path)
                messagebox.showinfo("Imported", f"Added '{fname}' to Anime Audio Library!")
                self.tracks_dict = anime_auto_engine.get_all_available_tracks()
                self.track_keys = list(self.tracks_dict.keys())
                self.audio_combo['values'] = [self.tracks_dict[k] for k in self.track_keys]
                for i, k in enumerate(self.track_keys):
                    if k == fname:
                        self.audio_combo.current(i)
                        self.audio_mode_var.set("specific_song")
                        break
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy song: {e}")

    def preview_selected_audio(self):
        idx = self.audio_combo.current()
        if 0 <= idx < len(self.track_keys):
            track_key = self.track_keys[idx]
            p = anime_auto_engine.resolve_audio_path(track_key)
            if p:
                anime_auto_engine.play_audio(p, duration_limit=15)

    def save_audio_settings(self):
        idx = self.audio_combo.current()
        track_key = self.track_keys[idx] if (0 <= idx < len(self.track_keys)) else "one_piece_overtaken.mp3"
        mode = self.audio_mode_var.get()

        anime_settings.update_setting("song_mode", mode)
        anime_settings.update_setting("specific_song", track_key)
        anime_settings.update_setting("play_full_song", self.play_full_song_var.get())
        anime_settings.update_setting("sound_enabled", (mode != "mute"))

        messagebox.showinfo("Audio Saved", f"Audio Mode updated to: {mode}")

    # ========================== TAB 6: ANIME PORTALS ==========================
    def build_portals_tab(self):
        tab = tk.Frame(self.content_area, bg="#0c0a17")
        self.tabs["portals"] = tab

        tk.Label(tab, text="🌐 ANIME STREAMING & WEB PORTALS", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0c0a17").pack(anchor="w", pady=(0, 4))
        tk.Label(tab, text="1-Click fast access to official anime, manga readers, downloads, and 24/7 lofi radio.", font=("Segoe UI", 8), fg="#b8b5cb", bg="#0c0a17").pack(anchor="w", pady=(0, 8))

        portal_container = tk.Frame(tab, bg="#0c0a17")
        portal_container.pack(fill="both", expand=True)

        for i, (name, desc, url, color) in enumerate(PORTALS):
            r = i // 2
            c = i % 2
            p_card = tk.Frame(portal_container, bg="#16122a", padx=12, pady=12, highlightbackground=color, highlightthickness=1)
            p_card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            portal_container.grid_columnconfigure(c, weight=1)

            lbl_p_name = tk.Label(p_card, text=name, font=("Segoe UI", 10, "bold"), fg=color, bg="#16122a")
            lbl_p_name.pack(anchor="w")

            lbl_p_desc = tk.Label(p_card, text=desc, font=("Segoe UI", 8), fg="#b8b5cb", bg="#16122a", wraplength=280, justify="left")
            lbl_p_desc.pack(anchor="w", pady=(2, 6))

            btn_open = tk.Button(
                p_card,
                text="🚀 Open Website",
                font=("Segoe UI", 8, "bold"),
                bg=color,
                fg="#000000" if color in ["#ffe600", "#00f5d4"] else "#ffffff",
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=3,
                command=lambda u=url: webbrowser.open(u)
            )
            btn_open.pack(anchor="w")

    # ========================== TAB 7: PREFERENCES & SETTINGS ==========================
    def build_settings_tab(self):
        tab = tk.Frame(self.content_area, bg="#0c0a17")
        self.tabs["settings"] = tab

        tk.Label(tab, text="⚙️ APP PREFERENCES & SYSTEM CONTROLS", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#0c0a17").pack(anchor="w", pady=(0, 4))

        card = tk.Frame(tab, bg="#16122a", padx=16, pady=12, highlightbackground="#3d2c60", highlightthickness=1)
        card.pack(fill="x", pady=4)

        self.anim_toggle_var = tk.BooleanVar(value=self.settings.get("show_visual_transition", True))
        chk_trans = tk.Checkbutton(
            card,
            text="✨ Enable Cinematic Animated Visual Overlay on Wallpaper Change",
            variable=self.anim_toggle_var,
            font=("Segoe UI", 8, "bold"),
            fg="#ffe600",
            bg="#16122a",
            selectcolor="#16122a",
            activebackground="#16122a",
            activeforeground="#00f5d4"
        )
        chk_trans.pack(anchor="w", pady=2)

        trans_dur_row = tk.Frame(card, bg="#16122a")
        trans_dur_row.pack(fill="x", padx=16, pady=2)

        tk.Label(trans_dur_row, text="Transition Duration:", font=("Segoe UI", 7), fg="#b8b5cb", bg="#16122a").pack(side="left")
        self.trans_dur_var = tk.IntVar(value=self.settings.get("transition_duration", 5))
        for d_lbl, d_val in [("5s Cinematic", 5), ("3s Fast", 3), ("1s Flash", 1), ("0s Instant", 0)]:
            tk.Radiobutton(trans_dur_row, text=d_lbl, value=d_val, variable=self.trans_dur_var, font=("Segoe UI", 7), bg="#16122a", fg="#ffffff", selectcolor="#ff0055", activebackground="#16122a", activeforeground="#00f5d4").pack(side="left", padx=3)

        hud_box = tk.Frame(card, bg="#16122a")
        hud_box.pack(fill="x", pady=(10, 4))

        tk.Label(hud_box, text="🪟 Floating Desktop Mini-Widget:", font=("Segoe UI", 8, "bold"), fg="#00f5d4", bg="#16122a").pack(side="left")
        btn_hud_action = tk.Button(hud_box, text="Toggle Mini-HUD On/Off", font=("Segoe UI", 7, "bold"), bg="#7209b7", fg="#ffffff", relief="flat", cursor="hand2", padx=8, pady=2, command=self.toggle_mini_hud)
        btn_hud_action.pack(side="left", padx=8)
        add_hover(btn_hud_action, "#7209b7", "#8415d1")

        self.tray_close_var = tk.BooleanVar(value=self.settings.get("minimize_to_tray_on_close", False))
        chk_tray = tk.Checkbutton(
            card,
            text="🔕 Minimize to System Tray instead of Exit when clicking 'X' (Unchecked = Full Exit & Stop)",
            variable=self.tray_close_var,
            font=("Segoe UI", 8),
            fg="#00f5d4",
            bg="#16122a",
            selectcolor="#16122a",
            activebackground="#16122a",
            activeforeground="#ffe600"
        )
        chk_tray.pack(anchor="w", pady=(6, 2))

        btn_save_app = tk.Button(card, text="💾 SAVE APP PREFERENCES", font=("Segoe UI", 9, "bold"), bg="#2a9d8f", fg="#ffffff", relief="flat", cursor="hand2", pady=7, command=self.save_app_preferences)
        btn_save_app.pack(fill="x", pady=(10, 0))
        add_hover(btn_save_app, "#2a9d8f", "#34b8a7")

        # Update & Maintenance Card
        update_card = tk.Frame(tab, bg="#16122a", padx=16, pady=12, highlightbackground="#00b4d8", highlightthickness=1)
        update_card.pack(fill="x", pady=(10, 0))

        tk.Label(update_card, text="🔄 SMART 1-CLICK UPDATER", font=("Segoe UI", 9, "bold"), fg="#00f5d4", bg="#16122a").pack(anchor="w")
        tk.Label(update_card, text="Updates application scripts and features in ~3 seconds. Preserves all 301+ 4K wallpapers and custom user files.", font=("Segoe UI", 8), fg="#b8b5cb", bg="#16122a").pack(anchor="w", pady=(2, 6))

        btn_run_update = tk.Button(
            update_card,
            text="🚀 CHECK & APPLY LATEST UPDATES NOW",
            font=("Segoe UI", 8, "bold"),
            bg="#00b4d8",
            fg="#0c0817",
            activebackground="#00f5d4",
            activeforeground="#0c0817",
            relief="flat",
            cursor="hand2",
            pady=7,
            command=self.trigger_inapp_update
        )
        btn_run_update.pack(fill="x")
        add_hover(btn_run_update, "#00b4d8", "#00f5d4")

        # Emergency Kill Switch Card
        danger_card = tk.Frame(tab, bg="#2a0812", padx=16, pady=12, highlightbackground="#e63946", highlightthickness=1)
        danger_card.pack(fill="x", pady=(12, 0))

        tk.Label(danger_card, text="🛑 EMERGENCY KILL SWITCH", font=("Segoe UI", 9, "bold"), fg="#ff5964", bg="#2a0812").pack(anchor="w")
        tk.Label(danger_card, text="Instantly stop all wallpaper auto-changing, mute all audio, and terminate the application.", font=("Segoe UI", 8), fg="#b8b5cb", bg="#2a0812").pack(anchor="w", pady=(1, 6))

        btn_kill = tk.Button(
            danger_card,
            text="🛑 FORCE STOP EVERYTHING & EXIT APP",
            font=("Segoe UI", 9, "bold"),
            bg="#e63946",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=8,
            command=self.kill_and_exit
        )
        btn_kill.pack(fill="x")
        add_hover(btn_kill, "#e63946", "#c92a37")

    def save_app_preferences(self):
        anime_settings.update_setting("show_visual_transition", self.anim_toggle_var.get())
        anime_settings.update_setting("transition_duration", self.trans_dur_var.get())
        anime_settings.update_setting("minimize_to_tray_on_close", self.tray_close_var.get())
        messagebox.showinfo("Saved", "App preferences updated successfully!")

    def trigger_inapp_update(self):
        update_script = os.path.join(BASE_DIR, "update.ps1")
        if not os.path.exists(update_script):
            messagebox.showerror("Update", "update.ps1 not found in application directory.")
            return

        res = messagebox.askyesno(
            "Update Anime Studio Pro",
            "Do you want to update Anime Studio Pro now?\n\n"
            "• Updates scripts & installs latest features\n• Preserves all 301+ 4K wallpapers\n• Takes ~3-5 seconds"
        )
        if res:
            try:
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", update_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start updater:\n{e}")

    # ========================== ENGINE & TIMER LOOP ==========================
    def update_timer_loop(self):
        latest = anime_settings.load_settings()
        now = time.time()
        next_ts = latest.get("next_change_timestamp", now + 30)
        interval = max(5, latest.get("interval_seconds", 30))

        if self.auto_change_enabled and not self.is_changing:
            remaining = next_ts - now

            if remaining <= 0:
                # Advance timestamp immediately so timer loop never multi-triggers
                latest["next_change_timestamp"] = now + interval
                anime_settings.save_settings(latest)
                self.trigger_change_now(manual=False)
            else:
                human_rem = anime_settings.format_seconds_to_human(remaining)
                self.lbl_dash_timer.config(text=f"⏳ Next 4K Wallpaper: {human_rem}", fg="#ffe600")
                self.lbl_sidebar_timer.config(text=f"⏳ Next: {human_rem}", fg="#ffe600")

                target_str = time.strftime("%a, %b %d %I:%M %p", time.localtime(next_ts))
                self.lbl_dash_next_date.config(text=f"📅 Scheduled: {target_str}")

                w = self.canvas_dash_prog.winfo_width()
                if w < 10:
                    w = 500
                frac = max(0.0, min(1.0, remaining / float(interval)))
                prog_w = int(w * frac)
                self.canvas_dash_prog.coords(self.rect_dash_prog, 0, 0, prog_w, 8)
        elif not self.auto_change_enabled:
            self.lbl_dash_timer.config(text="🔴 Auto-Rotation is currently PAUSED", fg="#ff5964")
            self.lbl_sidebar_timer.config(text="🔴 Paused", fg="#ff5964")
            self.canvas_dash_prog.coords(self.rect_dash_prog, 0, 0, 0, 8)

        self.root.after(1000, self.update_timer_loop)

    def trigger_change_now(self, manual=True):
        if self.is_changing:
            return
        self.is_changing = True
        self.lbl_dash_timer.config(text="🎬 Transitioning 4K Wallpaper...", fg="#00f5d4")

        cur_settings = anime_settings.load_settings()

        def worker():
            wp_path, meta, song_name = anime_auto_engine.change_wallpaper_now(settings=cur_settings, force=manual)
            self.root.after(0, lambda: self.on_change_completed(wp_path, meta, song_name))

        threading.Thread(target=worker, daemon=True).start()

    def on_change_completed(self, wp_path, meta, song_name):
        self.is_changing = False
        self.active_wallpaper_path = wp_path
        self.active_meta = meta
        self.active_song_title = song_name
        self.refresh_current_display()

        latest = anime_settings.load_settings()
        rem = latest.get("next_change_timestamp", time.time() + 30) - time.time()
        self.lbl_dash_timer.config(text=f"⏳ Next 4K Wallpaper: {anime_settings.format_seconds_to_human(rem)}", fg="#ffe600")

    def refresh_current_display(self):
        if self.active_wallpaper_path and "12_Custom_Wallpapers" in self.active_wallpaper_path:
            self.lbl_active_anime.config(text="Custom Anime Collection")
            self.lbl_active_char.config(text="Personal Anime Wallpaper")
        elif self.active_meta:
            self.lbl_active_anime.config(text=self.active_meta.get("title", "Anime Masterpiece"))
            self.lbl_active_char.config(text=self.active_meta.get("char", "Featured Hero"))
        if self.active_song_title:
            self.lbl_active_song.config(text=self.active_song_title)

        if self.active_wallpaper_path and os.path.exists(self.active_wallpaper_path):
            self.lbl_active_wp_name.config(text=os.path.basename(self.active_wallpaper_path))
            try:
                im = Image.open(self.active_wallpaper_path)
                w, h = im.size
                self.lbl_active_res.config(text=f"{w}x{h} UHD 4K")
                im.thumbnail((300, 168), Image.Resampling.LANCZOS)
                self.active_preview_img = ImageTk.PhotoImage(im)
                self.lbl_preview_canvas.config(image=self.active_preview_img, text="")
            except:
                pass

    def toggle_pause(self):
        self.auto_change_enabled = not self.auto_change_enabled
        if self.auto_change_enabled:
            self.btn_pause.config(text="⏸️ PAUSE AUTO", bg="#2a9d8f")
            self.lbl_status_badge.config(text="🟢 AUTO-MODE: ON", fg="#00f5d4")
            anime_settings.update_setting("auto_mode_enabled", True)
            anime_settings.register_next_change()
        else:
            self.btn_pause.config(text="▶️ RESUME AUTO", bg="#e63946")
            self.lbl_status_badge.config(text="🔴 AUTO-MODE: PAUSED", fg="#ff5964")
            self.lbl_dash_timer.config(text="🔴 Auto-Change is currently PAUSED", fg="#ff5964")
            anime_settings.update_setting("auto_mode_enabled", False)
            anime_auto_engine.stop_audio()

    # ========================== FLOATING MINI-HUD ==========================
    def toggle_mini_hud(self):
        self.show_mini_hud = not self.show_mini_hud
        if self.show_mini_hud:
            if not self.mini_hud_window or not tk.Toplevel.winfo_exists(self.mini_hud_window):
                self.create_mini_hud()
            self.btn_hud_toggle.config(text="🪟 HIDE MINI-HUD", bg="#f72585")
        else:
            if self.mini_hud_window and tk.Toplevel.winfo_exists(self.mini_hud_window):
                self.mini_hud_window.destroy()
            self.btn_hud_toggle.config(text="🪟 SHOW MINI-HUD", bg="#7209b7")

    def create_mini_hud(self):
        self.mini_hud_window = tk.Toplevel(self.root)
        self.mini_hud_window.title("⛩️ Mini HUD")
        self.mini_hud_window.overrideredirect(True)
        self.mini_hud_window.attributes("-topmost", True)
        self.mini_hud_window.attributes("-alpha", 0.95)

        sw = self.mini_hud_window.winfo_screenwidth()
        self.mini_hud_window.geometry(f"320x95+{sw - 335}+40")
        self.mini_hud_window.configure(bg="#0c0a18")

        frame = tk.Frame(self.mini_hud_window, bg="#16122a", padx=10, pady=8, highlightbackground="#00f5d4", highlightthickness=1)
        frame.pack(fill="both", expand=True)

        def start_d(e):
            self.mini_hud_window._x = e.x
            self.mini_hud_window._y = e.y
        def do_d(e):
            x = self.mini_hud_window.winfo_pointerx() - self.mini_hud_window._x
            y = self.mini_hud_window.winfo_pointery() - self.mini_hud_window._y
            self.mini_hud_window.geometry(f"+{x}+{y}")

        frame.bind("<Button-1>", start_d)
        frame.bind("<B1-Motion>", do_d)

        top_r = tk.Frame(frame, bg="#16122a")
        top_r.pack(fill="x")
        lbl_hud_title = tk.Label(top_r, text="⛩️ ANIME MINI-HUD", font=("Segoe UI", 7, "bold"), fg="#00f5d4", bg="#16122a")
        lbl_hud_title.pack(side="left")
        lbl_hud_title.bind("<Button-1>", start_d)
        lbl_hud_title.bind("<B1-Motion>", do_d)

        lbl_close = tk.Label(top_r, text="✕", font=("Segoe UI", 8, "bold"), fg="#ff5964", bg="#16122a", cursor="hand2")
        lbl_close.pack(side="right")
        lbl_close.bind("<Button-1>", lambda e: self.toggle_mini_hud())

        self.lbl_mini_anime = tk.Label(frame, text=self.active_meta.get("title", "Anime Masterpiece") if self.active_meta else "Anime Studio", font=("Segoe UI", 8, "bold"), fg="#ffe600", bg="#16122a")
        self.lbl_mini_anime.pack(anchor="w")

        self.lbl_mini_timer = tk.Label(frame, text="Next in: ...", font=("Segoe UI", 8), fg="#00f5d4", bg="#16122a")
        self.lbl_mini_timer.pack(anchor="w")

        def update_mini():
            if self.mini_hud_window and tk.Toplevel.winfo_exists(self.mini_hud_window):
                rem = anime_settings.load_settings().get("next_change_timestamp", time.time() + 30) - time.time()
                self.lbl_mini_timer.config(text=f"⏳ Next 4K Wallpaper: {anime_settings.format_seconds_to_human(rem)}")
                if self.active_meta:
                    self.lbl_mini_anime.config(text=self.active_meta.get("title", "Anime"))
                self.mini_hud_window.after(1000, update_mini)

        update_mini()

    # ========================== SYSTEM TRAY ==========================
    def setup_system_tray(self):
        try:
            im = Image.open(ICON_PATH)
            menu = (
                item("🌸 Next Wallpaper Now", lambda: self.root.after(0, self.trigger_change_now)),
                item("🟢 Pause / Resume Auto", lambda: self.root.after(0, self.toggle_pause)),
                item("🪟 Toggle Mini-HUD", lambda: self.root.after(0, self.toggle_mini_hud)),
                item("⚙️ Open Anime Studio", lambda: self.root.after(0, self.restore_window)),
                item("🛑 Exit Completely", lambda: self.root.after(0, self.kill_and_exit))
            )
            self.tray_icon = pystray.Icon("AnimeStudio", im, "Anime Studio Pro — 4K Desktop Suite", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print("System tray error:", e)

    def check_restore_signal(self):
        flag_file = os.path.join(CONFIG_DIR, "restore_signal.flag")
        if os.path.exists(flag_file):
            try:
                os.remove(flag_file)
            except:
                pass
            self.restore_window()
        self.root.after(400, self.check_restore_signal)

    def restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def on_close_clicked(self):
        latest = anime_settings.load_settings()
        minimize_to_tray = latest.get("minimize_to_tray_on_close", False)
        if minimize_to_tray:
            self.root.withdraw()
            return

        res = messagebox.askyesnocancel(
            "Close Anime Studio",
            "How would you like to close Anime Studio?\n\n"
            "• YES: EXIT & STOP completely\n• NO: MINIMIZE to System Tray\n• CANCEL: Stay in Anime Studio",
            "• CANCEL: Stay in Anime Studio",
            icon="question"
        )
        if res is True:
            self.kill_and_exit()
        elif res is False:
            self.root.withdraw()

    def kill_and_exit(self):
        try:
            anime_settings.update_setting("auto_mode_enabled", False)
            anime_settings.update_setting("sound_enabled", False)
            anime_auto_engine.stop_audio()
        except:
            pass
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        for fl in [PID_FILE, os.path.join(CONFIG_DIR, "restore_signal.flag")]:
            if os.path.exists(fl):
                try:
                    os.remove(fl)
                except:
                    pass
        try:
            self.root.destroy()
        except:
            pass
        os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeStudioApp(root)
    root.mainloop()
