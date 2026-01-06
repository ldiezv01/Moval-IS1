# src/moval/app/views/register_view.py
import customtkinter as ctk
from tkinter import messagebox
from .base_view import BaseView

class RegisterView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.configure(fg_color="transparent")

        # CONTENEDOR CENTRAL
        self.card = ctk.CTkFrame(self, width=500, corner_radius=20, border_width=3,
                                border_color=("#e2e8f0", "#1e293b"))
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        
        self.card.pack_propagate(False)
        self.card.configure(height=720) # Un poco más alto para que quepa todo holgado

        # --- BOTÓN VOLVER (Esquina superior izquierda de la tarjeta) ---
        btn_back_icon = ctk.CTkButton(self.card, text="← Volver", 
                                      width=70, height=30,
                                      fg_color="transparent",
                                      text_color="gray",
                                      hover_color=("#f1f5f9", "#1e293b"),
                                      command=lambda: controller.switch_view("login"))
        btn_back_icon.place(x=20, y=20) # Posición absoluta dentro de la tarjeta

        # --- Cabecera ---
        try:
            logo = controller.get_logo_image()
            if logo:
                logo_lbl = ctk.CTkLabel(self.card, image=logo, text="")
                logo_lbl.pack(pady=(50, 10))
            else:
                raise Exception
        except:
            ctk.CTkLabel(self.card, text="MOVAL", 
                        font=ctk.CTkFont(size=40, weight="bold"),
                        text_color=("#1e293b", "#f8fafc")).pack(pady=(50, 5))

        ctk.CTkLabel(self.card, text="Crea tu cuenta ahora", 
                    font=ctk.CTkFont(size=15),
                    text_color="gray").pack(pady=(0, 15))

        # --- Formulario ---
        form_container = ctk.CTkFrame(self.card, fg_color="transparent")
        form_container.pack(fill="x", padx=60)

        ctk.CTkLabel(form_container, text="Registro de Usuario", 
                    font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(0, 15))

        self.inputs = {}
        campos = [("dni", "DNI"), ("nombre", "Nombre"), ("apellidos", "Apellidos"), ("email", "Email")]
        
        for k, ph in campos:
            inp = ctk.CTkEntry(form_container, placeholder_text=ph, height=45, corner_radius=12)
            inp.pack(fill="x", pady=6)
            self.inputs[k] = inp

        self.pass_inp = ctk.CTkEntry(form_container, placeholder_text="Contraseña", 
                                    show="*", height=45, corner_radius=12)
        self.pass_inp.pack(fill="x", pady=6)

        # Botón REGISTRARSE
        btn_reg = ctk.CTkButton(form_container, text="REGISTRARSE", 
                                command=self.do_register, 
                                corner_radius=12, height=50,
                                font=ctk.CTkFont(size=15, weight="bold"),
                                fg_color="#3b82f6", hover_color="#2563eb")
        btn_reg.pack(fill="x", pady=(20, 10))

        # --- ENLACE INFERIOR (Segunda opción para volver) ---
        btn_login_link = ctk.CTkButton(self.card, text="¿Ya tienes cuenta? Inicia sesión",
                               fg_color="transparent",
                               text_color=("#3b82f6", "#60a5fa"),
                               hover_color=None,
                               font=ctk.CTkFont(size=13, weight="bold", underline=True),
                               command=lambda: controller.switch_view("login"))
        btn_login_link.pack(side="bottom", pady=30)
        
    def do_register(self):
        try:
            data = {k: v.get() for k, v in self.inputs.items()}
            data["password"] = self.pass_inp.get()
            self.controller.register(data)
        except Exception as e:
            messagebox.showerror("Error", str(e))
