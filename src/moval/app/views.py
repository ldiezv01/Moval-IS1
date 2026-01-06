import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import tkinter as tk
import tkintermapview

# Configuración global de apariencia
ctk.set_appearance_mode("System")  # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")

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
        """Abre el diálogo de ayuda con el texto contextual de la vista actual."""
        HelpDialog(self, self.get_help_text())

    def open_options(self):
        """Abre el diálogo de opciones con los botones devueltos por get_options()."""
        OptionsDialog(self, self.get_options())

# ==========================================
# DIALOGO: PERFIL
# ==========================================
class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent_view: BaseView, controller):
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
        
        # Recuperar datos del controller (método ya existía en tu main)
        user_data = controller.get_current_user_data()
        
        self.entries = {}
        fields = [("Nombre", "nombre"), ("Apellidos", "apellidos"), ("Teléfono", "telefono"), ("Email", "email")]
        
        for label_text, key in fields:
            lbl = ctk.CTkLabel(main_frame, text=label_text, font=ctk.CTkFont(weight="bold"))
            lbl.pack(anchor="w", pady=(5, 0))
            
            entry = ctk.CTkEntry(main_frame, width=350, placeholder_text=f"Ingrese su {label_text.lower()}")
            current_val = user_data.get(key, '')
            if current_val is None: current_val = ''
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


class HelpDialog(ctk.CTkToplevel):
    def __init__(self, parent_view: BaseView, help_text: str):
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

class HelpDialog(ctk.CTkToplevel):
    def __init__(self, parent_view: BaseView, help_text: str):
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


class OptionsDialog(ctk.CTkToplevel):
    def __init__(self, parent_view: BaseView, options: list):
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

# ==========================================
# LOGIN
# ==========================================
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
        self.email_entry.insert(0, "admin@moval.com")

        self.pass_entry = ctk.CTkEntry(form_container, placeholder_text="Contraseña", 
                                    show="*", height=50, corner_radius=12)
        self.pass_entry.pack(fill="x", pady=10)
        self.pass_entry.insert(0, "1234")

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

# ==========================================
# REGISTRO
# ==========================================
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
        """Recolecta datos del formulario y llama al controller.register."""
        try:
            data = {k: v.get() for k, v in self.inputs.items()}
            data["password"] = self.pass_inp.get()
            self.controller.register(data)
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ==========================================
# ADMIN
# ==========================================
class AdminView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("Panel de Administración")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_shipments = self.tabview.add("Envíos")
        self.tab_users = self.tabview.add("Usuarios")
        self.tab_couriers = self.tabview.add("Repartidores")
        self.tab_ratings = self.tabview.add("Valoraciones")

        self.setup_shipments()
        self.setup_users()
        self.setup_couriers()
        self.setup_ratings()

    def setup_shipments(self):
        # Crear Tabview para las 4 vistas
        self.shipment_tabview = ctk.CTkTabview(self.tab_shipments)
        self.shipment_tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear pestañas
        self.tab_reg = self.shipment_tabview.add("Registrados")
        self.tab_asg = self.shipment_tabview.add("Asignados")
        self.tab_ent = self.shipment_tabview.add("Entregados")
        self.tab_inc = self.shipment_tabview.add("Incidencias")

        # --- 1. REGISTRADOS (Controles de Asignación) ---
        ctrl_reg = ctk.CTkFrame(self.tab_reg, fg_color="transparent")
        ctrl_reg.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ctrl_reg, text="Asignar a:").pack(side="left", padx=5)
        self.courier_combo = ctk.CTkComboBox(ctrl_reg, width=200, values=[])
        self.courier_combo.pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl_reg, text="Asignar", width=100, command=self.assign).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_reg, text="Ver Detalles", width=100, fg_color="#3b82f6", command=self.show_details).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_reg, text="Actualizar", width=100, fg_color="#64748b", command=self.refresh_data).pack(side="right", padx=5)
        
        self.tree_reg = self.create_tree(self.tab_reg, ["ID", "Código", "Origen", "Destino", "Estado"])

        # --- 2. ASIGNADOS (Controles de Desasignación) ---
        ctrl_asg = ctk.CTkFrame(self.tab_asg, fg_color="transparent")
        ctrl_asg.pack(fill="x", pady=5)
        
        ctk.CTkButton(ctrl_asg, text="Desasignar", width=100, fg_color="#f59e0b", hover_color="#d97706", command=self.unassign).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_asg, text="Ver Detalles", width=100, fg_color="#3b82f6", command=self.show_details).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_asg, text="Actualizar", width=100, fg_color="#64748b", command=self.refresh_data).pack(side="right", padx=5)
        
        self.tree_asg = self.create_tree(self.tab_asg, ["ID", "Código", "Origen", "Destino", "Estado", "Repartidor"])

        # --- 3. ENTREGADOS (Solo visualización) ---
        ctrl_ent = ctk.CTkFrame(self.tab_ent, fg_color="transparent")
        ctrl_ent.pack(fill="x", pady=5)
        
        ctk.CTkButton(ctrl_ent, text="Ver Detalles", width=100, fg_color="#3b82f6", command=self.show_details).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_ent, text="Actualizar", width=100, fg_color="#64748b", command=self.refresh_data).pack(side="right", padx=5)
        
        self.tree_ent = self.create_tree(self.tab_ent, ["ID", "Código", "Destino", "Repartidor", "Fecha Entrega"])

        # --- 4. INCIDENCIAS (Re-Asignación y Visualización) ---
        ctrl_inc = ctk.CTkFrame(self.tab_inc, fg_color="transparent")
        ctrl_inc.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ctrl_inc, text="Reasignar a:").pack(side="left", padx=5)
        self.courier_combo_inc = ctk.CTkComboBox(ctrl_inc, width=200, values=[])
        self.courier_combo_inc.pack(side="left", padx=5)
        
        ctk.CTkButton(ctrl_inc, text="Reasignar", width=100, command=self.assign_incident).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_inc, text="Ver Detalles", width=100, fg_color="#3b82f6", command=self.show_details).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_inc, text="Actualizar", width=100, fg_color="#64748b", command=self.refresh_data).pack(side="right", padx=5)
        
        self.tree_inc = self.create_tree(self.tab_inc, ["ID", "Código", "Destino", "Estado", "Repartidor"])

    def get_active_tree(self):
        tab = self.shipment_tabview.get()
        if tab == "Registrados": return self.tree_reg
        if tab == "Asignados": return self.tree_asg
        if tab == "Entregados": return self.tree_ent
        if tab == "Incidencias": return self.tree_inc
        return None

    def show_details(self):
        tree = self.get_active_tree()
        if not tree: return
        
        selection = tree.selection()
        if not selection: return
        
        sid = int(tree.item(selection[0])['values'][0])
        det = self.controller.get_shipment_details(sid)
        eta = self.controller.calculate_eta(sid)
        
        msg = f"--- DETALLES DEL PEDIDO ---\n\n"
        msg += f"Código: {det.get('codigo_seguimiento')}\n"
        msg += f"Descripción: {det.get('descripcion')}\n"
        msg += f"Estado: {det.get('estado')}\n"
        msg += f"ETA: {eta.get('texto_mostrar', 'N/A')}\n\n"
        
        msg += f"--- CLIENTE (DESTINATARIO) ---\n"
        msg += f"Nombre: {det.get('cliente_nombre', 'N/A')}\n"
        msg += f"Email: {det.get('cliente_email', 'N/A')}\n"
        msg += f"Destino: {det.get('direccion_destino')}\n\n"
        
        if det.get("estado") == "INCIDENCIA" or det.get("ultima_incidencia"):
            msg += f"--- MOTIVO INCIDENCIA ---\n"
            msg += f"Descripción: {det.get('ultima_incidencia', 'Sin descripción')}\n"
            if det.get("fecha_incidencia"):
                msg += f"Fecha: {det.get('fecha_incidencia')}\n"
        
        messagebox.showinfo(f"Pedido #{sid}", msg)

    def setup_couriers(self):
        f = ctk.CTkFrame(self.tab_couriers, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(f, text="Seguimiento de Repartidores", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        
        self.tree_couriers = self.create_tree(f, ["Nombre", "Estado", "Última Entrada", "Última Salida", "Media"])

    def setup_users(self):
        layout = ctk.CTkFrame(self.tab_users, fg_color="transparent")
        layout.pack(fill="both", expand=True, padx=20, pady=20)
        
        search_f = ctk.CTkFrame(layout, fg_color="transparent")
        search_f.pack(fill="x")
        self.search_entry = ctk.CTkEntry(search_f, placeholder_text="Email del usuario...", width=300)
        self.search_entry.pack(side="left", padx=5)
        ctk.CTkButton(search_f, text="Buscar", width=80, command=self.search_user).pack(side="left", padx=5)
        
        self.user_info_lbl = ctk.CTkLabel(layout, text="Busque un usuario para gestionar su rol.", font=ctk.CTkFont(slant="italic"))
        self.user_info_lbl.pack(pady=20)
        
        self.role_frame = ctk.CTkFrame(layout, fg_color="transparent")
        ctk.CTkLabel(self.role_frame, text="Nuevo Rol:").pack(side="left", padx=5)
        self.role_combo = ctk.CTkComboBox(self.role_frame, values=["Cliente", "Repartidor", "Administrador"])
        self.role_combo.pack(side="left", padx=5)
        self.btn_upd_role = ctk.CTkButton(self.role_frame, text="Actualizar Rol", command=self.update_role)
        self.btn_upd_role.pack(side="left", padx=5)

    def setup_ratings(self):
        self.tree_rat = self.create_tree(self.tab_ratings, ["Fecha", "Autor", "Mensajero", "Nota", "Comentario"])

    def create_tree(self, parent, cols):
        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True)
        
        tree = ttk.Treeview(container, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor="center")
        
        # Scrollbar
        sb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tree

    def refresh_data(self):
        # Repartidores
        couriers = self.controller.get_available_couriers()
        self.courier_map = {f"{c['nombre']} {c['apellidos']} (ID: {c['id']})": c['id'] for c in couriers}
        
        # Populate combos
        c_vals = list(self.courier_map.keys())
        self.courier_combo.configure(values=c_vals)
        self.courier_combo_inc.configure(values=c_vals)
        
        if c_vals: 
            self.courier_combo.set(c_vals[0])
            self.courier_combo_inc.set(c_vals[0])

        # Envíos - Limpiar tablas
        for t in [self.tree_reg, self.tree_asg, self.tree_ent, self.tree_inc]:
            t.delete(*t.get_children())

        shipments = self.controller.get_all_shipments()
        for s in shipments:
            st = s['estado']
            # REGISTRADOS
            if st == 'REGISTRADO':
                self.tree_reg.insert("", "end", values=(
                    s['id'], s['codigo_seguimiento'], s['direccion_origen'], s['direccion_destino'], st
                ))
            # ASIGNADOS (y En Reparto)
            elif st in ['ASIGNADO', 'EN_REPARTO']:
                self.tree_asg.insert("", "end", values=(
                    s['id'], s['codigo_seguimiento'], s['direccion_origen'], s['direccion_destino'], st,
                    s.get('id_mensajero') or ''
                ))
            # ENTREGADOS
            elif st == 'ENTREGADO':
                self.tree_ent.insert("", "end", values=(
                    s['id'], s['codigo_seguimiento'], s['direccion_destino'],
                    s.get('id_mensajero') or '', s.get('fecha_entrega_real') or ''
                ))
            # INCIDENCIAS
            elif st == 'INCIDENCIA':
                self.tree_inc.insert("", "end", values=(
                    s['id'], s['codigo_seguimiento'], s['direccion_destino'], st,
                    s.get('id_mensajero') or ''
                ))

        # Ratings
        ratings = self.controller.get_all_ratings()
        self.tree_rat.delete(*self.tree_rat.get_children())
        for r in ratings:
            self.tree_rat.insert("", "end", values=(r['fecha'], r['autor'], r['mensajero'] or "", r['puntuacion'], r['comentario']))

        # Reporte Repartidores
        report = self.controller.get_all_couriers_report()
        self.tree_couriers.delete(*self.tree_couriers.get_children())
        for c in report:
            estado_jornada = c.get('estado_jornada')
            
            if estado_jornada == 'ACTIVA':
                status_text = "TRABAJANDO"
                salida_text = "Aún activo"
            elif estado_jornada == 'FINALIZADA':
                status_text = "INACTIVO"
                salida_text = c.get('fecha_fin') or "---"
            else:
                status_text = "INACTIVO"
                salida_text = "---"

            media = f"{c['media']:.1f}" if c['media'] else "N/A"
            self.tree_couriers.insert("", "end", values=(
                f"{c['nombre']} {c['apellidos']}",
                status_text,
                c.get('fecha_inicio') or "---",
                salida_text,
                media
            ))

    def assign(self):
        selection = self.tree_reg.selection()
        c_val = self.courier_combo.get()
        if not selection or not c_val: return
        cid = self.courier_map[c_val]
        sids = [int(self.tree_reg.item(i)['values'][0]) for i in selection]
        self.controller.assign_shipments(sids, cid)
        self.refresh_data()

    def assign_incident(self):
        selection = self.tree_inc.selection()
        c_val = self.courier_combo_inc.get()
        if not selection or not c_val: return
        cid = self.courier_map[c_val]
        sids = [int(self.tree_inc.item(i)['values'][0]) for i in selection]
        self.controller.assign_shipments(sids, cid)
        self.refresh_data()

    def unassign(self):
        selection = self.tree_asg.selection()
        if not selection: return
        for i in selection:
            self.controller.unassign_shipment(int(self.tree_asg.item(i)['values'][0]))
        self.refresh_data()

    def search_user(self):
        u = self.controller.get_user_by_email(self.search_entry.get())
        if u:
            self.found_user = u
            self.user_info_lbl.configure(text=f"Usuario: {u['nombre']} {u['apellidos']} | Rol Actual: {u['role']}", font=ctk.CTkFont(weight="bold"))
            self.role_frame.pack(pady=10)
        else:
            self.user_info_lbl.configure(text="No encontrado.")
            self.role_frame.pack_forget()

    def update_role(self):
        roles = {"Cliente": "CUSTOMER", "Repartidor": "COURIER", "Administrador": "ADMIN"}
        self.controller.change_user_role(self.found_user['email'], roles[self.role_combo.get()])
        self.search_user()
        
    def get_help_text(self):
        return (
            "Panel de Administración:\n\n"
            "- 'Asignar' y 'Desasignar' para gestionar mensajeros.\n"
            "- Usa 'Ver Detalles' para ver información completa de un envío.\n"
            "- En la pestaña Usuarios puedes buscar y cambiar roles.\n"
        )

    def get_options(self):
        return [
            ("Actualizar Datos", lambda: self.refresh_data()),
            ("Generar Reporte Repartidores", lambda: self.controller.get_all_couriers_report()),
        ]


# ==========================================
# REPARTIDOR (COURIER)
# ==========================================
class CourierView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("Panel del Repartidor")

        # Main Layout: 2 Columns
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- LEFT COLUMN (Controls & List) ---
        self.left_col = ctk.CTkFrame(self.main_content, fg_color="transparent", width=400)
        self.left_col.pack(side="left", fill="y", expand=False, padx=(0, 10))

        # 1. Status
        status_card = ctk.CTkFrame(self.left_col)
        status_card.pack(fill="x", pady=(0, 10))
        
        self.status_lbl = ctk.CTkLabel(status_card, text="Jornada: ...", font=ctk.CTkFont(size=16))
        self.status_lbl.pack(side="left", padx=15, pady=10)
        
        self.btn_toggle_wd = ctk.CTkButton(status_card, text="Iniciar/Fin", width=100, command=self.toggle_wd)
        self.btn_toggle_wd.pack(side="right", padx=15)

        # 2. Next Stop
        self.next_stop_frame = ctk.CTkFrame(self.left_col, fg_color=("#e2e8f0", "#1e293b"), border_width=2, border_color="#3b82f6")
        self.next_stop_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.next_stop_frame, text="PRÓXIMA ENTREGA", font=ctk.CTkFont(size=14, weight="bold"), text_color="#3b82f6").pack(pady=(10, 0))
        
        self.next_address_lbl = ctk.CTkLabel(self.next_stop_frame, text="Sin ruta generada", font=ctk.CTkFont(size=20, weight="bold"), wraplength=350)
        self.next_address_lbl.pack(pady=10)
        
        self.next_info_lbl = ctk.CTkLabel(self.next_stop_frame, text="-", font=ctk.CTkFont(size=14))
        self.next_info_lbl.pack(pady=(0, 10))

        # 3. Scrollable List (Cards)
        self.scroll_frame = ctk.CTkScrollableFrame(self.left_col, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

        # 4. Global Buttons
        act_f = ctk.CTkFrame(self.left_col, fg_color="transparent")
        act_f.pack(fill="x", pady=10)
        
        act_f.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(act_f, text="Generar Ruta", fg_color="#3b82f6", command=self.generate_route).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(act_f, text="Actualizar", fg_color="#64748b", command=self.refresh_data).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        # --- RIGHT COLUMN (Map) ---
        self.right_col = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.right_col.pack(side="right", fill="both", expand=True)

        self.map_widget = tkintermapview.TkinterMapView(self.right_col, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        # Set default location (e.g., León, Spain)
        self.map_widget.set_position(42.60003, -5.57032)
        self.map_widget.set_zoom(13)

    def refresh_data(self):
        wd = self.controller.get_active_workday()
        if wd:
            self.status_lbl.configure(text="Jornada: ACTIVA", text_color="#10b981")
            self.btn_toggle_wd.configure(text="Finalizar Jornada", fg_color="#ef4444")
        else:
            self.status_lbl.configure(text="Jornada: INACTIVA", text_color="#ef4444")
            self.btn_toggle_wd.configure(text="Iniciar Jornada", fg_color="#10b981")

        shipments = self.controller.get_my_shipments()
        
        # Clear existing cards
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Filter pending (exclude Delivered AND Incidents)
        pending = [s for s in shipments if s['estado'] not in ['ENTREGADO', 'INCIDENCIA']]
        
        for i, s in enumerate(pending):
            self.create_shipment_card(i + 1, s)

        if not pending:
            self.next_address_lbl.configure(text="¡Todo entregado!")
            self.next_info_lbl.configure(text="-")

    def create_shipment_card(self, idx, shipment):
        card = ctk.CTkFrame(self.scroll_frame, fg_color=("#ffffff", "#334155"), border_width=1, border_color="#cbd5e1")
        card.pack(fill="x", pady=5, padx=2)
        
        # Top Row: ID and Status
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))
        
        sid_txt = f"#{idx} | {shipment.get('codigo_seguimiento', shipment['id'])}"
        ctk.CTkLabel(top, text=sid_txt, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        
        status_color = "#f59e0b" if shipment['estado'] == "INCIDENCIA" else "#3b82f6"
        ctk.CTkLabel(top, text=shipment['estado'], text_color=status_color, font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")
        
        # Middle: Address
        mid = ctk.CTkFrame(card, fg_color="transparent")
        mid.pack(fill="x", padx=10, pady=0)
        
        dest = shipment.get('cliente_nombre') or "Cliente desconocido"
        ctk.CTkLabel(mid, text=dest, font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkLabel(mid, text=shipment['direccion_destino'], font=ctk.CTkFont(size=13), wraplength=300).pack(anchor="w", pady=(2, 5))

        # Bottom: Buttons
        bot = ctk.CTkFrame(card, fg_color="transparent")
        bot.pack(fill="x", padx=10, pady=(5, 10))
        
        # Only enable delivery for the first item (Next Stop)
        is_next = (idx == 1)
        del_state = "normal" if is_next else "disabled"
        del_color = "#10b981" if is_next else "#94a3b8" # Green vs Gray

        ctk.CTkButton(bot, text="Entregar", width=100, height=30, 
                      fg_color=del_color, state=del_state,
                      command=lambda s=shipment: self.deliver(s['id'])).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(bot, text="Incidencia", width=100, height=30, fg_color="#f59e0b", 
                      command=lambda s=shipment: self.incident(s['id'])).pack(side="left")

    def toggle_wd(self):
        wd = self.controller.get_active_workday()
        if wd: self.controller.end_workday()
        else: self.controller.start_workday()
        self.refresh_data()
        
    def generate_route(self):
        if not self.controller.get_active_workday():
            messagebox.showwarning("Acción no permitida", "Debes iniciar tu jornada para generar una ruta.")
            return
        try:
            route_data = self.controller.generate_my_route()
            if not route_data:
                return

            ordered = route_data.get('ordered_shipments', [])
            
            if ordered:
                # Update Next Stop
                next_pkg = ordered[0]
                self.next_address_lbl.configure(text=next_pkg['direccion'].upper())
                self.next_info_lbl.configure(text=f"Pedido: {next_pkg.get('codigo', '?')} - {next_pkg.get('descripcion', '')}")

                # Refresh list with ordered shipments
                # Note: generate_my_route returns partial dicts in 'ordered_shipments'. 
                # We need to map them back to full shipment objects or just use what we have.
                # The 'ordered_shipments' contains: id, codigo, direccion, latitud, longitud, estado, descripcion.
                # It misses 'cliente_nombre' which create_shipment_card uses.
                # So we should probably re-fetch or merge data. 
                # For simplicity, let's just refresh_data() normally. 
                # Ideally, refresh_data should respect order if we persisted it, but the user reverted that requirement.
                # So the list will just be the default list. 
                
                # Wait, if the list is not ordered, the "Next Delivery" label might contradict the list.
                # But since we reverted "caching order", the list is just "pending shipments".
                # However, generate_route DOES return an ordered list.
                # Let's populate the scroll frame with THIS ordered list for now to show the route order visually.
                
                # We need to adapt the ordered dicts to what create_shipment_card expects
                for widget in self.scroll_frame.winfo_children():
                    widget.destroy()

                for i, s in enumerate(ordered):
                    # construct a compat dict
                    s_compat = {
                        'id': s['id'],
                        'codigo_seguimiento': s.get('codigo'),
                        'estado': s.get('estado', 'ASIGNADO'),
                        'cliente_nombre': 'Ver detalle', # Missing in simplified route obj
                        'direccion_destino': s['direccion']
                    }
                    self.create_shipment_card(i + 1, s_compat)

            # Update Map on widget
            self.plot_route_on_widget(route_data)

        except Exception as e:
            messagebox.showerror("Error Ruta", str(e))

    def plot_route_on_widget(self, route_data):
        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()

        coords = route_data.get('geometry_coordinates', [])
        if not coords: return

        # Set Path
        self.map_widget.set_path(coords, color="blue", width=5)
        
        # Fit map (take first coord)
        if len(coords) > 0:
            self.map_widget.set_position(coords[0][0], coords[0][1])
            self.map_widget.set_zoom(13)

        # Markers
        # Start
        start_pos = coords[0]
        self.map_widget.set_marker(start_pos[0], start_pos[1], text="INICIO", marker_color_circle="green")
        
        # End (Warehouse)
        end_pos = coords[-1]
        self.map_widget.set_marker(end_pos[0], end_pos[1], text="ALMACÉN", marker_color_circle="red")

        # Shipments
        ordered = route_data.get('ordered_shipments', [])
        for i, pkg in enumerate(ordered):
            lat = float(pkg['latitud'])
            lon = float(pkg['longitud'])
            self.map_widget.set_marker(
                lat, lon, 
                text=f"{i+1}", 
                marker_color_circle="blue"
            )

    def deliver(self, sid):
        if not self.controller.get_active_workday():
            messagebox.showwarning("Acción no permitida", "Debes iniciar tu jornada para marcar entregas.")
            return

        if sid:
            try:
                self.controller.deliver_shipment(sid)
                messagebox.showinfo("Entrega", "Paquete entregado con éxito.")
                self.refresh_data()
                # Re-generar ruta para actualizar el "Siguiente"
                self.generate_route()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def incident(self, sid):
        if not self.controller.get_active_workday():
            messagebox.showwarning("Acción no permitida", "Debes iniciar tu jornada para reportar incidencias.")
            return
        
        if sid:
            msg = tk.simpledialog.askstring("Incidencia", "Descripción:")
            if msg: self.controller.report_incident(sid, msg); self.refresh_data()
            
    def get_help_text(self):
        return (
            "Panel del Repartidor:\n\n"
            "- Pulsar 'Iniciar/Fin' para comenzar o finalizar tu jornada.\n"
            "- Seleccionar un envío y pulsar 'Entregado' para marcar entrega.\n"
            "- 'Incidencia' permite reportar problemas en un envío.\n"
            "- 'Generar Ruta' optimiza tu recorrido y abre un mapa.\n"
        )

    def get_options(self):
        # Actions refer to controller methods
        return [
            ("Iniciar/Finalizar Jornada", lambda: self.controller.start_workday() if not self.controller.get_active_workday() else self.controller.end_workday()),
            ("Generar Ruta", lambda: self.generate_route()),
            ("Actualizar", lambda: self.refresh_data()),
        ]

# ==========================================
# CLIENTE
# ==========================================
class CustomerView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("Mis Pedidos")

        # Scrollable container for cards
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Bottom Action Bar (Just Refresh)
        act_f = ctk.CTkFrame(self, fg_color="transparent")
        act_f.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(act_f, text="Actualizar Lista", command=self.refresh_data).pack(side="right")

    def refresh_data(self):
        shipments = self.controller.get_my_shipments()
        
        # Clear
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        if not shipments:
             ctk.CTkLabel(self.scroll_frame, text="No tienes pedidos activos.", font=ctk.CTkFont(size=16)).pack(pady=20)
             return

        for s in shipments:
            self.create_shipment_card(s)

    def create_shipment_card(self, shipment):
        card = ctk.CTkFrame(self.scroll_frame, fg_color=("#ffffff", "#334155"), border_width=1, border_color="#cbd5e1")
        card.pack(fill="x", pady=10, padx=5)

        # Header: Code + Status
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        code = shipment.get('codigo_seguimiento') or str(shipment['id'])
        ctk.CTkLabel(header, text=f"Pedido: {code}", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        st_color = "#3b82f6"
        if shipment['estado'] == "ENTREGADO": st_color = "#10b981"
        elif shipment['estado'] == "INCIDENCIA": st_color = "#ef4444"
        
        ctk.CTkLabel(header, text=shipment['estado'], text_color=st_color, font=ctk.CTkFont(weight="bold")).pack(side="right")

        # Body: Description
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=15, pady=5)
        
        desc = shipment.get('descripcion') or "Sin descripción"
        ctk.CTkLabel(body, text=desc, font=ctk.CTkFont(size=14), wraplength=600, anchor="w", justify="left").pack(fill="x")

        # Footer: Buttons
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=15, pady=(10, 15))

        sid = shipment['id']
        
        ctk.CTkButton(footer, text="Detalles / ETA", width=120, height=32, 
                      command=lambda: self.details(sid)).pack(side="left", padx=(0, 10))
                      
        if shipment['estado'] == "ENTREGADO":
             ctk.CTkButton(footer, text="Valorar", width=100, height=32, fg_color="#f59e0b",
                           command=lambda: self.rate(sid)).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(footer, text="Ver Repartidor", width=120, height=32, fg_color="#64748b",
                      command=lambda: self.view_courier(sid)).pack(side="left")

    def details(self, sid):
        det = self.controller.get_shipment_details(sid)
        eta = self.controller.calculate_eta(sid)
        
        eta_str = eta.get("texto_mostrar", f"{eta.get('eta_minutos', '?')} min")
        
        msg = f"--- DETALLES ---\n\n"
        msg += f"Código: {det.get('codigo_seguimiento')}\n"
        msg += f"Descripción: {det.get('descripcion')}\n"
        msg += f"Origen: {det['direccion_origen']}\n"
        msg += f"Destino: {det['direccion_destino']}\n"
        msg += f"\nEstado: {det['estado']}\n"
        
        if det['estado'] not in ['ENTREGADO', 'CANCELADO']:
             msg += f"ETA Estimado: {eta_str}\n"

        messagebox.showinfo("Detalles del Pedido", msg)

    def rate(self, sid):
        score = tk.simpledialog.askinteger("Valorar", "Puntuación (1-5):", minvalue=1, maxvalue=5)
        if score:
            com = tk.simpledialog.askstring("Valorar", "Comentario (Opcional):")
            self.controller.rate_delivery(sid, score, com)

    def view_courier(self, sid):
        det = self.controller.get_shipment_details(sid)
        cid = det.get('id_mensajero')
        if cid:
            p = self.controller.get_courier_profile(cid)
            info = f"Nombre: {p['nombre']} {p['apellidos']}\n"
            info += f"Puntuación Media: {p.get('puntuacion_media', 'N/A')}\n"
            info += f"Total Entregas: {p.get('total_entregas', 0)}"
            messagebox.showinfo("Información del Repartidor", info)
        else:
            messagebox.showinfo("Info", "Este pedido aún no tiene un repartidor asignado.")

    def get_help_text(self):
        return (
            "Panel Cliente:\n\n"
            "- Cada tarjeta representa un pedido.\n"
            "- Usa 'Detalles / ETA' para ver el tiempo estimado de llegada.\n"
            "- Si el pedido fue entregado, puedes 'Valorar' el servicio.\n"
            "- 'Ver Repartidor' muestra quién te trae el paquete.\n"
        )

    def get_options(self):
        return [
            ("Actualizar", lambda: self.refresh_data()),
            ("Ver Ayuda", lambda: self.open_help()),
        ]