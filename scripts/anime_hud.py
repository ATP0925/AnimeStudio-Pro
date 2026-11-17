import tkinter as tk
from tkinter import ttk
import time
import os
import sys
import threading
import ctypes

import psutil

# Prevent duplicate HUD instances
current_pid = os.getpid()
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if p.info['pid'] != current_pid:
            cmd = ' '.join(p.info['cmdline'] or []).lower()
            if 'anime_hud.py' in cmd:
                sys.exit(0)
    except:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
sys.path.append(os.path.join(BASE_DIR, "scripts"))
import anime_settings
import anime_auto_engine

DAYS_ENGLISH = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS_ENGLISH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

class AnimeHUD:
    def __init__(self, root):
        self.root = root
        self.root.title("⛩️ Anime HUD - 4K Cinematic & Long-Term Scheduled Dashboard")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)

        screen_w = self.root.winfo_screenwidth()
        x = max(10, screen_w - 450)
        y = 35
        self.root.geometry(f"440x445+{x}+{y}")
        self.root.configure(bg="#0c0a17")

        self._offsetx = 0
        self._offsety = 0

        self.settings = anime_settings.load_settings()
        self.auto_change_enabled = self.settings.get("auto_mode_enabled", True)
        self.sound_enabled = self.settings.get("sound_enabled", False)
        self.animation_enabled = self.settings.get("show_visual_transition", False)
        self.is_changing = False

        self.setup_ui()
        self.update_clock()
        self.run_timer()

    def start_drag(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def do_drag(self, event):
        x = self.root.winfo_pointerx() - self._offsetx
        y = self.root.winfo_pointery() - self._offsety
        self.root.geometry(f"+{x}+{y}")

    def on_close(self):
        try:
            mci = ctypes.windll.winmm.mciSendStringW
            mci("stop anime_auto_sound", None, 0, None)
            mci("close anime_auto_sound", None, 0, None)
            mci("stop all", None, 0, None)
            mci("close all", None, 0, None)
        except Exception:
            pass
        self.root.destroy()

    def open_settings_gui(self):
        try:
            flag = os.path.join(CONFIG_DIR, "restore_signal.flag")
            with open(flag, "w") as f:
                f.write("restore")
            pid_file = os.path.join(CONFIG_DIR, "app.pid")
            running = False
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, "r") as f:
                        pid = int(f.read().strip())
                    running = psutil.pid_exists(pid)
                except:
                    pass
            if not running:
                import subprocess
                pythonw = sys.executable.replace("python.exe", "pythonw.exe")
                subprocess.Popen([pythonw, os.path.join(BASE_DIR, "AnimeStudio.pyw")])
        except Exception as e:
            print("Error opening AnimeStudio:", e)

    def setup_ui(self):
        outer = tk.Frame(self.root, bg="#ff0055", padx=2, pady=2)
        outer.pack(fill="both", expand=True)

        inner = tk.Frame(outer, bg="#0c0a17")
        inner.pack(fill="both", expand=True)

        # Title bar (Draggable)
        title_bar = tk.Frame(inner, bg="#16122a", height=30, cursor="fleur")
        title_bar.pack(fill="x")
        title_bar.bind("<Button-1>", self.start_drag)
        title_bar.bind("<B1-Motion>", self.do_drag)

        lbl_title = tk.Label(
            title_bar,
            text=" ⛩️ ANIME HUD | 4K SCHEDULED DASHBOARD",
            font=("Segoe UI", 8, "bold"),
            fg="#00f5d4",
            bg="#16122a"
        )
        lbl_title.pack(side="left", padx=8, pady=5)
        lbl_title.bind("<Button-1>", self.start_drag)
        lbl_title.bind("<B1-Motion>", self.do_drag)

        btn_settings = tk.Label(
            title_bar,
            text=" ⚙️ Settings ",
            font=("Segoe UI", 8, "bold"),
            fg="#ffe600",
            bg="#16122a",
            cursor="hand2"
        )
        btn_settings.pack(side="right", padx=2)
        btn_settings.bind("<Button-1>", lambda e: self.open_settings_gui())

        btn_close = tk.Label(
            title_bar,
            text=" ✕ Close ",
            font=("Segoe UI", 8, "bold"),
            fg="#ff5964",
            bg="#16122a",
            cursor="hand2"
        )
        btn_close.pack(side="right", padx=4)
        btn_close.bind("<Button-1>", lambda e: self.on_close())

        body = tk.Frame(inner, bg="#0c0a17", padx=12, pady=6)
        body.pack(fill="both", expand=True)

        # Header Row: Clock & English Date
        header_row = tk.Frame(body, bg="#0c0a17")
        header_row.pack(fill="x")

        self.lbl_clock = tk.Label(
            header_row,
            text="00:00:00",
            font=("Segoe UI", 15, "bold"),
            fg="#ffffff",
            bg="#0c0a17"
        )
        self.lbl_clock.pack(side="left")

        self.lbl_date = tk.Label(
            header_row,
            text="Friday, Oct 30, 2026",
            font=("Segoe UI", 9, "bold"),
            fg="#00f5d4",
            bg="#0c0a17"
        )
        self.lbl_date.pack(side="right", pady=3)

        # Meta Row: Active Anime & 4K Collection Badge
        meta_row = tk.Frame(body, bg="#0c0a17")
        meta_row.pack(fill="x", pady=(4, 2))

        self.lbl_anime = tk.Label(
            meta_row,
            text="Jujutsu Kaisen",
            font=("Segoe UI", 9, "bold"),
            fg="#ffe600",
            bg="#1d163a",
            padx=6,
            pady=2
        )
        self.lbl_anime.pack(side="left")

        self.lbl_pool = tk.Label(
            meta_row,
            text="📁 301+ 4K UHD Wallpapers",
            font=("Segoe UI", 7, "bold"),
            fg="#00f5d4",
            bg="#121829",
            padx=5,
            pady=2
        )
        self.lbl_pool.pack(side="right")

        self.lbl_char = tk.Label(
            body,
            text="Satoru Gojo & Sukuna",
            font=("Segoe UI", 10, "bold"),
            fg="#ff70a6",
            bg="#0c0a17"
        )
        self.lbl_char.pack(anchor="w", pady=(1, 3))

        # Song Card
        card = tk.Frame(body, bg="#151226", padx=8, pady=6, highlightbackground="#3d2c60", highlightthickness=1)
        card.pack(fill="x", pady=2)

        self.lbl_song_icon = tk.Label(
            card,
            text="🎵 ACTIVE ANIME AUDIO TRACK:",
            font=("Segoe UI", 7, "bold"),
            fg="#ffbe0b",
            bg="#151226"
        )
        self.lbl_song_icon.pack(anchor="w")

        self.lbl_song = tk.Label(
            card,
            text="Lost in Paradise (ALI feat. AKLO)",
            font=("Segoe UI", 9, "bold"),
            fg="#00f5d4",
            bg="#151226",
            wraplength=380,
            justify="center"
        )
        self.lbl_song.pack(anchor="center", pady=(1, 3))

        self.lbl_file = tk.Label(
            card,
            text="🖼️ Active 4K UHD Wallpaper",
            font=("Segoe UI", 7, "italic"),
            fg="#b8b5cb",
            bg="#151226"
        )
        self.lbl_file.pack(anchor="center")

        # Countdown Progress Bar (Supports up to 1 Year+)
        timer_frame = tk.Frame(body, bg="#0c0a17")
        timer_frame.pack(fill="x", pady=(6, 2))

        self.lbl_timer_text = tk.Label(
            timer_frame,
            text="⏳ Next 4K Wallpaper in: Calculating...",
            font=("Segoe UI", 8, "bold"),
            fg="#ffbe0b",
            bg="#0c0a17"
        )
        self.lbl_timer_text.pack(anchor="w")

        self.canvas_prog = tk.Canvas(timer_frame, height=6, bg="#1a142e", highlightthickness=0)
        self.canvas_prog.pack(fill="x", pady=(2, 4))
        self.prog_rect = self.canvas_prog.create_rectangle(0, 0, 400, 6, fill="#00f5d4", width=0)

        # Control Row 1 (Auto Toggle, Sound Toggle, Anim Toggle, Settings)
        toggles_row = tk.Frame(body, bg="#0c0a17")
        toggles_row.pack(fill="x", pady=(2, 4))

        self.btn_auto = tk.Button(
            toggles_row,
            text="🟢 Auto: ON",
            font=("Segoe UI", 8, "bold"),
            bg="#2a9d8f",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=4,
            pady=3,
            command=self.toggle_auto
        )
        self.btn_auto.pack(side="left", expand=True, fill="x", padx=1)

        self.btn_sound = tk.Button(
            toggles_row,
            text="🔊 Songs: ON" if self.sound_enabled else "🔇 Songs: MUTE",
            font=("Segoe UI", 8, "bold"),
            bg="#7209b7" if self.sound_enabled else "#4a4e69",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=4,
            pady=3,
            command=self.toggle_sound
        )
        self.btn_sound.pack(side="left", expand=True, fill="x", padx=1)

        self.btn_anim = tk.Button(
            toggles_row,
            text="✨ Anim: ON" if self.animation_enabled else "⚡ Anim: OFF",
            font=("Segoe UI", 8, "bold"),
            bg="#f72585" if self.animation_enabled else "#4a4e69",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=4,
            pady=3,
            command=self.toggle_anim
        )
        self.btn_anim.pack(side="left", expand=True, fill="x", padx=1)

        self.btn_cfg = tk.Button(
            toggles_row,
            text="⚙️ Customizer",
            font=("Segoe UI", 8, "bold"),
            bg="#3a0ca3",
            fg="#ffe600",
            relief="flat",
            cursor="hand2",
            padx=4,
            pady=3,
            command=self.open_settings_gui
        )
        self.btn_cfg.pack(side="left", expand=True, fill="x", padx=1)

        # Action Buttons Row
        action_row = tk.Frame(body, bg="#0c0a17")
        action_row.pack(fill="x", pady=(2, 4))

        self.btn_next_now = tk.Button(
            action_row,
            text="🎬 Change Wallpaper Now (Cinematic Transition)",
            font=("Segoe UI", 8, "bold"),
            bg="#ff0055",
            fg="#ffffff",
            activebackground="#ff5400",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=4,
            command=self.trigger_change_now
        )
        self.btn_next_now.pack(fill="x")

        # Quick Jump Category Pills (English)
        picker_frame = tk.Frame(body, bg="#0c0a17")
        picker_frame.pack(fill="x", pady=(2, 0))

        pills = [
            ("JJK", "01_Jujutsu_Kaisen"),
            ("DemonSlayer", "02_Demon_Slayer"),
            ("OnePiece", "03_One_Piece"),
            ("AOT", "04_Attack_on_Titan"),
            ("Naruto", "05_Naruto_Shippuden"),
            ("Frieren", "06_Frieren"),
            ("SoloLeveling", "07_Solo_Leveling"),
            ("Cyberpunk", "08_Cyberpunk_Edgerunners"),
            ("Ghibli", "09_Studio_Ghibli"),
            ("Shinkai", "10_Makoto_Shinkai")
        ]

        pill_row1 = tk.Frame(picker_frame, bg="#0c0a17")
        pill_row1.pack(fill="x", pady=1)
        for name, folder in pills[:5]:
            btn = tk.Button(
                pill_row1,
                text=name,
                font=("Segoe UI", 7),
                bg="#1a142e",
                fg="#00f5d4",
                activebackground="#7209b7",
                activeforeground="#ffffff",
                relief="flat",
                cursor="hand2",
                padx=2,
                pady=1,
                command=lambda fld=folder: self.jump_to_category(fld)
            )
            btn.pack(side="left", expand=True, fill="x", padx=1)

        pill_row2 = tk.Frame(picker_frame, bg="#0c0a17")
        pill_row2.pack(fill="x", pady=1)
        for name, folder in pills[5:]:
            btn = tk.Button(
                pill_row2,
                text=name,
                font=("Segoe UI", 7),
                bg="#1a142e",
                fg="#00f5d4",
                activebackground="#7209b7",
                activeforeground="#ffffff",
                relief="flat",
                cursor="hand2",
                padx=2,
                pady=1,
                command=lambda fld=folder: self.jump_to_category(fld)
            )
            btn.pack(side="left", expand=True, fill="x", padx=1)

    def update_clock(self):
        now = time.localtime()
        time_str = time.strftime("%H:%M:%S", now)
        day_str = DAYS_ENGLISH[now.tm_wday]
        month_str = MONTHS_ENGLISH[now.tm_mon - 1]
        date_str = f"{day_str}, {month_str} {now.tm_mday}, {now.tm_year}"

        self.lbl_clock.config(text=time_str)
        self.lbl_date.config(text=date_str)
        self.root.after(1000, self.update_clock)

    def run_timer(self):
        latest = anime_settings.load_settings()
        now = time.time()
        next_ts = latest.get("next_change_timestamp", now + 30)
        interval = max(5, latest.get("interval_seconds", 30))

        if self.auto_change_enabled and not self.is_changing:
            remaining = next_ts - now

            # Check if AnimeStudio is already handling the active rotation
            studio_running = False
            pid_file = os.path.join(CONFIG_DIR, "app.pid")
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, "r") as pf:
                        spid = int(pf.read().strip())
                    if psutil.pid_exists(spid):
                        studio_running = True
                except:
                    pass

            if remaining <= 0:
                if not studio_running:
                    self.trigger_change_now()
            else:
                human_rem = anime_settings.format_seconds_to_human(remaining)
                self.lbl_timer_text.config(text=f"⏳ Next 4K Wallpaper in: {human_rem}")

                w = self.canvas_prog.winfo_width()
                if w < 10:
                    w = 380

                frac = max(0.0, min(1.0, remaining / float(interval)))
                prog_w = int(w * frac)
                self.canvas_prog.coords(self.prog_rect, 0, 0, prog_w, 6)

        self.root.after(1000, self.run_timer)

    def trigger_change_now(self, specific_category=None):
        if self.is_changing:
            return
        self.is_changing = True
        self.lbl_timer_text.config(text="🎬 Running Anime Visual Transition...", fg="#00f5d4")

        cur_settings = anime_settings.load_settings()
        if specific_category:
            cur_settings["anime_filter"] = specific_category

        def worker():
            wp_path, meta, song_name = anime_auto_engine.change_wallpaper_now(settings=cur_settings)
            self.root.after(0, lambda: self.on_change_done(wp_path, meta, song_name))

        threading.Thread(target=worker, daemon=True).start()

    def on_change_done(self, wp_path, meta, song_name):
        self.is_changing = False
        if meta and wp_path:
            self.lbl_anime.config(text=meta.get("title", "Anime Masterpiece"))
            self.lbl_char.config(text=meta.get("char", "Featured Hero"))
            self.lbl_song.config(text=song_name or "Audio Muted")
            self.lbl_file.config(text=f"🖼️ Wallpaper: {os.path.basename(wp_path)}")

        latest = anime_settings.load_settings()
        rem = latest.get("next_change_timestamp", time.time() + 30) - time.time()
        self.lbl_timer_text.config(text=f"⏳ Next 4K Wallpaper in: {anime_settings.format_seconds_to_human(rem)}", fg="#ffbe0b")

    def toggle_auto(self):
        self.auto_change_enabled = not self.auto_change_enabled
        if self.auto_change_enabled:
            self.btn_auto.config(text="🟢 Auto: ON", bg="#2a9d8f")
            anime_settings.update_setting("auto_mode_enabled", True)
            anime_settings.register_next_change()
        else:
            self.btn_auto.config(text="🔴 Auto: STOPPED", bg="#e63946")
            self.lbl_timer_text.config(text="🔴 Auto-Change is completely STOPPED", fg="#ff5964")
            anime_settings.update_setting("auto_mode_enabled", False)
            anime_auto_engine.stop_audio()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.btn_sound.config(text="🔊 Songs: ON", bg="#7209b7")
            anime_settings.update_setting("sound_enabled", True)
            if anime_settings.load_settings().get("song_mode") == "mute":
                anime_settings.update_setting("song_mode", "match_anime")
        else:
            self.btn_sound.config(text="🔇 Songs: MUTE", bg="#4a4e69")
            anime_settings.update_setting("sound_enabled", False)
            anime_settings.update_setting("song_mode", "mute")
            anime_auto_engine.stop_audio()

    def toggle_anim(self):
        self.animation_enabled = not self.animation_enabled
        if self.animation_enabled:
            self.btn_anim.config(text="✨ Anim: ON", bg="#f72585")
            anime_settings.update_setting("show_visual_transition", True)
        else:
            self.btn_anim.config(text="⚡ Anim: OFF", bg="#4a4e69")
            anime_settings.update_setting("show_visual_transition", False)

    def jump_to_category(self, folder_name):
        self.trigger_change_now(specific_category=folder_name)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeHUD(root)
    root.mainloop()
