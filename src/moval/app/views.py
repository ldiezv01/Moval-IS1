import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class BaseFrame(tk.Frame):
    """Clase base para todas las vistas, facilita el acceso a la app principal."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=20, pady=20)

# ==========================================
# VISTA A: LOGIN
# ==========================================
class LoginView(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Título
        tk.Label(self, text="MOVAL LOGISTICS", font=("Arial", 20, "bold")).pack(pady=20)
        tk.Label(self, text="Iniciar Sesión", font=("Arial", 12)).pack(pady=10)

        # Campos
        tk.Label(self, text="Email:").pack(anchor="w")
        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.pack(pady=5)
        self.email_entry.insert(0, "admin@moval.com") # Default para pruebas

        tk.Label(self, text="Contraseña:").pack(anchor="w")
        self.pass_entry = tk.Entry(self, width=30, show="*")
        self.pass_entry.pack(pady=5)
        self.pass_entry.insert(0, "1234") # Default para pruebas

        # Botones
        tk.Button(self, text="Entrar", command=self.perform_login, bg="#4CAF50", fg="white", width=15).pack(pady=10)
        
        tk.Label(self, text="¿No tienes cuenta?").pack(pady=(10, 0))
        tk.Button(self, text="Registrarse", command=lambda: controller.show_frame(RegisterView), fg="blue", cursor="hand2", bd=0).pack()

    def perform_login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        self.controller.login(email, password)

# ==========================================
# VISTA: REGISTRO
# ==========================================
class RegisterView(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        tk.Label(self, text="CREAR CUENTA", font=("Arial", 18, "bold")).pack(pady=10)

        # Formulario
        fields = [("DNI:", "dni"), ("Nombre:", "nombre"), ("Apellidos:", "apellidos"), ("Email:", "email")]
        self.entries = {}

        for label_text, key in fields:
            tk.Label(self, text=label_text).pack(anchor="w")
            entry = tk.Entry(self, width=30)
            entry.pack(pady=5)
            self.entries[key] = entry

        tk.Label(self, text="Contraseña:").pack(anchor="w")
        self.pass_entry = tk.Entry(self, width=30, show="*")
        self.pass_entry.pack(pady=5)

        # Botones
        tk.Button(self, text="Registrarse", command=self.perform_register, bg="#2196F3", fg="white", width=15).pack(pady=20)
        tk.Button(self, text="Volver al Login", command=lambda: controller.show_frame(LoginView), bd=0, fg="grey").pack()

    def perform_register(self):
        data = {k: v.get() for k, v in self.entries.items()}
        data["password"] = self.pass_entry.get()
        self.controller.register(data)

# ==========================================
# VISTA B: ADMINISTRADOR
# ==========================================
class AdminView(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Header
        header = tk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Panel de Administrador", font=("Arial", 16, "bold")).pack(side="left")
        tk.Button(header, text="Cerrar Sesión", command=controller.logout).pack(side="right")

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # TAB 1: GESTIÓN DE ENVÍOS
        self.tab_shipments = tk.Frame(self.notebook, padx=10, pady=10)
        self.notebook.add(self.tab_shipments, text="Gestión de Envíos")
        self.setup_shipments_tab()

        # TAB 2: GESTIÓN DE USUARIOS
        self.tab_users = tk.Frame(self.notebook, padx=10, pady=10)
        self.notebook.add(self.tab_users, text="Gestión de Usuarios")
        self.setup_users_tab()

        # TAB 3: VALORACIONES
        self.tab_ratings = tk.Frame(self.notebook, padx=10, pady=10)
        self.notebook.add(self.tab_ratings, text="Valoraciones")
        self.setup_ratings_tab()

    def setup_shipments_tab(self):
        # ... (código existente) ...
        controls = tk.LabelFrame(self.tab_shipments, text="Asignación de Paquetes", padx=10, pady=10)
        controls.pack(fill="x", pady=10)

        tk.Label(controls, text="Mensajero:").pack(side="left", padx=5)
        self.courier_combo = ttk.Combobox(controls, state="readonly", width=25)
        self.courier_combo.pack(side="left", padx=5)
        
        tk.Button(controls, text="Asignar Selección", command=self.assign_shipments, bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(controls, text="Desasignar", command=self.unassign_shipment, bg="#FF9800", fg="white").pack(side="left", padx=5)
        tk.Button(controls, text="Refrescar", command=self.refresh_data).pack(side="right", padx=5)

        # --- Tabla ---
        tk.Label(self.tab_shipments, text="Listado Global de Envíos", font=("Arial", 10, "bold")).pack(anchor="w")
        
        cols = ("ID", "Código", "Origen", "Destino", "Estado", "Mensajero")
        self.tree = ttk.Treeview(self.tab_shipments, columns=cols, show="headings", selectmode="extended")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

    def setup_ratings_tab(self):
        tk.Button(self.tab_ratings, text="Actualizar", command=self.refresh_data).pack(anchor="e", pady=5)
        
        cols = ("Fecha", "Cliente", "Mensajero", "Puntuación", "Comentario")
        self.tree_ratings = ttk.Treeview(self.tab_ratings, columns=cols, show="headings")
        
        self.tree_ratings.heading("Fecha", text="Fecha")
        self.tree_ratings.column("Fecha", width=120)
        
        self.tree_ratings.heading("Cliente", text="Cliente")
        self.tree_ratings.column("Cliente", width=150)
        
        self.tree_ratings.heading("Mensajero", text="Mensajero")
        self.tree_ratings.column("Mensajero", width=150)
        
        self.tree_ratings.heading("Puntuación", text="Puntuación")
        self.tree_ratings.column("Puntuación", width=80, anchor="center")
        
        self.tree_ratings.heading("Comentario", text="Comentario")
        self.tree_ratings.column("Comentario", width=300)
        
        self.tree_ratings.pack(fill="both", expand=True)

    def setup_users_tab(self):
        # ... (código existente setup_users_tab) ...
        # Mapeo de roles para la interfaz
        self.role_display = {
            "CUSTOMER": "Cliente",
            "COURIER": "Repartidor",
            "ADMIN": "Administrador"
        }
        self.role_internal = {v: k for k, v in self.role_display.items()}

        # Buscador
        search_frame = tk.LabelFrame(self.tab_users, text="Buscar Usuario", padx=10, pady=10)
        search_frame.pack(fill="x", pady=10)

        tk.Label(search_frame, text="Email:").pack(side="left", padx=5)
        self.user_search_entry = tk.Entry(search_frame, width=30)
        self.user_search_entry.pack(side="left", padx=5)
        tk.Button(search_frame, text="Buscar", command=self.search_user).pack(side="left", padx=5)

        # Resultado de búsqueda
        self.user_info_frame = tk.LabelFrame(self.tab_users, text="Datos del Usuario", padx=10, pady=10)
        self.user_info_frame.pack(fill="x", pady=10)
        self.user_info_label = tk.Label(self.user_info_frame, text="Busque un usuario para ver sus detalles.", justify="left")
        self.user_info_label.pack(pady=5)

        # Cambio de Rol
        role_frame = tk.Frame(self.user_info_frame)
        role_frame.pack(fill="x", pady=5)
        
        tk.Label(role_frame, text="Nuevo Rol:").pack(side="left", padx=5)
        self.role_combo = ttk.Combobox(role_frame, values=list(self.role_display.values()), state="readonly")
        self.role_combo.pack(side="left", padx=5)
        self.btn_update_role = tk.Button(role_frame, text="Actualizar Rol", command=self.update_role, bg="#4CAF50", fg="white", state="disabled")
        self.btn_update_role.pack(side="left", padx=5)

    def search_user(self):
        # ... (código existente search_user) ...
        email = self.user_search_entry.get()
        user = self.controller.get_user_by_email(email)
        if user:
            self.current_searched_user = user
            rol_esp = self.role_display.get(user['role'], user['role'])
            info = f"ID: {user['id']}\nNombre: {user['nombre']} {user['apellidos']}\nEmail: {user['email']}\nRol Actual: {rol_esp}"
            self.user_info_label.config(text=info)
            self.role_combo.set(rol_esp)
            self.btn_update_role.config(state="normal")
        else:
            self.user_info_label.config(text="No se encontró ningún usuario.")
            self.btn_update_role.config(state="disabled")

    def update_role(self):
        # ... (código existente update_role) ...
        rol_seleccionado = self.role_combo.get()
        new_role = self.role_internal[rol_seleccionado]
        email = self.current_searched_user['email']
        self.controller.change_user_role(email, new_role)
        self.search_user() # Refrescar info

    def refresh_data(self):
        # 1. Cargar Mensajeros Disponibles
        couriers = self.controller.get_available_couriers()
        self.courier_map = {f"{c['nombre']} {c['apellidos']} (ID: {c['id']})": c['id'] for c in couriers}
        self.courier_combo['values'] = list(self.courier_map.keys())
        if self.courier_map: self.courier_combo.current(0)

        # 2. Cargar Paquetes
        shipments = self.controller.get_all_shipments()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for s in shipments:
            self.tree.insert("", "end", values=(s['id'], s['codigo_seguimiento'], s['direccion_origen'], s['direccion_destino'], s['estado'], s.get('id_mensajero', '')))

        # 3. Cargar Valoraciones (Nuevo)
        ratings = self.controller.get_all_ratings()
        for item in self.tree_ratings.get_children():
            self.tree_ratings.delete(item)
        for r in ratings:
            self.tree_ratings.insert("", "end", values=(r['fecha'], r['autor'], r['mensajero'] or "N/A", f"{r['puntuacion']}/5", r['comentario']))

    def assign_shipments(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione al menos un paquete.")
            return
        courier_str = self.courier_combo.get()
        if not courier_str:
            messagebox.showwarning("Aviso", "Seleccione un mensajero.")
            return
        courier_id = self.courier_map[courier_str]
        shipment_ids = [self.tree.item(item)['values'][0] for item in selection]
        self.controller.assign_shipments(shipment_ids, courier_id)
        self.refresh_data()

    def unassign_shipment(self):
        selection = self.tree.selection()
        if not selection: return
        for item in selection:
            sid = self.tree.item(item)['values'][0]
            self.controller.unassign_shipment(sid)
        self.refresh_data()


# ==========================================
# VISTA C: REPARTIDOR (COURIER)
# ==========================================
class CourierView(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Header
        header = tk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Panel de Repartidor", font=("Arial", 16, "bold")).pack(side="left")
        tk.Button(header, text="Cerrar Sesión", command=controller.logout).pack(side="right")

        # --- Control de Jornada ---
        self.workday_frame = tk.LabelFrame(self, text="Control de Jornada", padx=10, pady=10)
        self.workday_frame.pack(fill="x", pady=10)
        
        self.status_label = tk.Label(self.workday_frame, text="Estado: DESCONOCIDO", font=("Arial", 12))
        self.status_label.pack(side="left", padx=20)
        
        self.btn_start = tk.Button(self.workday_frame, text="Iniciar Jornada", command=self.start_workday, bg="#4CAF50", fg="white")
        self.btn_end = tk.Button(self.workday_frame, text="Finalizar Jornada", command=self.end_workday, bg="#F44336", fg="white")

        # --- Lista de Entregas ---
        tk.Label(self, text="Mis Paquetes Asignados", font=("Arial", 10, "bold")).pack(anchor="w")

        cols = ("ID", "Dirección", "Estado")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50)
        self.tree.heading("Dirección", text="Dirección Destino"); self.tree.column("Dirección", width=300)
        self.tree.heading("Estado", text="Estado"); self.tree.column("Estado", width=100)
        self.tree.pack(fill="both", expand=True)

        # Acciones de Entrega
        actions = tk.Frame(self)
        actions.pack(fill="x", pady=5)
        tk.Button(actions, text="Marcar como ENTREGADO", command=self.mark_delivered, bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(actions, text="Reportar Incidencia", command=self.report_issue, bg="#FF9800", fg="white").pack(side="left", padx=5)
        tk.Button(actions, text="Refrescar", command=self.refresh_data).pack(side="right")

    def refresh_data(self):
        # 1. Estado Jornada
        active_wd = self.controller.get_active_workday()
        if active_wd:
            self.status_label.config(text=f"Estado: ACTIVA (Inicio: {active_wd['fecha_inicio']})", fg="green")
            self.btn_start.pack_forget()
            self.btn_end.pack(side="left")
        else:
            self.status_label.config(text="Estado: INACTIVA", fg="red")
            self.btn_end.pack_forget()
            self.btn_start.pack(side="left")

        # 2. Paquetes
        shipments = self.controller.get_my_shipments()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for s in shipments:
            if s['estado'] != 'ENTREGADO': # Solo mostrar activos
                self.tree.insert("", "end", values=(s['id'], s['direccion_destino'], s['estado']))

    def start_workday(self):
        self.controller.start_workday()
        self.refresh_data()

    def end_workday(self):
        self.controller.end_workday()
        self.refresh_data()

    def mark_delivered(self):
        sel = self.tree.selection()
        if not sel: return
        sid = self.tree.item(sel[0])['values'][0]
        self.controller.deliver_shipment(sid)
        self.refresh_data()

    def report_issue(self):
        sel = self.tree.selection()
        if not sel: return
        sid = self.tree.item(sel[0])['values'][0]
        # Simple input dialog
        desc = simpledialog.askstring("Incidencia", "Describa el problema:")
        if desc:
            self.controller.report_incident(sid, desc)
            self.refresh_data()

# ==========================================
# VISTA D: CLIENTE (CUSTOMER)
# ==========================================
class CustomerView(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        header = tk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Mis Envíos", font=("Arial", 16, "bold")).pack(side="left")
        tk.Button(header, text="Cerrar Sesión", command=controller.logout).pack(side="right")

        cols = ("ID", "Descripción", "Estado", "ETA")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols: self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, pady=10)

        tk.Button(self, text="Valorar Entrega", command=self.rate_delivery, bg="#FFC107").pack(side="left", padx=5)
        tk.Button(self, text="Ver Detalles / ETA", command=self.show_details).pack(side="left", padx=5)
        tk.Button(self, text="Actualizar", command=self.refresh_data).pack(side="right")

    def refresh_data(self):
        shipments = self.controller.get_my_shipments()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for s in shipments:
            self.tree.insert("", "end", values=(s['id'], s['descripcion'], s['estado'], "Calcular..."))

    def show_details(self):
        sel = self.tree.selection()
        if not sel: return
        sid = self.tree.item(sel[0])['values'][0]
        
        details = self.controller.get_shipment_details(sid)
        eta_data = self.controller.calculate_eta(sid)
        
        # Uso de \n explícito para evitar problemas de multilinea en diferentes OS/editores
        msg = (f"Producto: {details.get('descripcion', '')}\n"
               f"Origen: {details.get('direccion_origen', '')}\n"
               f"Destino: {details.get('direccion_destino', '')}\n"
               f"Peso: {details.get('peso', '0')} kg\n\n"
               f"Tiempo Estimado (ETA): {eta_data.get('eta_minutos', 'Unknown')} minutos")
        
        messagebox.showinfo("Detalles del Envío", msg)

    def rate_delivery(self):
        sel = self.tree.selection()
        if not sel: return
        sid = self.tree.item(sel[0])['values'][0]
        state = self.tree.item(sel[0])['values'][2]

        if state != "ENTREGADO":
            messagebox.showerror("Error", "Solo puede valorar pedidos ENTREGADOS.")
            return

        score = simpledialog.askinteger("Valorar", "Puntuación (1-5):", minvalue=1, maxvalue=5)
        if score:
            comment = simpledialog.askstring("Valorar", "Comentario (Opcional):")
            self.controller.rate_delivery(sid, score, comment)