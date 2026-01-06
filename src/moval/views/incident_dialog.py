import customtkinter as ctk

class VentanaIncidencia(ctk.CTkToplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.incident_reason = ""
        
        self.title("Reportar Incidencia")
        self.geometry("450x450")
        self.resizable(False, False)
        
        # Modal behavior
        self.transient(parent)
        self.grab_set()
        self.after(100, self.focus_force)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_title = ctk.CTkLabel(
            self.main_frame, 
            text="Detalle de la Incidencia", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_title.pack(pady=(0, 20))

        # Etiquetas Rápidas
        self.lbl_tags = ctk.CTkLabel(self.main_frame, text="Selección Rápida:", anchor="w")
        self.lbl_tags.pack(fill="x", pady=(0, 5))

        self.tags_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.tags_frame.pack(fill="x", pady=5)
        
        self.tags = ["Cliente Ausente", "Dirección Errónea", "Paquete Dañado", "Rechazado"]
        for tag in self.tags:
            ctk.CTkButton(
                self.tags_frame,
                text=tag,
                height=30,
                fg_color="#64748b",
                hover_color="#475569",
                command=lambda t=tag: self.append_tag(t)
            ).pack(side="left", padx=2, fill="x", expand=True)

        # Área de Texto Grande
        self.lbl_desc = ctk.CTkLabel(self.main_frame, text="Descripción detallada:", anchor="w")
        self.lbl_desc.pack(fill="x", pady=(15, 5))

        self.txt_desc = ctk.CTkTextbox(self.main_frame, height=120)
        self.txt_desc.pack(fill="x", pady=(0, 20))

        # Botón de Alerta
        self.btn_submit = ctk.CTkButton(
            self.main_frame, 
            text="REPORTAR INCIDENCIA", 
            fg_color="#ef4444", 
            hover_color="#dc2626",
            font=ctk.CTkFont(weight="bold"),
            height=40,
            command=self.submit
        )
        self.btn_submit.pack(fill="x", pady=10)

    def append_tag(self, tag):
        current_text = self.txt_desc.get("1.0", "end-1c")
        if current_text.strip():
            self.txt_desc.insert("end", f" - {tag}")
        else:
            self.txt_desc.insert("1.0", tag)

    def submit(self):
        description = self.txt_desc.get("1.0", "end-1c").strip()
        if not description:
             # Basic validation: ensure reason is not empty
             self.txt_desc.configure(border_color="red", border_width=2)
             return
             
        if self.callback:
            self.callback(description)
        self.destroy()
