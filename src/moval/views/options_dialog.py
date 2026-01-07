# src/moval/views/options_dialog.py
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

class OptionsDialog(ctk.CTkToplevel):
    def __init__(self, parent_view, options: list, show_close_button: bool = True):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.controller = getattr(parent_view, "controller", None)
        self.title("Opciones")
        self.geometry("420x300")   # keep fixed so dialog itself doesn't resize with scale
        self.resizable(False, False)
        self.after(100, self.focus_force)
        self.show_close_button = bool(show_close_button)

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Opciones", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))

        # Apariencia (igual que antes)
        ctk.CTkLabel(frame, text="Apariencia", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(4, 4))
        modes = ["System", "Light", "Dark"]
        try:
            current_mode = ctk.get_appearance_mode()
        except Exception:
            current_mode = "System"

        self.mode_cb = ctk.CTkComboBox(frame, values=modes, width=180)
        self.mode_cb.set(current_mode)
        self.mode_cb.pack(anchor="w", pady=(0, 8))

        def apply_appearance():
            try:
                mode = self.mode_cb.get()
                ctk.set_appearance_mode(mode)
                if self.controller is not None:
                    prefs = getattr(self.controller, "ui_prefs", {}) or {}
                    prefs["appearance_mode"] = mode
                    self.controller.ui_prefs = prefs
                messagebox.showinfo("Apariencia", f"Apariencia '{mode}' aplicada.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo aplicar la apariencia: {e}")

        ctk.CTkButton(frame, text="Aplicar apariencia", command=apply_appearance).pack(fill="x", pady=(0, 8))

        # --- Escala: NO usamos ctk.set_widget_scaling() para no afectar al diálogo ---
        ctk.CTkLabel(frame, text="Escala ventana principal", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10, 4))

        # Leer escala actual desde controller.ui_prefs (si existe) o usar 1.0
        init_scale = 1.0
        if self.controller is not None:
            init_scale = getattr(self.controller, "ui_prefs", {}).get("scale", 1.0)
        try:
            init_scale = float(init_scale)
        except Exception:
            init_scale = 1.0

        self.scale_min = 0.6
        self.scale_max = 2.0
        self.scale_step = 0.1
        self.scale = float(round(init_scale, 2))

        scale_frame = ctk.CTkFrame(frame, fg_color="transparent")
        scale_frame.pack(fill="x", pady=(0, 6))

        def update_scale_label():
            pct = int(round(self.scale * 100))
            self.scale_lbl.configure(text=f"Escala: {pct}%")

        def apply_scale_to_app(new_scale):
            # guarda pref y llama al controller para que aplique la escala SOLO en ventana principal
            new_scale = max(self.scale_min, min(self.scale_max, round(new_scale, 2)))
            self.scale = new_scale
            prefs = getattr(self.controller, "ui_prefs", {}) or {}
            prefs["scale"] = self.scale
            if self.controller is not None:
                self.controller.ui_prefs = prefs
                # si MovalApp tiene apply_ui_scale -> úsalo (aplica solo a la ventana principal)
                if hasattr(self.controller, "apply_ui_scale"):
                    try:
                        self.controller.apply_ui_scale(self.scale)
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo aplicar escala en la app: {e}")
            update_scale_label()

        def dec_scale():
            apply_scale_to_app(self.scale - self.scale_step)

        def inc_scale():
            apply_scale_to_app(self.scale + self.scale_step)

        btn_dec = ctk.CTkButton(scale_frame, text="−", width=40, height=30, command=dec_scale)
        btn_dec.pack(side="left", padx=(0, 8))

        self.scale_lbl = ctk.CTkLabel(scale_frame, text="", width=120, anchor="center")
        self.scale_lbl.pack(side="left")

        btn_inc = ctk.CTkButton(scale_frame, text="+", width=40, height=30, command=inc_scale)
        btn_inc.pack(side="left", padx=(8, 0))

        update_scale_label()

        # --- Restaurar valores por defecto (no toca dialog size) ---
        def restore_defaults():
            try:
                # apariencia por defecto
                ctk.set_appearance_mode("System")
                try:
                    ctk.set_default_color_theme("blue")
                except Exception:
                    pass
                # prefs en controller
                if self.controller is not None:
                    self.controller.ui_prefs = {"appearance_mode": "System", "theme": "blue", "scale": 1.0}
                    if hasattr(self.controller, "apply_ui_scale"):
                        self.controller.apply_ui_scale(1.0)
                # actualizar controles
                self.mode_cb.set("System")
                self.scale = 1.0
                update_scale_label()
                messagebox.showinfo("Restaurar", "Valores restaurados a los predeterminados.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron restaurar los valores por defecto: {e}")

        ctk.CTkButton(frame, text="Restaurar valores por defecto", fg_color="gray", hover_color="#dc2626", command=restore_defaults).pack(fill="x", pady=(8, 12))

        # --- Opciones específicas de la vista (si hay) ---
        if options:
            ctk.CTkLabel(frame, text="Opciones de la vista", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(6, 6))
            for label, action in options:
                def make_cb(fn):
                    def cb():
                        try:
                            fn()
                        except Exception as e:
                            messagebox.showerror("Error", str(e))
                        finally:
                            try:
                                parent_view.refresh_data()
                            except:
                                pass
                    return cb
                btn = ctk.CTkButton(frame, text=label, command=make_cb(action))
                btn.pack(fill="x", pady=6)

        if self.show_close_button:
            ctk.CTkButton(frame, text="Cerrar", command=self.destroy).pack(pady=(10, 0))


