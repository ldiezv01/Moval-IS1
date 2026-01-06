import customtkinter as ctk
from tkinter import messagebox, simpledialog, ttk
from moval.views.base_view import BaseView

class LoginView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
    
        # Fondo general
        self.configure(fg_color="transparent")

        # CONTENEDOR CENTRAL
        self.card = ctk.CTkFrame(self, width=500, corner_radius=20, border_width=3,
                                border_color=("#e2e8f0", "#1e293b"))
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ajustamos la altura para que quepa todo sin problemas
        self.card.pack_propagate(False)
        self.card.configure(height=600) 

        # --- Cabecera ---
        try:
            logo = controller.get_logo_image()
            if logo:
                logo_lbl = ctk.CTkLabel(self.card, image=logo, text="")
                logo_lbl.pack(pady=(40, 10))
            else:
                raise Exception
        except:
            ctk.CTkLabel(self.card, text="MOVAL", 
                        font=ctk.CTkFont(size=40, weight="bold"),
                        text_color=("#1e293b", "#f8fafc")).pack(pady=(40, 5))

        ctk.CTkLabel(self.card, text="Logística simple y efectiva", 
                    font=ctk.CTkFont(size=15),
                    text_color="gray").pack(pady=(0, 20))

        # --- Formulario ---
        form_container = ctk.CTkFrame(self.card, fg_color="transparent")
        form_container.pack(fill="x", padx=60)

        # Título Centrado
        ctk.CTkLabel(form_container, text="Iniciar Sesión", 
                    font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(10, 20))

        # Inputs
        self.email_entry = ctk.CTkEntry(form_container, placeholder_text="Correo electrónico",
                                    height=50, corner_radius=12)
        self.email_entry.pack(fill="x", pady=10)

        self.pass_entry = ctk.CTkEntry(form_container, placeholder_text="Contraseña", 
                                    show="*", height=50, corner_radius=12)
        self.pass_entry.pack(fill="x", pady=10)

        # Botón ENTRAR
        btn_login = ctk.CTkButton(form_container, text="ENTRAR", 
                                command=self.do_login, 
                                corner_radius=12, height=50,
                                font=ctk.CTkFont(size=15, weight="bold"),
                                fg_color="#3b82f6", hover_color="#2563eb")
        btn_login.pack(fill="x", pady=(20, 10))

        # --- BOTÓN DE REGISTRO (Ahora dentro del flujo principal para que no desaparezca) ---
        btn_reg = ctk.CTkButton(self.card, text="¿No tienes cuenta? Regístrate",
                               fg_color="transparent",
                               text_color=("#3b82f6", "#60a5fa"),
                               hover_color=("#f1f5f9", "#1e293b"),
                               font=ctk.CTkFont(size=13, weight="bold"),
                               command=lambda: controller.switch_view("register"))
        btn_reg.pack(pady=(10, 20))

    def do_login(self):
        """Ejecuta el login usando el controller (main.MovalApp)."""
        try:
            email = self.email_entry.get()
            password = self.pass_entry.get()
            self.controller.login(email, password)
        except Exception as e:
            messagebox.showerror("Error", str(e))

