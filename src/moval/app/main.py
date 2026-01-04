import tkinter as tk
from tkinter import messagebox
import sys
import os

# Ajuste de path para que encuentre 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')))

# Imports de Dominio y Persistencia
from moval.persistence.repositories import UserRepo, SessionRepo, ShipmentRepo, CourierRepo, WorkdayRepo, IncidentRepo, RatingRepo
from moval.security.password_hasher import PasswordHasher
from moval.services.clock import Clock

# Imports de Casos de Uso
from moval.usecases.login import Login
from moval.usecases.list_pending_shipments import ListPendingShipments
from moval.usecases.list_available_couriers import ListAvailableCouriers
from moval.usecases.assign_shipment import AssignShipments
from moval.usecases.unassign_shipment import UnassignShipment
from moval.usecases.list_shipments import ListShipments
from moval.usecases.start_workday import StartWorkday
from moval.usecases.end_workday import EndWorkday
from moval.usecases.get_active_workday import GetActiveWorkday
from moval.usecases.deliver_shipment import DeliverShipment
from moval.usecases.report_incident import ReportIncident
from moval.usecases.get_shipment_details import GetShipmentDetails
from moval.usecases.calculate_eta import CalculateETA
from moval.usecases.rate_delivery import RateDelivery
from moval.usecases.register_user import RegisterUser
from moval.usecases.change_user_role import ChangeUserRole

# Import de Vistas
from moval.app.views import LoginView, AdminView, CourierView, CustomerView, RegisterView

class MovalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Moval Logistics System")
        self.geometry("900x600")
        
        # 0. Autoinicialización de Base de Datos (Modo Demo para evaluación)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        db_file = os.path.join(project_root, 'db', 'moval.db')
        
        if not os.path.exists(db_file):
            print("Base de datos no detectada. Generando escenario de demostración...")
            try:
                if project_root not in sys.path:
                    sys.path.append(project_root)
                from db.init_db import init_db
                init_db()
            except Exception as e:
                print(f"Error inicializando datos de prueba: {e}")

        # 1. Inicialización de Capa de Datos (Clean Architecture)
        self.user_repo = UserRepo()
        self.session_repo = SessionRepo()
        self.shipment_repo = ShipmentRepo()
        self.courier_repo = CourierRepo()
        self.workday_repo = WorkdayRepo()
        self.incident_repo = IncidentRepo()
        self.rating_repo = RatingRepo()
        
        self.clock = Clock()
        self.hasher = PasswordHasher()

        # 2. Inicialización de Casos de Uso
        self.uc_login = Login(self.user_repo, self.session_repo, self.hasher)
        self.uc_register = RegisterUser(self.user_repo, self.hasher)
        
        # Admin
        self.uc_list_pending = ListPendingShipments(self.shipment_repo)
        self.uc_list_couriers = ListAvailableCouriers(self.courier_repo)
        self.uc_assign = AssignShipments(self.shipment_repo, self.courier_repo)
        self.uc_unassign = UnassignShipment(self.shipment_repo)
        self.uc_list_all = ListShipments(self.shipment_repo) # Para que admin vea todo
        self.uc_change_role = ChangeUserRole(self.user_repo)
        
        # Courier
        self.uc_list_my_shipments = ListShipments(self.shipment_repo)
        self.uc_start_workday = StartWorkday(self.workday_repo, self.clock)
        self.uc_end_workday = EndWorkday(self.workday_repo, self.clock)
        self.uc_get_workday = GetActiveWorkday(self.workday_repo)
        self.uc_deliver = DeliverShipment(self.shipment_repo, self.clock)
        self.uc_incident = ReportIncident(self.shipment_repo, self.incident_repo, self.clock)
        
        # Customer
        self.uc_details = GetShipmentDetails(self.shipment_repo)
        self.uc_eta = CalculateETA(self.shipment_repo, self.clock)
        self.uc_rate = RateDelivery(self.shipment_repo, self.rating_repo)

        # Estado Global
        self.current_user = None # {id, role, ...}
        
        # 3. Gestión de Vistas
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.frames = {}
        
        for F in (LoginView, AdminView, CourierView, CustomerView, RegisterView):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginView)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        # Si la vista tiene método refresh_data, llamarlo al mostrar
        if hasattr(frame, "refresh_data") and self.current_user:
            frame.refresh_data()

    def logout(self):
        self.current_user = None
        self.show_frame(LoginView)

    # ==========================================
    # MÉTODOS CONTROLADORES (Bridge UI <-> UseCases)
    # ==========================================
    
    def login(self, email, password):
        try:
            user = self.uc_login.execute(email, password)
            self.current_user = user
            role = user['role']
            
            if role == 'ADMIN':
                self.show_frame(AdminView)
            elif role == 'COURIER':
                self.show_frame(CourierView)
            elif role == 'CUSTOMER':
                self.show_frame(CustomerView)
            else:
                messagebox.showerror("Error", f"Rol desconocido: {role}")
        except Exception as e:
            messagebox.showerror("Login Fallido", str(e))

    def register(self, data):
        try:
            self.uc_register.execute(data)
            messagebox.showinfo("Éxito", "Cuenta creada correctamente. Ya puede iniciar sesión.")
            self.show_frame(LoginView)
        except Exception as e:
            messagebox.showerror("Error de Registro", str(e))

    # --- ADMIN ---
    def get_available_couriers(self):
        try:
            return self.uc_list_couriers.execute(self.current_user)
        except Exception as e:
            print(e)
            return []

    def get_all_shipments(self):
        # Admin ve todo, o podríamos usar list_pending. AdminView pide "Pendientes"
        try:
            # Usamos list_pending para la tabla principal
            return self.uc_list_pending.execute(self.current_user)
        except Exception as e:
            print(e)
            return []

    def assign_shipments(self, shipment_ids, courier_id):
        try:
            self.uc_assign.execute(self.current_user, shipment_ids, courier_id)
            messagebox.showinfo("Éxito", "Paquetes asignados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def unassign_shipment(self, shipment_id):
        try:
            self.uc_unassign.execute(self.current_user, shipment_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_user_by_email(self, email):
        try:
            # Usamos el repo directamente para la búsqueda simple o creamos un UC si fuera necesario
            user = self.user_repo.get_by_email(email)
            return user
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    def change_user_role(self, email, new_role):
        try:
            self.uc_change_role.execute(self.current_user, email, new_role)
            messagebox.showinfo("Éxito", f"El rol del usuario {email} ha sido actualizado a {new_role}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- COURIER ---
    def get_active_workday(self):
        try:
            return self.uc_get_workday.execute(self.current_user['user_id'])
        except Exception:
            return None

    def start_workday(self):
        try:
            self.uc_start_workday.execute({"id": self.current_user['user_id'], "role": "COURIER"})
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def end_workday(self):
        try:
            self.uc_end_workday.execute({"id": self.current_user['user_id'], "role": "COURIER"})
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_my_shipments(self):
        try:
            # Reutiliza ListShipments que filtra por rol internamente
            actor = {"id": self.current_user['user_id'], "role": self.current_user['role']}
            return self.uc_list_my_shipments.execute(actor)
        except Exception as e:
            print(e)
            return []

    def deliver_shipment(self, shipment_id):
        try:
            actor = {"id": self.current_user['user_id'], "role": "COURIER"}
            self.uc_deliver.execute(actor, shipment_id)
            messagebox.showinfo("Éxito", "Paquete entregado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def report_incident(self, shipment_id, description):
        try:
            actor = {"id": self.current_user['user_id'], "role": self.current_user['role']}
            self.uc_incident.execute(actor, shipment_id, description)
            messagebox.showinfo("Reportado", "Incidencia registrada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- CUSTOMER ---
    def get_shipment_details(self, shipment_id):
        try:
            actor = {"id": self.current_user['user_id'], "role": self.current_user['role']}
            return self.uc_details.execute(actor, shipment_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return {}

    def calculate_eta(self, shipment_id):
        try:
            actor = {"id": self.current_user['user_id'], "role": self.current_user['role']}
            return self.uc_eta.execute(actor, shipment_id)
        except Exception as e:
            return {"eta_minutes": "Desc.", "error": str(e)}

    def rate_delivery(self, shipment_id, score, comment):
        try:
            actor = {"id": self.current_user['user_id'], "role": self.current_user['role']}
            self.uc_rate.execute(actor, shipment_id, score, comment)
            messagebox.showinfo("Gracias", "Valoración enviada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = MovalApp()
    app.mainloop()
