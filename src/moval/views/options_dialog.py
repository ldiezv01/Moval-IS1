import customtkinter as ctk

class OptionsDialog(ctk.CTkToplevel):
    def __init__(self, parent_view, options: list):
        super().__init__(parent_view)
        self.title("Opciones")
        self.geometry("420x260")
        self.resizable(False, False)
        self.after(100, self.focus_force)

        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Opciones", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))

        if not options:
            ctk.CTkLabel(frame, text="No hay opciones disponibles para esta vista.").pack(pady=20)
        else:
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

        ctk.CTkButton(frame, text="Cerrar", command=self.destroy).pack(pady=(10, 0))
