import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
import threading
import time

sys.path.append(r"C:\Users\atpad\AnimeSetup\scripts")
import anime_settings
import anime_auto_engine

class AnimeControlCenter:
    def __init__(self, root):
        self.root = root
        self.root.title("⛩️ Anime Dashboard Control Center - Full Customizer")
        self.root.geometry("560x730")
        self.root.configure(bg="#0c0a17")
        self.root.resizable(False, False)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - 560) // 2
        y = max(10, (sh - 730) // 2)
        self.root.geometry(f"560x730+{x}+{y}")

        self.current_settings = anime_settings.load_settings()
        self.setup_ui()
        self.update_live_schedule_label()

    def setup_ui(self):
        # Header banner
        header = tk.Frame(self.root, bg="#16122a", pady=10, padx=16)
        header.pack(fill="x")

        lbl_title = tk.Label(
            header,
            text="⛩️ ANIME DASHBOARD CONTROL CENTER",
            font=("Segoe UI", 13, "bold"),
            fg="#00f5d4",
            bg="#16122a"
        )
        lbl_title.pack()

        lbl_sub = tk.Label(
            header,
            text="Full Customization: 10s up to 1 Year+, Custom Music, Voices & Wallpapers",
            font=("Segoe UI", 8, "bold"),
            fg="#ffe600",
            bg="#16122a"
        )
        lbl_sub.pack(pady=(2, 0))

        # Main Canvas + Scrollbar in case screen is compact
        container = tk.Frame(self.root, bg="#0c0a17")
        container.pack(fill="both", expand=True, padx=14, pady=6)

        # SECTION 1: TIMER (From 5s up to 1 Year+)
        sec1 = tk.LabelFrame(
            container,
            text=" ⏱️ AUTO-CHANGE INTERVAL (FULL CUSTOMIZATION: 5s UP TO 1 YEAR+) ",
            font=("Segoe UI", 8, "bold"),
            fg="#00f5d4",
            bg="#151226",
            padx=10,
            pady=6
        )
        sec1.pack(fill="x", pady=4)

        # Quick Preset Buttons
        p_frame1 = tk.Frame(sec1, bg="#151226")
        p_frame1.pack(fill="x", pady=1)

        tk.Label(p_frame1, text="Short Presets:", font=("Segoe UI", 7, "bold"), fg="#b8b5cb", bg="#151226").pack(side="left")
        short_presets = [("10s", 10, "seconds"), ("30s", 30, "seconds"), ("1m", 1, "minutes"), ("5m", 5, "minutes"), ("15m", 15, "minutes"), ("30m", 30, "minutes")]
        for lbl, val, unit in short_presets:
            btn = tk.Button(
                p_frame1, text=lbl, font=("Segoe UI", 7), bg="#1f1a38", fg="#00f5d4", relief="flat", cursor="hand2", padx=3, pady=1,
                command=lambda v=val, u=unit: self.set_preset(v, u)
            )
            btn.pack(side="left", padx=2)

        p_frame2 = tk.Frame(sec1, bg="#151226")
        p_frame2.pack(fill="x", pady=2)

        tk.Label(p_frame2, text="Long Presets: ", font=("Segoe UI", 7, "bold"), fg="#b8b5cb", bg="#151226").pack(side="left")
        long_presets = [("1 Hour", 1, "hours"), ("6 Hours", 6, "hours"), ("1 Day", 1, "days"), ("1 Week", 1, "weeks"), ("1 Month", 1, "months"), ("1 Year", 1, "years")]
        for lbl, val, unit in long_presets:
            btn = tk.Button(
                p_frame2, text=lbl, font=("Segoe UI", 7), bg="#2d1b4e", fg="#ffe600", relief="flat", cursor="hand2", padx=3, pady=1,
                command=lambda v=val, u=unit: self.set_preset(v, u)
            )
            btn.pack(side="left", padx=2)

        # Custom Input Row: [ Value Entry ] + [ Unit Combobox ]
        input_row = tk.Frame(sec1, bg="#151226")
        input_row.pack(fill="x", pady=(4, 2))

        tk.Label(input_row, text="Exact Custom Interval:", font=("Segoe UI", 8, "bold"), fg="#ffffff", bg="#151226").pack(side="left")

        self.val_var = tk.StringVar(value=str(self.current_settings.get("interval_value", 30)))
        self.val_var.trace_add("write", lambda *args: self.update_live_schedule_label())

        self.entry_val = tk.Entry(
            input_row,
            textvariable=self.val_var,
            font=("Segoe UI", 9, "bold"),
            width=7,
            bg="#1f1a38",
            fg="#00f5d4",
            insertbackground="#ffffff"
        )
        self.entry_val.pack(side="left", padx=6)

        self.unit_combo = ttk.Combobox(
            input_row,
            values=["Seconds", "Minutes", "Hours", "Days", "Weeks", "Months", "Years"],
            state="readonly",
            font=("Segoe UI", 8, "bold"),
            width=10
        )
        cur_unit = self.current_settings.get("interval_unit", "seconds").capitalize()
        self.unit_combo.set(cur_unit if cur_unit in self.unit_combo['values'] else "Seconds")
        self.unit_combo.bind("<<ComboboxSelected>>", lambda e: self.update_live_schedule_label())
        self.unit_combo.pack(side="left", padx=2)

        # Next Scheduled Timestamp Banner
        self.lbl_scheduled = tk.Label(
            sec1,
            text="📅 Next Wallpaper Change: Calculating...",
            font=("Segoe UI", 8, "bold"),
            fg="#ffbe0b",
            bg="#151226"
        )
        self.lbl_scheduled.pack(anchor="w", pady=(2, 0))

        # SECTION 2: MUSIC & VOICE CUSTOMIZATION
        sec2 = tk.LabelFrame(
            container,
            text=" 🎵 MUSIC & VOICE CUSTOMIZATION ",
            font=("Segoe UI", 8, "bold"),
            fg="#00f5d4",
            bg="#151226",
            padx=10,
            pady=6
        )
        sec2.pack(fill="x", pady=4)

        self.song_mode_var = tk.StringVar(value=self.current_settings.get("song_mode", "match_anime"))

        modes = [
            ("Dynamic: Anime Viral Theme Songs (Overtaken, Silhouette, Lost in Paradise, etc.)", "match_anime"),
            ("Dynamic: Original Japanese Voice Climax (Gojo Domain, Zenitsu Thunder, Gear 5)", "match_voice"),
            ("Lock to Specific Song / Voice Track (Select below)", "specific_song"),
            ("Shuffle All Tracks Randomly", "shuffle_all"),
            ("Silent Mode (Wallpaper changes silently, No audio)", "mute")
        ]

        for text, val in modes:
            rb = tk.Radiobutton(
                sec2,
                text=text,
                value=val,
                variable=self.song_mode_var,
                font=("Segoe UI", 8),
                bg="#151226",
                fg="#ffffff",
                selectcolor="#7209b7",
                activebackground="#151226",
                activeforeground="#ffe600",
                anchor="w"
            )
            rb.pack(fill="x", pady=1)

        # Track picker combobox
        track_row = tk.Frame(sec2, bg="#151226")
        track_row.pack(fill="x", pady=(3, 2))

        tk.Label(track_row, text="Select Track:", font=("Segoe UI", 7, "bold"), fg="#b8b5cb", bg="#151226").pack(side="left")

        self.tracks_dict = anime_auto_engine.get_all_available_tracks()
        self.track_keys = list(self.tracks_dict.keys())

        self.song_combo = ttk.Combobox(
            track_row,
            values=[self.tracks_dict[k] for k in self.track_keys],
            state="readonly",
            font=("Segoe UI", 8),
            width=36
        )
        cur_track = self.current_settings.get("specific_song", "one_piece_overtaken.mp3")
        for i, k in enumerate(self.track_keys):
            if k == cur_track:
                self.song_combo.current(i)
                break
        if not self.song_combo.get() and self.track_keys:
            self.song_combo.current(0)
        self.song_combo.pack(side="left", padx=4)

        btn_add_mp3 = tk.Button(
            track_row,
            text="+ Import MP3",
            font=("Segoe UI", 7, "bold"),
            bg="#2a9d8f",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=4,
            pady=1,
            command=self.import_custom_mp3
        )
        btn_add_mp3.pack(side="left", padx=2)

        # Full Song background checkbox
        self.full_song_var = tk.BooleanVar(value=self.current_settings.get("play_full_song", False))
        chk_full = tk.Checkbutton(
            sec2,
            text="🎵 Play Full Song in Background (Keep playing after transition finishes)",
            variable=self.full_song_var,
            font=("Segoe UI", 7),
            fg="#b8b5cb",
            bg="#151226",
            selectcolor="#151226",
            activebackground="#151226",
            activeforeground="#00f5d4"
        )
        chk_full.pack(anchor="w", pady=(1, 0))

        # SECTION 3: ANIME THEME & WALLPAPER FILTER
        sec3 = tk.LabelFrame(
            container,
            text=" 🎌 ANIME THEME & WALLPAPER SELECTION ",
            font=("Segoe UI", 8, "bold"),
            fg="#00f5d4",
            bg="#151226",
            padx=10,
            pady=6
        )
        sec3.pack(fill="x", pady=4)

        anime_row = tk.Frame(sec3, bg="#151226")
        anime_row.pack(fill="x")

        tk.Label(anime_row, text="Active Anime:", font=("Segoe UI", 7, "bold"), fg="#b8b5cb", bg="#151226").pack(side="left")

        self.anime_options = [("🌐 All Anime (Balanced Shuffle Rotation)", "all")]
        for k, v in anime_auto_engine.ANIME_CATALOG.items():
            self.anime_options.append((f"{v['title']} ({v['char']})", k))

        self.anime_combo = ttk.Combobox(
            anime_row,
            values=[opt[0] for opt in self.anime_options],
            state="readonly",
            font=("Segoe UI", 8),
            width=36
        )
        cur_cat = self.current_settings.get("anime_filter", "all")
        for i, opt in enumerate(self.anime_options):
            if opt[1] == cur_cat:
                self.anime_combo.current(i)
                break
        if not self.anime_combo.get():
            self.anime_combo.current(0)
        self.anime_combo.pack(side="left", padx=4)

        btn_add_wp = tk.Button(
            anime_row,
            text="+ Add Wallpapers",
            font=("Segoe UI", 7, "bold"),
            bg="#2a9d8f",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=4,
            pady=1,
            command=self.import_custom_wallpaper
        )
        btn_add_wp.pack(side="left", padx=2)

        # SECTION 4: TRANSITION & STARTUP
        sec4 = tk.Frame(container, bg="#0c0a17")
        sec4.pack(fill="x", pady=3)

        self.anim_var = tk.BooleanVar(value=self.current_settings.get("show_visual_transition", True))
        chk_anim = tk.Checkbutton(
            sec4,
            text="✨ Enable Cinematic Animated Visual Overlay on Wallpaper Change",
            variable=self.anim_var,
            font=("Segoe UI", 8, "bold"),
            fg="#ffe600",
            bg="#0c0a17",
            selectcolor="#0c0a17",
            activebackground="#0c0a17",
            activeforeground="#00f5d4"
        )
        chk_anim.pack(anchor="w")

        trans_row = tk.Frame(sec4, bg="#0c0a17")
        trans_row.pack(fill="x", padx=18, pady=1)

        tk.Label(trans_row, text="Transition Duration:", font=("Segoe UI", 7), fg="#b8b5cb", bg="#0c0a17").pack(side="left")
        self.trans_dur_var = tk.IntVar(value=self.current_settings.get("transition_duration", 5))
        for d_lbl, d_val in [("5 Seconds (Cinematic)", 5), ("3 Seconds (Fast)", 3), ("1 Second (Flash)", 1), ("Instant (0s)", 0)]:
            tk.Radiobutton(
                trans_row, text=d_lbl, value=d_val, variable=self.trans_dur_var,
                font=("Segoe UI", 7), bg="#0c0a17", fg="#ffffff", selectcolor="#ff0055",
                activebackground="#0c0a17", activeforeground="#00f5d4"
            ).pack(side="left", padx=3)

        self.startup_var = tk.BooleanVar(value=self.current_settings.get("run_at_startup", False))
        chk_startup = tk.Checkbutton(
            sec4,
            text="🚀 Run at Windows Startup (Ensures wallpaper schedule stays active 24/7 across months/years)",
            variable=self.startup_var,
            font=("Segoe UI", 7, "bold"),
            fg="#00f5d4",
            bg="#0c0a17",
            selectcolor="#0c0a17",
            activebackground="#0c0a17",
            activeforeground="#ffe600"
        )
        chk_startup.pack(anchor="w", pady=(3, 0))

        # ACTION BUTTONS
        btn_box = tk.Frame(self.root, bg="#16122a", pady=10, padx=16)
        btn_box.pack(fill="x", side="bottom")

        btn_save = tk.Button(
            btn_box,
            text="💾 SAVE & APPLY ALL SETTINGS (UP TO 1 YEAR+ ACTIVE)",
            font=("Segoe UI", 10, "bold"),
            bg="#2a9d8f",
            fg="#ffffff",
            activebackground="#21867a",
            relief="flat",
            cursor="hand2",
            pady=6,
            command=self.save_settings
        )
        btn_save.pack(fill="x", pady=2)

        row_ops = tk.Frame(btn_box, bg="#16122a")
        row_ops.pack(fill="x", pady=2)

        btn_test = tk.Button(
            row_ops,
            text="🎬 Change Wallpaper Now",
            font=("Segoe UI", 8, "bold"),
            bg="#ff0055",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=4,
            command=self.trigger_change_now
        )
        btn_test.pack(side="left", expand=True, fill="x", padx=2)

        btn_stop = tk.Button(
            row_ops,
            text="🛑 STOP Anime Mode",
            font=("Segoe UI", 8, "bold"),
            bg="#e63946",
            fg="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=4,
            command=self.stop_all
        )
        btn_stop.pack(side="left", expand=True, fill="x", padx=2)

    def set_preset(self, val, unit):
        self.val_var.set(str(val))
        self.unit_combo.set(unit.capitalize())
        self.update_live_schedule_label()

    def update_live_schedule_label(self):
        try:
            val = float(self.val_var.get())
            unit = self.unit_combo.get().lower()
            secs = anime_settings.convert_to_seconds(val, unit)
            human_str = anime_settings.format_seconds_to_human(secs)

            target_ts = time.time() + secs
            target_str = time.strftime("%a, %b %d, %Y at %I:%M:%S %p", time.localtime(target_ts))
            self.lbl_scheduled.config(text=f"📅 Next Change: {target_str} (Every {human_str})")
        except:
            self.lbl_scheduled.config(text="📅 Enter a valid number")

    def import_custom_mp3(self):
        file_path = filedialog.askopenfilename(
            title="Select Custom Anime Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a")]
        )
        if file_path:
            dest_dir = r"C:\Users\atpad\AnimeSetup\audio\viral_songs"
            os.makedirs(dest_dir, exist_ok=True)
            fname = os.path.basename(file_path)
            dest_path = os.path.join(dest_dir, fname)
            try:
                shutil.copy2(file_path, dest_path)
                messagebox.showinfo("Custom Song Added", f"Successfully imported '{fname}' into Anime Audio Library!")
                # Refresh tracks
                self.tracks_dict = anime_auto_engine.get_all_available_tracks()
                self.track_keys = list(self.tracks_dict.keys())
                self.song_combo['values'] = [self.tracks_dict[k] for k in self.track_keys]
                for i, k in enumerate(self.track_keys):
                    if k == fname:
                        self.song_combo.current(i)
                        self.song_mode_var.set("specific_song")
                        break
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import song: {e}")

    def import_custom_wallpaper(self):
        files = filedialog.askopenfilenames(
            title="Select Custom Anime Wallpapers",
            filetypes=[("Image Files", "*.jpg *.png *.jpeg *.webp")]
        )
        if files:
            dest_dir = r"C:\Users\atpad\AnimeSetup\wallpapers\collection\12_Custom_Wallpapers"
            os.makedirs(dest_dir, exist_ok=True)
            count = 0
            for f in files:
                fname = os.path.basename(f)
                try:
                    shutil.copy2(f, os.path.join(dest_dir, fname))
                    count += 1
                except:
                    pass
            messagebox.showinfo("Wallpapers Added", f"Successfully added {count} custom wallpapers to '12_Custom_Wallpapers' category!")

    def save_settings(self):
        try:
            val = float(self.val_var.get())
            if val <= 0:
                val = 5
        except:
            val = 30

        unit = self.unit_combo.get().lower()
        secs = anime_settings.convert_to_seconds(val, unit)
        now = time.time()

        song_mode = self.song_mode_var.get()
        selected_track_idx = self.song_combo.current()
        specific_song = self.track_keys[selected_track_idx] if (0 <= selected_track_idx < len(self.track_keys)) else "one_piece_overtaken.mp3"

        selected_anime_idx = self.anime_combo.current()
        anime_filter = self.anime_options[selected_anime_idx][1] if (0 <= selected_anime_idx < len(self.anime_options)) else "all"

        new_settings = {
            "interval_value": val,
            "interval_unit": unit,
            "interval_seconds": secs,
            "last_change_timestamp": now,
            "next_change_timestamp": now + secs,
            "song_mode": song_mode,
            "specific_song": specific_song,
            "anime_filter": anime_filter,
            "show_visual_transition": self.anim_var.get(),
            "transition_duration": self.trans_dur_var.get(),
            "play_full_song": self.full_song_var.get(),
            "sound_enabled": (song_mode != "mute"),
            "auto_mode_enabled": True,
            "run_at_startup": self.startup_var.get()
        }

        anime_settings.save_settings(new_settings)
        anime_settings.set_windows_startup(self.startup_var.get())

        human_time = anime_settings.format_seconds_to_human(secs)
        target_str = time.strftime("%a, %b %d, %Y at %I:%M:%S %p", time.localtime(now + secs))
        messagebox.showinfo(
            "Settings Saved",
            f"Anime Dashboard Settings Saved!\n\n"
            f"⏱️ Interval: Every {human_time} ({secs:,} seconds)\n"
            f"📅 Next Change: {target_str}\n"
            f"🎵 Music Mode: {song_mode}\n"
            f"🎌 Theme Filter: {anime_filter}\n"
            f"🚀 Startup Enabled: {self.startup_var.get()}"
        )

    def trigger_change_now(self):
        self.save_settings()
        def worker():
            anime_auto_engine.change_wallpaper_now()
        threading.Thread(target=worker, daemon=True).start()

    def stop_all(self):
        try:
            import stop_anime
            stop_anime.kill_everything_anime()
            messagebox.showinfo("Anime Control Center", "All Anime Auto-Changers and Music have been STOPPED.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeControlCenter(root)
    root.mainloop()
