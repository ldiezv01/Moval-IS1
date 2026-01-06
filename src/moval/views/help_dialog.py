import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class HelpDialog(ctk.CTkToplevel):
    def __init__(self, parent_view, help_text: str):
        super().__init__(parent_view)
        self.title("Ayuda")
        self.geometry("500x340")
        self.resizable(False, False)
        self.after(100, self.focus_force)

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        label = ctk.CTkLabel(frame, text="Ayuda", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(anchor="w", pady=(0, 10))

        txt = tk.Text(frame, wrap="word", height=12)
        txt.insert("1.0", help_text)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

        btn_close = ctk.CTkButton(frame, text="Cerrar", command=self.destroy)
        btn_close.pack(pady=(10, 0))
