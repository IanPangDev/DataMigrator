import customtkinter as ctk
from datetime import datetime

class TkLoggerView:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Logs")
        self.app.resizable(False, False)

        self._center_window(0.5, 0.7)

        frame = ctk.CTkFrame(self.app, fg_color=None, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.textbox = ctk.CTkTextbox(frame)
        self.textbox.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.app.attributes("-topmost", True)
        self.app.after(200, lambda: self.app.attributes("-topmost", False))

    def _center_window(self, width_ratio, height_ratio):
        self.app.update_idletasks()
        sw = self.app.winfo_screenwidth()
        sh = self.app.winfo_screenheight()

        w = int(sw * width_ratio)
        h = int(sh * height_ratio)

        x = (sw - w) // 2
        y = (sh - h) // 2

        self.app.geometry(f"{w}x{h}+{x}+{y}")

    def log(self, message: str):
        timestamp = datetime.now()
        self.textbox.insert("end", f"[{timestamp}] {message}\n")
        self.textbox.see("end")
        self.app.update_idletasks()
