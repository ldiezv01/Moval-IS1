import customtkinter as ctk
from tkinter import messagebox
from tkinter import messagebox, simpledialog, ttk

class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent_view, controller):

        super().__init__(parent_view)
        self.controller = controller
        self.title("Ajustes de Perfil")
        self.geometry("450x550")
        self.after(100, self.focus_force)
        self.resizable(False, False)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(main_frame, text="Mi Perfil", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))
        ctk.CTkLabel(main_frame, text="Actualice sus datos personales a continuación:", font=ctk.CTkFont(size=13)).pack(pady=(0, 20))
        
        user_data = controller.get_current_user_data()
        
        self.entries = {}
        fields = [("Nombre", "nombre"), ("Apellidos", "apellidos"), ("Teléfono", "telefono"), ("Email", "email")]
        
        for label_text, key in fields:
            lbl = ctk.CTkLabel(main_frame, text=label_text, font=ctk.CTkFont(weight="bold"))
            lbl.pack(anchor="w", pady=(5, 0))
            
            entry = ctk.CTkEntry(main_frame, width=350, placeholder_text=f"Ingrese su {label_text.lower()}")
            current_val = user_data.get(key, '')
            if current_val is None:
                current_val = ''
            entry.insert(0, str(current_val))
            entry.pack(pady=(0, 5))
            self.entries[key] = entry
            
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        btn_save = ctk.CTkButton(btn_frame, text="GUARDAR", 
                                 fg_color="#10b981", hover_color="#059669",
                                 font=ctk.CTkFont(weight="bold"),
                                 command=self.save)
        btn_save.pack(side="left", expand=True, padx=(0, 5))
        
        btn_cancel = ctk.CTkButton(btn_frame, text="CANCELAR", 
                                   fg_color="transparent", border_width=1, border_color="#cbd5e1", text_color="#64748b",
                                   command=self.destroy)
        btn_cancel.pack(side="right", expand=True, padx=(5, 0))

    def save(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if self.controller.update_profile(data):
            messagebox.showinfo("Perfil", "Tus datos han sido actualizados con éxito.")
            self.destroy()