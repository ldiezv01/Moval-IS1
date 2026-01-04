import sqlite3
from typing import Optional, List, Union
from moval.domain.enums import Role, ShipmentStatus
from datetime import datetime

# Clase base para manejar la conexión, no modifica la interfaz pública de los repos
class BaseSQLiteRepo:
    def __init__(self, db_path: str = "moval.db"):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        # Habilitar integridad referencial (Foreign Keys)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

class UserRepo(BaseSQLiteRepo):
    def get_by_email(self, email: str):
        with self._get_connection() as conn:
            # Seleccionamos todos los campos que podría necesitar el dominio
            cursor = conn.execute(
                "SELECT id, dni, nombre, apellidos, email, password_hash, rol as role, activo as is_active FROM Usuario WHERE email = ?", 
                (email,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def exists_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None
    
    # Metodo necesario para registrar usuarios
    def create(self, user_data: dict) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO Usuario (dni, nombre, apellidos, email, password_hash, rol) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_data.get("dni", ""), # DNI might be optional in some flows or required
                    user_data.get("nombre", ""),
                    user_data.get("apellidos", ""),
                    user_data.get("email"),
                    user_data.get("password_hash"), # Asumiendo que llega hasheado o texto plano segun decidas luego
                    user_data.get("role")
                )
            )
            return cursor.lastrowid

class SessionRepo:
    def create_session(self, user_id: int) -> str:
        # Implementación simple de token por ahora
        return f"session_{user_id}_{int(datetime.now().timestamp())}"

class ShipmentRepo(BaseSQLiteRepo):
    def list_pending(self) -> List[dict]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM Paquete WHERE estado = 'REGISTRADO'")
            return [dict(row) for row in cursor.fetchall()]

    def get(self, shipment_id: int) -> dict | None:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM Paquete WHERE id = ?", (shipment_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def assign(self, shipment_id: list[int], courier_id: int) -> None:
        # El parámetro shipment_id es una lista de ints
        with self._get_connection() as conn:
            for sid in shipment_id:
                conn.execute(
                    "UPDATE Paquete SET id_mensajero = ?, estado = 'ASIGNADO' WHERE id = ?",
                    (courier_id, sid)
                )

    def unassign(self, shipment_id: int) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE Paquete SET id_mensajero = NULL, estado = 'REGISTRADO' WHERE id = ?",
                (shipment_id,)
            )

    def update(self, shipment_id: int, fields: dict) -> None:
        if not fields: return
        # Construye la query dinámicamente
        query = "UPDATE Paquete SET " + ", ".join([f"{k} = ?" for k in fields.keys()]) + " WHERE id = ?"
        params = list(fields.values()) + [shipment_id]
        with self._get_connection() as conn:
            conn.execute(query, params)

    def set_status(self, shipment_id: int, status: ShipmentStatus, delivered_at: datetime | None = None) -> None:
        with self._get_connection() as conn:
            if delivered_at:
                conn.execute(
                    "UPDATE Paquete SET estado = ?, fecha_entrega_real = ? WHERE id = ?",
                    (status.value, delivered_at, shipment_id)
                )
            else:
                conn.execute(
                    "UPDATE Paquete SET estado = ? WHERE id = ?",
                    (status.value, shipment_id)
                )

    def list_all(self, filters: dict | None = None) -> List[dict]:
        query = "SELECT * FROM Paquete"
        params = []
        if filters:
            conditions = [f"{k} = ?" for k in filters.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(filters.values())
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def list_by_courier(self, courier_id: int, filters: dict | None = None) -> List[dict]:
        f = (filters or {}).copy()
        f["id_mensajero"] = courier_id
        return self.list_all(f)

    def list_by_customer(self, customer_id: int, filters: dict | None = None) -> List[dict]:
        f = (filters or {}).copy()
        f["id_cliente"] = customer_id
        return self.list_all(f)

    def count_by_courier(self, courier_id: int, filters: dict | None = None) -> int:
        return len(self.list_by_courier(courier_id, filters))


class CourierRepo(BaseSQLiteRepo):
    def list_available(self) -> List[dict]:
        with self._get_connection() as conn:
            # Disponible = Rol Courier + Jornada Activa
            cursor = conn.execute("""
                SELECT u.* FROM Usuario u
                JOIN Jornada j ON u.id = j.id_mensajero
                WHERE u.rol = 'COURIER' AND j.estado = 'ACTIVA'
            """)
            return [dict(row) for row in cursor.fetchall()]

    def can_take_more(self, courier_id: int, limit: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM Paquete WHERE id_mensajero = ? AND estado IN ('ASIGNADO', 'EN_REPARTO')",
                (courier_id,)
            )
            row = cursor.fetchone()
            return row["count"] < limit

    def get(self, courier_id: int) -> dict | None:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM Usuario WHERE id = ? AND rol = 'COURIER'", (courier_id,))
            row = cursor.fetchone()
            return dict(row) if row else None


class RatingRepo(BaseSQLiteRepo):
    def create_delivery_rating(self, shipment_id: int, customer_id: int, courier_id: int, score: int, comment: str | None):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO Valoracion (id_paquete, id_autor, puntuacion, comentario) VALUES (?, ?, ?, ?)",
                (shipment_id, customer_id, score, comment)
            )

    def recalc_courier_avg(self, courier_id: int) -> None:
        # No persistimos el promedio en Usuario por ahora, se calcula al vuelo
        pass

    def has_rating_for_shipment(self, shipment_id: int, customer_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id FROM Valoracion WHERE id_paquete = ? AND id_autor = ?",
                (shipment_id, customer_id)
            )
            return cursor.fetchone() is not None

    def average_by_courier(self, courier_id: int) -> float | None:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT AVG(v.puntuacion) as avg_score 
                FROM Valoracion v
                JOIN Paquete p ON v.id_paquete = p.id
                WHERE p.id_mensajero = ?
            """, (courier_id,))
            row = cursor.fetchone()
            val = row["avg_score"]
            return val if val else None

    def has_rating_for_workday(self, workday_id: int, customer_id: int) -> bool:
        # Sin soporte en BD aun para valorar jornadas directamente
        return False

    def create_workday_rating(self, workday_id: int, customer_id: int, courier_id: int, score: int, comment: str | None, created_at=None) -> dict:
        return {"id": 0, "status": "not_implemented_in_db"}


class IncidentRepo(BaseSQLiteRepo):
    def create_incident(self, shipment_id: int, reported_id: int, description: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO Incidencia (id_paquete, id_usuario, titulo, descripcion, tipo) VALUES (?, ?, ?, ?, ?)",
                (shipment_id, reported_id, "Incidencia", description, "GENERIC")
            )

class HelpRepo:
    def load_help_content(self) -> str:
        return "Contactar soporte..."

class WorkdayRepo(BaseSQLiteRepo):
    def get_active_workday(self, courier_id: int) -> dict | None:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM Jornada WHERE id_mensajero = ? AND estado = 'ACTIVA'",
                (courier_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_workday(self, courier_id: int, start_ts) -> dict:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO Jornada (id_mensajero, fecha_inicio, estado) VALUES (?, ?, 'ACTIVA')",
                (courier_id, start_ts)
            )
            return {"id": cursor.lastrowid, "id_mensajero": courier_id, "fecha_inicio": start_ts}

    def close_workday(self, workday_id: int, end_ts) -> dict:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE Jornada SET fecha_fin = ?, estado = 'FINALIZADA' WHERE id = ?",
                (end_ts, workday_id)
            )
            return {"id": workday_id, "fecha_fin": end_ts}

    def get_by_id(self, workday_id: int) -> dict | None:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM Jornada WHERE id = ?", (workday_id,))
            row = cursor.fetchone()
            return dict(row) if row else None