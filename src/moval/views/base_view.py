# moval/views/base_view.py
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog


class BaseView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_header(self, title_text):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        try:
            icon = None
            if hasattr(self.controller, "get_app_icon"):
                icon = self.controller.get_app_icon()
            if icon:
                icon_lbl = ctk.CTkLabel(header, image=icon, text="")
                icon_lbl.image = icon  # mantener referencia
                icon_lbl.pack(side="left", padx=(0, 10))
        except Exception:
            pass
        
        lbl = ctk.CTkLabel(header, text=title_text, font=ctk.CTkFont(size=24, weight="bold"))
        lbl.pack(side="left")

        # Botón Opciones (⚙)
        btn_options = ctk.CTkButton(
            header,
            text="⚙",
            width=40,
            height=32,
            corner_radius=8,
            command=self.open_options
        )
        btn_options.pack(side="right", padx=(5, 0))

        # Botón Ayuda (?)
        btn_help = ctk.CTkButton(
            header,
            text="❓",
            width=40,
            height=32,
            corner_radius=8,
            command=self.open_help
        )
        btn_help.pack(side="right", padx=(5, 0))

        btn_logout = ctk.CTkButton(
            header,
            text="Cerrar Sesión",
            fg_color="#ef4444",
            hover_color="#dc2626",
            width=100,
            command=self.controller.logout
        )
        btn_logout.pack(side="right", padx=5)

        btn_profile = ctk.CTkButton(
            header,
            text="Mi Perfil",
            fg_color="#64748b",
            hover_color="#475569",
            width=100,
            command=self.open_profile  # <- aquí necesita existir open_profile
        )
        btn_profile.pack(side="right", padx=5)
        
        return header

    # -------------------------
    # Funciones que deben existir
    # -------------------------
    def open_profile(self):
        from moval.views.profile_dialog import ProfileDialog
        #from moval.views.profile_dialog import ProfileDialog
        """Abrir diálogo de perfil. Llama a ProfileDialog con el controller."""
        ProfileDialog(self,self.controller)

    def get_help_text(self) -> str:
        """Texto de ayuda por defecto; las vistas pueden sobrescribirlo."""
        return (
            "Ayuda general:\n"
            "- Navega por las pestañas.\n"
            "- Usa los botones en la vista para acciones específicas.\n"
            "- Pulsa ⚙ para opciones rápidas.\n"
            "- Pulsa Mi Perfil para editar tus datos."
        )

    def get_options(self) -> list:
        """Opciones por defecto (vacío). Las vistas pueden devolver [(label, callable), ...]."""
        return []

    def open_help(self):
        from moval.views.help_dialog import HelpDialog
        #from moval.views.help_dialog import HelpDialog
        """Abre el diálogo de ayuda con el texto contextual de la vista actual."""
        HelpDialog(self, self.get_help_text())

    def open_options(self):
        from moval.views.options_dialog import OptionsDialog
        #from moval.views.options_dialog import OptionsDialog
        """Abre el diálogo de opciones con los botones devueltos por get_options()."""
        OptionsDialog(self, self.get_options())


