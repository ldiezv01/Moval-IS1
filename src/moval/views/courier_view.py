import customtkinter as ctk
from tkinter import messagebox, simpledialog, ttk
import tkintermapview
from moval.views.base_view import BaseView
from tkinter import messagebox
from moval.views.incident_dialog import VentanaIncidencia

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
            def on_report(description):
                self.controller.report_incident(sid, description)
                self.refresh_data()
            
            VentanaIncidencia(self, callback=on_report)
            
    def get_help_text(self):
        return (
            "Panel del Repartidor:\n\n"
            "- Pulsar 'Iniciar/Finalizar Jornada' para comenzar o finalizar el periodo lectivo.\n"
            "- Pulsar 'Entregado' en un paquete para marcarlo como entregado.\n"
            "- Pulsar 'Incidencia' permite reportar problemas en un envío.\n"
            "- 'Generar Ruta' optimiza tu recorrido y crea una ruta en el mapa.\n"
        )

    def get_options(self):
        return []