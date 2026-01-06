import customtkinter as ctk
from tkinter import messagebox, simpledialog, ttk
from moval.views.base_view import BaseView

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
            
        self._show_pending_delivery_notifications()

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
        
    def _show_pending_delivery_notifications(self):
        """
        Llama repetidamente a controller.pop_next_delivery_notification()
        y muestra un messagebox para cada uno (uno a la vez).
        """
        # Sólo si hay user y es CUSTOMER
        user = getattr(self.controller, "current_user", None)
        if not user or user.get("role") != "CUSTOMER":
            return

        while True:
            notif = self.controller.pop_next_delivery_notification()
            if not notif:
                break

            # Construye el mensaje según los campos reales
            code = notif.get("codigo_seguimiento") or notif.get("codigo") or notif.get("id")
            desc = notif.get("descripcion") or ""
            delivered_at = notif.get("delivered_at") or notif.get("fecha_entrega_real") or ""

            msg = f"Tu pedido {code} ha sido entregado.\n\n{desc}"
            if delivered_at:
                msg += f"\n\nFecha entrega: {delivered_at}"

            # messagebox.showinfo es bloqueante (hasta que el usuario lo cierre),
            # eso produce el efecto "una notificación tras otra".
            try:
                messagebox.showinfo("Pedido entregado", msg)
            except Exception:
                # entornos sin GUI o errores: seguir sin romper
                pass
            
    def _show_pending_delivery_notifications(self):
        """
        Muestra popups uno a uno mediante messagebox.showinfo(),
        solicitando el siguiente paquete entregado que aún no hemos mostrado
        (usa el helper en MovalApp pop_next_delivery_notification_inmemory()).
        """
        # Comprobaciones rápidas
        user = getattr(self.controller, "current_user", None)
        if not user or user.get("role") != "CUSTOMER":
            return

        while True:
            notif = None
            try:
                notif = self.controller.pop_next_delivery_notification_inmemory()
            except Exception as e:
                print("DEBUG notify error:", e)
                break

            if not notif:
                break

            code = notif.get("codigo_seguimiento") or notif.get("codigo") or str(notif.get("id", "?"))
            desc = notif.get("descripcion") or ""
            delivered_at = notif.get("fecha_entrega_real") or notif.get("delivered_at") or ""

            msg = f"Tu pedido {code} ha sido entregado."
            if desc:
                msg += f"\n\n{desc}"
            if delivered_at:
                msg += f"\n\nFecha entrega: {delivered_at}"

            try:
                # showinfo bloquea la ejecución hasta que el usuario pulsa OK,
                # por eso cada notificación se mostrará una tras otra.
                messagebox.showinfo("Pedido entregado", msg)
            except Exception as e:
                print("DEBUG messagebox error:", e)
                break