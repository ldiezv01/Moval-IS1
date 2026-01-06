import customtkinter as ctk
from tkinter import messagebox
from moval.views.base_view import BaseView

class CreateShipmentDialog(ctk.CTkToplevel):
    def __init__(self, parent_view: BaseView, controller, on_success_callback=None):
        super().__init__(parent_view)
        self.controller = controller
        self.on_success = on_success_callback
        
        self.title("Crear Nuevo Paquete")
        self.geometry("600x650")
        self.after(100, self.focus_force)
        self.resizable(False, False)

        # Main Layout
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.main_frame, text="Datos del Envío", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 15))

        # Form
        self.entries = {}
        
        # Descripción
        ctk.CTkLabel(self.main_frame, text="Descripción del contenido:").pack(anchor="w", padx=10)
        self.entries['desc'] = ctk.CTkEntry(self.main_frame, placeholder_text="Ej: Documentos urgentes")
        self.entries['desc'].pack(fill="x", padx=10, pady=(0, 10))

        # Peso
        ctk.CTkLabel(self.main_frame, text="Peso (kg):").pack(anchor="w", padx=10)
        self.entries['peso'] = ctk.CTkEntry(self.main_frame, placeholder_text="Ej: 1.5")
        self.entries['peso'].pack(fill="x", padx=10, pady=(0, 10))

        # Origen
        ctk.CTkLabel(self.main_frame, text="Dirección de Origen:").pack(anchor="w", padx=10)
        self.entries['origen'] = ctk.CTkEntry(self.main_frame)
        self.entries['origen'].insert(0, "Almacén Central") # Default
        self.entries['origen'].pack(fill="x", padx=10, pady=(0, 10))

        # --- SECCION DESTINO ESTRUCTURADO ---
        dest_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        dest_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(dest_frame, text="Dirección de Destino", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0,5))
        
        # Calle
        self.entries['calle'] = ctk.CTkEntry(dest_frame, placeholder_text="Calle / Avenida")
        self.entries['calle'].pack(fill="x", pady=2)
        
        # Número y CP (Misca línea)
        row1 = ctk.CTkFrame(dest_frame, fg_color="transparent")
        row1.pack(fill="x", pady=2)
        
        self.entries['numero'] = ctk.CTkEntry(row1, placeholder_text="Número", width=80)
        self.entries['numero'].pack(side="left", padx=(0, 5))
        
        self.entries['cp'] = ctk.CTkEntry(row1, placeholder_text="Código Postal", width=100)
        self.entries['cp'].pack(side="left", padx=5)

        # Ciudad y Provincia (Misma línea)
        row2 = ctk.CTkFrame(dest_frame, fg_color="transparent")
        row2.pack(fill="x", pady=2)
        
        self.entries['ciudad'] = ctk.CTkEntry(row2, placeholder_text="Ciudad")
        self.entries['ciudad'].insert(0, "León")
        self.entries['ciudad'].pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.entries['provincia'] = ctk.CTkEntry(row2, placeholder_text="Provincia")
        self.entries['provincia'].insert(0, "León")
        self.entries['provincia'].pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(self.main_frame, text="* Se validará y geolocalizará automáticamente.", 
                     font=ctk.CTkFont(size=11, slant="italic"), text_color="gray").pack(anchor="w", padx=10, pady=(0, 10))
        # ------------------------------------

        # Cliente (Dropdown)
        ctk.CTkLabel(self.main_frame, text="Cliente Asignado:").pack(anchor="w", padx=10)
        self.customer_combo = ctk.CTkComboBox(self.main_frame, state="readonly", values=[])
        self.customer_combo.pack(fill="x", padx=10, pady=(0, 20))

        # Botones
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", command=self.destroy).pack(side="left", expand=True, padx=5)
        self.btn_create = ctk.CTkButton(btn_frame, text="Crear Paquete", command=self.create_shipment)
        self.btn_create.pack(side="right", expand=True, padx=5)

        # Cargar Clientes
        self.load_customers()

    def load_customers(self):
        customers = self.controller.get_all_customers()
        self.customer_map = {}
        display_values = []
        for c in customers:
            display = f"{c['nombre']} {c['apellidos']} ({c['email']})"
            self.customer_map[display] = c['id']
            display_values.append(display)
        
        if display_values:
            self.customer_combo.configure(values=display_values)
            self.customer_combo.set(display_values[0])
        else:
            self.customer_combo.configure(values=["Sin clientes registrados"])

    def create_shipment(self):
        # Gather data
        desc = self.entries['desc'].get()
        peso = self.entries['peso'].get()
        origen = self.entries['origen'].get()
        
        # Construct full address from parts
        calle = self.entries['calle'].get()
        numero = self.entries['numero'].get()
        cp = self.entries['cp'].get()
        ciudad = self.entries['ciudad'].get()
        provincia = self.entries['provincia'].get()
        
        if not calle or not ciudad:
            messagebox.showerror("Error", "Calle y Ciudad son obligatorios para la dirección.")
            return

        destino_completo = f"{calle}, {numero}, {cp}, {ciudad}, {provincia}".replace(", ,", ",")
        
        cust_str = self.customer_combo.get()
        if cust_str not in self.customer_map:
            messagebox.showerror("Error", "Seleccione un cliente válido.")
            return

        cust_id = self.customer_map[cust_str]
        
        data = {
            'descripcion': desc,
            'peso': peso,
            'direccion_origen': origen,
            'direccion_destino': destino_completo,
            'id_cliente': cust_id,
            # Campos extra para geocodificación precisa
            'calle': calle,
            'numero': numero,
            'cp': cp,
            'ciudad': ciudad,
            'provincia': provincia
        }

        # Disable button to prevent double submit
        self.btn_create.configure(state="disabled", text="Procesando...")
        self.update()

        try:
            # Call Controller
            self.controller.create_new_shipment(data)
            messagebox.showinfo("Éxito", f"Paquete creado.\nDirección: {destino_completo}")
            if self.on_success:
                self.on_success()
            self.destroy()
        except Exception as e:
            self.btn_create.configure(state="normal", text="Crear Paquete")
            messagebox.showerror("Error", str(e))