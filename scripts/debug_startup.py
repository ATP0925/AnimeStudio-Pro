import sys
import os
import traceback

log_file = r"C:\Users\atpad\AnimeSetup\config\startup_debug.log"
with open(log_file, "w") as log:
    try:
        log.write("Importing anime_studio...\n")
        scripts_dir = r"C:\Users\atpad\AnimeSetup\scripts"
        sys.path.insert(0, scripts_dir)
        import tkinter as tk
        import anime_studio

        log.write("Creating Tk root...\n")
        root = tk.Tk()
        log.write("Instantiating AnimeStudioApp...\n")
        app = anime_studio.AnimeStudioApp(root)
        log.write("Entering mainloop...\n")
        log.flush()
        root.mainloop()
        log.write("Mainloop exited normally.\n")
    except Exception as e:
        traceback.print_exc(file=log)

