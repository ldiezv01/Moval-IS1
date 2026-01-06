import customtkinter as ctk
from datetime import datetime

class NotificationDialog(ctk.CTkToplevel):
    def __init__(self, parent, notifications, on_close_callback=None):
        super().__init__(parent)
        self.title("Notificaciones")
        self.geometry("400x500")
        self.resizable(False, False)
        self.on_close_callback = on_close_callback
        
        # Modal
        self.transient(parent)
        self.grab_set()
        self.after(100, self.focus_force)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(header, text="Historial de Entregas", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # List
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if not notifications:
            ctk.CTkLabel(self.scroll, text="No hay notificaciones recientes.", text_color="gray").pack(pady=20)
        else:
            for notif in notifications:
                self.create_item(notif)
                
        # Close btn
        ctk.CTkButton(self, text="Cerrar", command=self.close).pack(pady=10)
        
        # Mark as read on open (conceptually) or close
        # We will trigger the callback when closing to update parent UI

    def close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def create_item(self, n):
        card = ctk.CTkFrame(self.scroll, fg_color=("#ffffff", "#334155"), border_width=1, border_color="#cbd5e1")
        card.pack(fill="x", pady=5, padx=5)
        
        # Status Icon (Dot)
        is_unread = (n.get('notificado_cliente', 0) == 0)
        dot_color = "#ef4444" if is_unread else "transparent"
        
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=10)
        
        # Dot
        if is_unread:
            lbl_dot = ctk.CTkLabel(row, text="●", text_color=dot_color, font=ctk.CTkFont(size=16))
            lbl_dot.pack(side="left", padx=(0, 5))
            
        # Content
        content = ctk.CTkFrame(row, fg_color="transparent")
        content.pack(side="left", fill="x", expand=True)
        
        code = n.get('codigo_seguimiento') or f"#{n['id']}"
        time_str = self.time_ago(n.get('fecha_entrega_real'))
        
        ctk.CTkLabel(content, text=f"Pedido {code} entregado", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(content, text=time_str, font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w")

    def time_ago(self, date_str):
        if not date_str: return "Recientemente"
        try:
            dt = None
            if isinstance(date_str, datetime):
                dt = date_str
            elif isinstance(date_str, str):
                # Eliminar microsegundos si existen (2023-01-01 10:00:00.123 -> 2023-01-01 10:00:00)
                if "." in date_str:
                    date_str = date_str.split(".")[0]
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            else:
                return "Fecha desconocida"

            now = datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"Hace {diff.days} día(s)"
            seconds = diff.total_seconds()
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            
            if hours > 0:
                return f"Hace {hours}h {minutes}m"
            if minutes > 0:
                return f"Hace {minutes} min"
            return "Hace un momento"
        except Exception as e:
            # print(f"DEBUG Date Error: {e}")
            return str(date_str)
