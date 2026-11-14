import os
import sys

scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import tkinter as tk
import anime_studio

if __name__ == "__main__":
    root = tk.Tk()
    app = anime_studio.AnimeStudioApp(root)
    root.mainloop()
