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

        # Botón
        tk.Button(self, text="Entrar", command=self.perform_login, bg="#4CAF50", fg="white", width=15).pack(pady=20)

    def perform_login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        self.controller.login(email, password)

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

        # --- Zona de Gestión ---
        controls = tk.LabelFrame(self, text="Gestión de Asignaciones", padx=10, pady=10)
        controls.pack(fill="x", pady=10)

        # Selector de Mensajero
        tk.Label(controls, text="Seleccionar Mensajero:").pack(side="left", padx=5)
        self.courier_combo = ttk.Combobox(controls, state="readonly", width=25)
        self.courier_combo.pack(side="left", padx=5)
        
        # Botones de Acción
        tk.Button(controls, text="Asignar Seleccionados", command=self.assign_shipments, bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(controls, text="Desasignar", command=self.unassign_shipment, bg="#FF9800", fg="white").pack(side="left", padx=5)
        tk.Button(controls, text="Actualizar Lista", command=self.refresh_data).pack(side="left", padx=5)

        # --- Tabla de Envíos Pendientes ---
        tk.Label(self, text="Envíos Pendientes / Sin Asignar", font=("Arial", 10, "bold")).pack(anchor="w")
        
        cols = ("ID", "Código", "Origen", "Destino", "Estado", "Mensajero")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="extended")
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True)

    def refresh_data(self):
        # 1. Cargar Mensajeros Disponibles
        couriers = self.controller.get_available_couriers()
        # Guardamos referencia ID -> Nombre
        self.courier_map = {f"{c['nombre']} {c['apellidos']} (ID: {c['id']})": c['id'] for c in couriers}
        self.courier_combo['values'] = list(self.courier_map.keys())
        if self.courier_map: self.courier_combo.current(0)

        # 2. Cargar Paquetes (Todos o Pendientes)
        shipments = self.controller.get_all_shipments()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Llenar tabla
        for s in shipments:
            # Filtramos visualmente o mostramos todo. Mostremos todo para que pueda desasignar.
            self.tree.insert("", "end", values=(s['id'], s['codigo_seguimiento'], s['direccion_origen'], s['direccion_destino'], s['estado'], s.get('id_mensajero', '')))

    def assign_shipments(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione al menos un paquete de la lista.")
            return
            
        courier_str = self.courier_combo.get()
        if not courier_str:
            messagebox.showwarning("Aviso", "Seleccione un mensajero del desplegable.")
            return

        courier_id = self.courier_map[courier_str]
        shipment_ids = [self.tree.item(item)['values'][0] for item in selection] # ID es col 0

        self.controller.assign_shipments(shipment_ids, courier_id)
        self.refresh_data()

    def unassign_shipment(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Seleccione un paquete.")
            return
        
        # Unassign de uno en uno o lote (el backend lo soporta de uno en uno por ahora)
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