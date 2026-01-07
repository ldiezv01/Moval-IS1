import customtkinter as ctk
from tkinter import messagebox, simpledialog, ttk
from moval.views.base_view import BaseView
from moval.views.rating_dialog import VentanaValoracion
from moval.views.notification_dialog import NotificationDialog

class CustomerView(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_header("Mis Pedidos")

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_active = self.tabview.add("En Curso")
        self.tab_incidents = self.tabview.add("Incidencias")
        self.tab_delivered = self.tabview.add("Entregados")

        # Scrollable frames for each tab
        self.scroll_active = ctk.CTkScrollableFrame(self.tab_active, fg_color="transparent")
        self.scroll_active.pack(fill="both", expand=True)
        
        self.scroll_incidents = ctk.CTkScrollableFrame(self.tab_incidents, fg_color="transparent")
        self.scroll_incidents.pack(fill="both", expand=True)

        self.scroll_delivered = ctk.CTkScrollableFrame(self.tab_delivered, fg_color="transparent")
        self.scroll_delivered.pack(fill="both", expand=True)

        # Bottom Action Bar
        act_f = ctk.CTkFrame(self, fg_color="transparent")
        act_f.pack(fill="x", padx=20, pady=10)
        
        # Bell Button (Left aligned)
        self.btn_bell = ctk.CTkButton(act_f, text="🔔", width=50, command=self.open_notifications)
        self.btn_bell.pack(side="left")
        
        ctk.CTkButton(act_f, text="Actualizar Lista", command=self.refresh_data).pack(side="right")

    def refresh_data(self):
        shipments = self.controller.get_my_shipments()
        self.update_bell_status()
        
        # Clear all
        for f in [self.scroll_active, self.scroll_incidents, self.scroll_delivered]:
            for w in f.winfo_children():
                w.destroy()

        if not shipments:
             ctk.CTkLabel(self.scroll_active, text="No tienes pedidos activos.", font=ctk.CTkFont(size=16)).pack(pady=20)
             return

        for s in shipments:
            st = s['estado']
            target_frame = self.scroll_active
            
            if st == 'ENTREGADO':
                target_frame = self.scroll_delivered
            elif st == 'INCIDENCIA':
                target_frame = self.scroll_incidents
            elif st in ['REGISTRADO', 'ASIGNADO', 'EN_REPARTO']:
                target_frame = self.scroll_active
            else:
                # Fallback
                target_frame = self.scroll_active

            self.create_shipment_card(s, target_frame)
            
    def update_bell_status(self):
        notifs = self.controller.get_customer_notifications()
        # Count unread (notificado_cliente is 0 or NULL)
        unread = sum(1 for n in notifs if (n.get('notificado_cliente', 0) == 0))
        
        if unread > 0:
            self.btn_bell.configure(text=f"🔔 {unread}", fg_color="#ef4444") # Red
        else:
            self.btn_bell.configure(text="🔔", fg_color="#3b82f6") # Default Blue

    def open_notifications(self):
        notifs = self.controller.get_customer_notifications()
        
        def on_close():
            self.controller.mark_notifications_read()
            self.update_bell_status()
            
        NotificationDialog(self, notifs, on_close_callback=on_close)

    def create_shipment_card(self, shipment, parent_frame):
        card = ctk.CTkFrame(parent_frame, fg_color=("#ffffff", "#334155"), border_width=1, border_color="#cbd5e1")
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
        
        # Lógica de ETA modificada para Incidencias
        if det['estado'] == 'INCIDENCIA':
            eta_str = "INCIDENCIA: Su pedido será reasignado."
        else:
            eta = self.controller.calculate_eta(sid)
            eta_str = eta.get("texto_mostrar", f"{eta.get('eta_minutos', '?')} min")
        
        msg = f"--- DETALLES ---\n\n"
        msg += f"Código: {det.get('codigo_seguimiento')}\n"
        msg += f"Descripción: {det.get('descripcion')}\n"
        msg += f"Origen: {det['direccion_origen']}\n"
        msg += f"Destino: {det['direccion_destino']}\n"
        msg += f"\nEstado: {det['estado']}\n"
        
        # Mostrar ETA solo si NO es entregado, cancelado O incidencia
        if det['estado'] not in ['ENTREGADO', 'CANCELADO', 'INCIDENCIA']:
             msg += f"ETA Estimado: {eta_str}\n"
        elif det['estado'] == 'INCIDENCIA':
             msg += f"\nNOTA: {eta_str}\n"

        if det.get("ultima_incidencia"):
             msg += f"\nMotivo Incidencia: {det.get('ultima_incidencia')}\n"

        messagebox.showinfo("Detalles del Pedido", msg)

    def rate(self, sid):
        def on_submit(score, comment):
            if score > 0:
                self.controller.rate_delivery(sid, score, comment)
                self.refresh_data()
        
        VentanaValoracion(self, callback=on_submit)

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
            "- Cada tarjeta representa un pedido. Usa 'Detalles / ETA' para ver su información de utilidad\n"
            "- 'Ver Repartidor' muestra quién te trae el paquete.\n"
            "- Si el pedido fue entregado, puedes 'Valorar' el servicio en la pestaña 'Entregados'.\n"
        )

    def get_options(self):
        return []