import customtkinter as ctk
from moval.views.base_view import BaseView
from tkinter import messagebox, simpledialog, ttk
from moval.views.shipment_dialog import ShipmentDialog
from moval.views.create_shipment_dialog import CreateShipmentDialog
import sqlite3

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
        
        ctk.CTkButton(ctrl_reg, text="Crear Paquete", width=120, fg_color="#10b981", hover_color="#059669", command=self.open_create_dialog).pack(side="left", padx=5)
        
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

    def open_create_dialog(self):
        CreateShipmentDialog(self, self.controller, on_success_callback=self.refresh_data)

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
        
        # Contenedor general para controles de rol (dos filas)
        self.role_frame = ctk.CTkFrame(layout, fg_color="transparent")
        # NOTA: no lo packeamos aquí para que esté oculto hasta que se encuentre usuario
        # (será packeado en search_user)
        
        # --- fila superior: label + combo + actualizar ---
        top_row = ctk.CTkFrame(self.role_frame, fg_color="transparent")
        top_row.pack(pady=(0, 6))
        ctk.CTkLabel(top_row, text="Nuevo Rol:").pack(side="left", padx=5)
        self.role_combo = ctk.CTkComboBox(top_row, values=["Cliente", "Repartidor", "Administrador"])
        self.role_combo.pack(side="left", padx=5)
        self.btn_upd_role = ctk.CTkButton(top_row, text="Actualizar Rol", command=self.update_role)
        self.btn_upd_role.pack(side="left", padx=5)
        
        # --- fila inferior: botón BORRAR (oculto inicialmente) ---
        bottom_row = ctk.CTkFrame(self.role_frame, fg_color="transparent")
        bottom_row.pack(pady=(0, 0))
        self.btn_delete_user = ctk.CTkButton(
            bottom_row,
            text="Borrar usuario",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.delete_user
        )

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
            score = r['puntuacion']
            stars_str = "★" * int(score) + "☆" * (5 - int(score))
            score_display = f"{stars_str} ({score})"
            self.tree_rat.insert("", "end", values=(r['fecha'], r['autor'], r['mensajero'] or "", score_display, r['comentario']))

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

            media_val = c['media']
            if media_val is not None and media_val > 0:
                 stars_count = int(round(media_val))
                 stars_str = "★" * stars_count + "☆" * (5 - stars_count)
                 media_display = f"{stars_str} ({media_val:.1f})"
            else:
                 media_display = "☆☆☆☆☆ (N/A)"

            self.tree_couriers.insert("", "end", values=(
                f"{c['nombre']} {c['apellidos']}",
                status_text,
                c.get('fecha_inicio') or "---",
                salida_text,
                media_display
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

            # Mostrar contenedor de rol (si no está visible). Packear sin anchor => centrado por defecto.
            try:
                if not self.role_frame.winfo_ismapped():
                    self.role_frame.pack(pady=10)
            except Exception:
                try:
                    self.role_frame.pack(pady=10)
                except:
                    pass

            # Pre-seleccionar el rol actual en el combo (si mapeable)
            role_map = {"CUSTOMER": "Cliente", "COURIER": "Repartidor", "ADMIN": "Administrador", "Cliente":"Cliente"}
            current_role_label = role_map.get(u.get("role"), role_map.get(u.get("rol"), "Cliente"))
            try:
                self.role_combo.set(current_role_label)
            except:
                pass

            # Mostrar botón borrar dentro de la fila inferior (si no está packeado)
            try:
                if not self.btn_delete_user.winfo_ismapped():
                    # lo empaquetamos con fill="x" para que el botón ocupe la anchura del bottom_row
                    self.btn_delete_user.pack(fill="x", padx=5, pady=(6, 0))
            except Exception:
                try:
                    self.btn_delete_user.pack(fill="x", padx=5, pady=(6, 0))
                except:
                    pass
        else:
            self.user_info_lbl.configure(text="No encontrado.")
            # ocultar controles de rol
            try:
                if self.role_frame.winfo_ismapped():
                    self.role_frame.pack_forget()
            except:
                try:
                    self.role_frame.pack_forget()
                except:
                    pass
            # ocultar boton borrar (si está)
            try:
                if self.btn_delete_user.winfo_ismapped():
                    self.btn_delete_user.pack_forget()
            except:
                try:
                    self.btn_delete_user.pack_forget()
                except:
                    pass
        
    def update_role(self):
        roles = {"Cliente": "CUSTOMER", "Repartidor": "COURIER", "Administrador": "ADMIN"}
        self.controller.change_user_role(self.found_user['email'], roles[self.role_combo.get()])
        self.search_user()
        
    def get_help_text(self):
        return (
            "Panel de Administración:\n\n"
            "- 'Asignar' y 'Desasignar' en las diferentes pestañas para gestionar a los repartidores.\n"
            "- 'Reasignar' una incidencia para poder poner el envío en marcha de nuevo \n"
            "- Usa 'Ver Detalles' para ver información completa de un envío.\n"
            "- En la pestaña Usuarios puedes buscar y cambiar roles de un usuario. También podrás eliminarlo\n"
            "- En la sección 'Repartidores', puedes observar el horario de los mismos \n"
            "- En la sección 'Valoraciones', puedes revisar la puntuación media de cada repartidor\n"
        )
        
    def delete_user(self):
        if not hasattr(self, "found_user") or not self.found_user:
            messagebox.showwarning("Selecciona un usuario", "Busca y selecciona primero un usuario a borrar.")
            return

        uid = self.found_user.get("id")
        if not uid:
            messagebox.showerror("Error", "ID de usuario no válido.")
            return

        # Evitar que el admin se borre a sí mismo (opcional)
        if self.controller.current_user and self.controller.current_user.get("id") == uid:
            messagebox.showwarning("Operación no permitida", "No puedes borrar tu propia cuenta mientras estés logueado.")
            return

        ans = messagebox.askyesno("Confirmar borrado",
                                f"¿Seguro que quieres borrar a {self.found_user.get('nombre')} {self.found_user.get('apellidos')}?\n"
                                "Esto eliminará también TODOS sus paquetes relacionados.")
        if not ans:
            return

        ok = self.controller.delete_user(uid)
        if ok:
            self.search_entry.delete(0, "end")
            self.user_info_lbl.configure(text="Usuario eliminado.")
            try:
                self.role_frame.pack_forget()
            except:
                pass
            try:
                if self.btn_delete_user.winfo_ismapped():
                    self.btn_delete_user.pack_forget()
            except:
                pass
            try:
                self.refresh_data()
            except:
                pass


    def get_options(self):
        return []