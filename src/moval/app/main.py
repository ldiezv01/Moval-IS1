import customtkinter as ctk
import sys
import os
from tkinter import messagebox

# Path Fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')))

# Lógica
from moval.persistence.repositories import UserRepo, SessionRepo, ShipmentRepo, CourierRepo, WorkdayRepo, IncidentRepo, RatingRepo
from moval.security.password_hasher import PasswordHasher
from moval.services.clock import Clock

from moval.usecases.login import Login
from moval.usecases.register_user import RegisterUser
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
from moval.usecases.change_user_role import ChangeUserRole
from moval.usecases.list_ratings import ListRatings
from moval.usecases.update_user_data import UpdateUserData
from moval.usecases.get_courier_profile import GetCourierProfile
from moval.services.route_service import RouteService
from moval.usecases.generate_delivery_route import GenerateDeliveryRoute

from moval.app.views import LoginView, RegisterView, AdminView, CourierView, CustomerView

class MovalApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Moval Logistics System")
        self.geometry("1100x750")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.init_db()
        
        # 1. Repositorios y Servicios
        self.user_repo = UserRepo()
        self.session_repo = SessionRepo()
        self.shipment_repo = ShipmentRepo()
        self.courier_repo = CourierRepo()
        self.workday_repo = WorkdayRepo()
        self.incident_repo = IncidentRepo()
        self.rating_repo = RatingRepo()
        self.clock = Clock()
        self.hasher = PasswordHasher()
        self.route_service = RouteService()

        # 2. Casos de Uso
        self.uc_login = Login(self.user_repo, self.session_repo, self.hasher)
        self.uc_register = RegisterUser(self.user_repo, self.hasher)
        self.uc_update_profile = UpdateUserData(self.user_repo)
        self.uc_list_all = ListShipments(self.shipment_repo)
        self.uc_list_couriers = ListAvailableCouriers(self.courier_repo)
        self.uc_assign = AssignShipments(self.shipment_repo, self.courier_repo)
        self.uc_unassign = UnassignShipment(self.shipment_repo)
        self.uc_change_role = ChangeUserRole(self.user_repo)
        self.uc_list_ratings = ListRatings(self.rating_repo)
        self.uc_start_wd = StartWorkday(self.workday_repo, self.clock)
        self.uc_end_wd = EndWorkday(self.workday_repo, self.clock)
        self.uc_get_wd = GetActiveWorkday(self.workday_repo)
        self.uc_deliver = DeliverShipment(self.shipment_repo, self.clock)
        self.uc_incident = ReportIncident(self.shipment_repo, self.incident_repo, self.clock)
        self.uc_details = GetShipmentDetails(self.shipment_repo, self.incident_repo, self.user_repo)
        self.uc_eta = CalculateETA(self.shipment_repo, self.route_service, self.clock)
        self.uc_rate = RateDelivery(self.shipment_repo, self.rating_repo)
        self.uc_courier_profile = GetCourierProfile(self.courier_repo, self.rating_repo, self.shipment_repo)
        self.uc_route = GenerateDeliveryRoute(self.shipment_repo, self.route_service, self.workday_repo)

        # 3. Estado
        self.current_user = None
        
        # 4. Contenedor de Vistas
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginView, RegisterView, AdminView, CourierView, CustomerView):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.switch_view("login")

    def init_db(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        db = os.path.join(root, 'db', 'moval.db')
        if not os.path.exists(db):
            if root not in sys.path: sys.path.append(root)
            from db.init_db import init_db
            init_db()

    def switch_view(self, name):
        name_map = {
            "login": LoginView, "register": RegisterView, 
            "admin": AdminView, "courier": CourierView, "customer": CustomerView
        }
        view_class = name_map[name]
        frame = self.frames[view_class]
        frame.tkraise()
        if hasattr(frame, "refresh_data") and self.current_user:
            frame.refresh_data()
            
    def on_close(self):
        """Handler para la X: confirmar y cerrar la app limpiamente."""
        try:
            if messagebox.askokcancel("Salir", "¿Deseas salir de Moval?"):
                # Si necesitas hacer limpieza: aquí es el lugar (persistir estado, cerrar conexiones…)
                self.destroy()
        except Exception:
            # En caso de que messagebox falle (entorno sin GUI), cerramos directo
            try:
                self.destroy()
            except:
                os._exit(0)

    # --- ACTIONS ---
    def login(self, email, password):
        try:
            user = self.uc_login.execute(email, password)
            user['id'] = user['user_id']
            self.current_user = user
            role = user['role']
            if role == "ADMIN": self.switch_view("admin")
            elif role == "COURIER": self.switch_view("courier")
            elif role == "CUSTOMER": self.switch_view("customer")
        except Exception as e: messagebox.showerror("Error", str(e))

    def logout(self):
        self.current_user = None
        self.switch_view("login")

    def register(self, data):
        try:
            self.uc_register.execute(data)
            messagebox.showinfo("Éxito", "Cuenta creada.")
            self.switch_view("login")
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_profile(self, data):
        try:
            # Recargar usuario para asegurar que tenemos sus datos
            actor = self.current_user
            updated = self.uc_update_profile.execute(actor, data)
            # Actualizar sesión local con los nuevos datos
            self.current_user.update(updated)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

    def get_current_user_data(self):
        """Recupera los datos frescos del usuario actual desde la BD."""
        if not self.current_user: return {}
        try:
            return self.user_repo.get(self.current_user['id']) or {}
        except:
            return {}

    # Admin
    def get_available_couriers(self):
        try: return self.uc_list_couriers.execute(self.current_user)
        except: return []

    def get_all_shipments(self):
        try: return self.uc_list_all.execute(self.current_user)
        except: return []

    def get_all_ratings(self):
        try: return self.uc_list_ratings.execute(self.current_user)
        except: return []

    def get_all_couriers_report(self):
        try:
            if self.current_user['role'] != 'ADMIN': return []
            return self.courier_repo.list_all_with_workday_info()
        except:
            return []

    def assign_shipments(self, sids, cid):
        try: self.uc_assign.execute(self.current_user, sids, cid)
        except Exception as e: messagebox.showerror("Error", str(e))

    def unassign_shipment(self, sid):
        try: self.uc_unassign.execute(self.current_user, sid)
        except Exception as e: messagebox.showerror("Error", str(e))

    def get_user_by_email(self, email):
        try: return self.user_repo.get_by_email(email)
        except: return None

    def change_user_role(self, email, role):
        try: self.uc_change_role.execute(self.current_user, email, role)
        except Exception as e: messagebox.showerror("Error", str(e))

    # Courier
    def get_active_workday(self):
        try: return self.uc_get_wd.execute(self.current_user)
        except: return None

    def start_workday(self):
        try: self.uc_start_wd.execute(self.current_user)
        except Exception as e: messagebox.showerror("Error", str(e))

    def end_workday(self):
        try: self.uc_end_wd.execute(self.current_user)
        except Exception as e: messagebox.showerror("Error", str(e))

    def get_my_shipments(self):
        try: return self.uc_list_all.execute(self.current_user)
        except: return []

    def deliver_shipment(self, sid):
        try: self.uc_deliver.execute(self.current_user, sid)
        except Exception as e: messagebox.showerror("Error", str(e))

    def report_incident(self, sid, desc):
        try: self.uc_incident.execute(self.current_user, sid, desc)
        except Exception as e: messagebox.showerror("Error", str(e))

    def generate_my_route(self):
        try:
            # Assumes current_user is Courier
            result = self.uc_route.execute(self.current_user['id'])
            return result
        except Exception as e:
            print(f"ERROR: {e}")
            messagebox.showerror("Error Generando Ruta", str(e))
            return None

    # Customer
    def get_shipment_details(self, sid):
        try: return self.uc_details.execute(self.current_user, sid)
        except: return {}

    def calculate_eta(self, sid):
        try: return self.uc_eta.execute(self.current_user, sid)
        except: return {"eta_minutos": "Error"}

    def rate_delivery(self, sid, score, com):
        try: self.uc_rate.execute(self.current_user, sid, score, com)
        except Exception as e: messagebox.showerror("Error", str(e))

    def get_courier_profile(self, cid):
        try: return self.uc_courier_profile.execute(self.current_user, cid)
        except: return None

if __name__ == "__main__":
    app = MovalApp()
    app.mainloop()
