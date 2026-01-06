import customtkinter as ctk
from moval.views.base_view import BaseView

class ShipmentDialog(ctk.CTkToplevel):
    def __init__(self, parent_view: BaseView, controller):
        super().__init__(parent_view)
        self.controller = controller
        self.title("Detalles del Envío")
        self.geometry("400x300")
        self.after(100, self.focus_force)
        self.resizable(False, False)

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Detalles del Envío", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

        # Aquí se pueden agregar más controles para mostrar los detalles del envío.
        self.shipment_details_label = ctk.CTkLabel(frame, text="Detalles del envío aquí", font=ctk.CTkFont(size=14))
        self.shipment_details_label.pack(pady=10)

        # Puedes agregar más botones para diferentes acciones relacionadas con los envíos, como editar o eliminar.
        self.btn_close = ctk.CTkButton(frame, text="Cerrar", command=self.destroy)
        self.btn_close.pack(pady=(10, 0))

    def update_details(self, details):
        """Método para actualizar los detalles del envío"""
        self.shipment_details_label.configure(text=details)