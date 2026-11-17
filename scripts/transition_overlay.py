import sys
import os
import time
import subprocess
import tkinter as tk
from PIL import Image, ImageTk

def run_overlay(wp_path, title_text, char_text, song_name, duration_sec=5, video_path=None):
    # 1. If a video clip is available, play it with hardware-accelerated ffplay!
    if video_path and os.path.exists(video_path):
        try:
            cmd = [
                "ffplay",
                "-fs",
                "-noborder",
                "-alwaysontop",
                "-autoexit",
                "-an",
                "-t", str(duration_sec),
                "-loglevel", "quiet",
                video_path
            ]
            subprocess.run(cmd)
            return
        except Exception as e:
            print("ffplay error, fallback to image overlay:", e)

    # 2. Fallback to aesthetic 4K image fade overlay
    try:
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.0)

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        root.geometry(f"{sw}x{sh}+0+0")
        root.configure(bg="#000000")

        if os.path.exists(wp_path):
            pil_img = Image.open(wp_path).convert("RGB")
            pil_img = pil_img.resize((sw, sh), Image.Resampling.BILINEAR)
            tk_img = ImageTk.PhotoImage(pil_img)

            container = tk.Frame(root, bg="#000000")
            container.pack(fill="both", expand=True)

            lbl_img = tk.Label(container, image=tk_img, bg="#000000", borderwidth=0)
            lbl_img.place(x=0, y=0, width=sw, height=sh)

            banner = tk.Frame(container, bg="#0c0817", padx=36, pady=14, highlightbackground="#00f5d4", highlightthickness=2)
            banner.place(relx=0.5, rely=0.86, anchor="center")

            lbl_title = tk.Label(banner, text=f"⛩️  {title_text.upper()}  ⛩️", font=("Segoe UI", 13, "bold"), fg="#ffe600", bg="#0c0817")
            lbl_title.pack()

            lbl_char = tk.Label(banner, text=char_text, font=("Segoe UI", 10, "bold"), fg="#00f5d4", bg="#0c0817")
            lbl_char.pack(pady=(1, 3))

            lbl_song = tk.Label(banner, text=f"🎵 {song_name}", font=("Segoe UI", 11, "bold"), fg="#ff0055", bg="#0c0817")
            lbl_song.pack(pady=(2, 5))

            canvas_bar = tk.Canvas(banner, width=420, height=5, bg="#1a142e", highlightthickness=0)
            canvas_bar.pack()
            bar_rect = canvas_bar.create_rectangle(0, 0, 0, 5, fill="#00f5d4", width=0)

            # Fade In
            fade_steps = 6
            fade_dt = min(0.1, (duration_sec * 0.15) / fade_steps)
            for a in [0.15, 0.35, 0.55, 0.75, 0.9, 1.0]:
                root.attributes("-alpha", a)
                root.update()
                time.sleep(fade_dt)

            # Showcase
            showcase_time = max(0.5, duration_sec - 1.0)
            showcase_steps = int(showcase_time * 10)
            for i in range(showcase_steps):
                prog = (i + 1) / float(showcase_steps)
                canvas_bar.coords(bar_rect, 0, 0, int(420 * prog), 5)
                color = "#ff0055" if (i % 6 < 3) else "#00f5d4"
                banner.config(highlightbackground=color)
                root.update()
                time.sleep(0.1)

            # Fade Out
            for a in [0.85, 0.65, 0.45, 0.25, 0.1, 0.0]:
                root.attributes("-alpha", a)
                root.update()
                time.sleep(fade_dt)

        root.destroy()
    except Exception as e:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    wp = sys.argv[1] if len(sys.argv) > 1 else ""
    title = sys.argv[2] if len(sys.argv) > 2 else "Anime Masterpiece"
    char = sys.argv[3] if len(sys.argv) > 3 else "Hero"
    song = sys.argv[4] if len(sys.argv) > 4 else "Theme"
    dur = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
    v_path = sys.argv[6] if len(sys.argv) > 6 else ""
    run_overlay(wp, title, char, song, dur, v_path)
