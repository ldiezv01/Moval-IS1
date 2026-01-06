import customtkinter as ctk

class VentanaValoracion(ctk.CTkToplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.rating = 0
        
        self.title("Valorar Envío")
        self.geometry("400x380")
        self.resizable(False, False)
        
        # Modal behavior
        self.transient(parent)
        self.grab_set()
        self.after(100, self.focus_force)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_title = ctk.CTkLabel(
            self.main_frame, 
            text="Valoración del Envío", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_title.pack(pady=(0, 20))

        # Stars container
        self.stars_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.stars_frame.pack(pady=10)

        self.star_buttons = []
        for i in range(1, 6):
            btn = ctk.CTkButton(
                self.stars_frame,
                text="★",
                width=40,
                height=40,
                font=ctk.CTkFont(size=30),
                fg_color="transparent",
                text_color="gray",
                command=lambda r=i: self.set_rating(r)
            )
            btn.pack(side="left", padx=2)
            self.star_buttons.append(btn)

        # Comment area
        self.lbl_comment = ctk.CTkLabel(self.main_frame, text="Comentario (opcional):", anchor="w")
        self.lbl_comment.pack(fill="x", pady=(15, 5))

        self.txt_comment = ctk.CTkTextbox(self.main_frame, height=80)
        self.txt_comment.pack(fill="x", pady=(0, 20))

        # Submit button
        self.btn_submit = ctk.CTkButton(
            self.main_frame, 
            text="Enviar Valoración", 
            command=self.submit_rating
        )
        self.btn_submit.pack(fill="x")

    def set_rating(self, rating):
        self.rating = rating
        for i, btn in enumerate(self.star_buttons):
            if i < rating:
                btn.configure(text_color="gold")
            else:
                btn.configure(text_color="gray")

    def submit_rating(self):
        comment = self.txt_comment.get("1.0", "end-1c").strip()
        if self.callback:
            self.callback(self.rating, comment)
        self.destroy()
