import psycopg2
import psycopg2.extras
import os
from typing import Optional, List, Union
from moval.domain.enums import Role, ShipmentStatus
from datetime import datetime

# Clase base para manejar la conexión a PostgreSQL
class BasePostgresRepo:
    def __init__(self, conn_info: dict = None):
        if conn_info is None:
            self.conn_info = {
                "host": "localhost",
                "database": "moval",
                "user": "postgres",
                "password": "1235",
                "port": "5432"
            }
        else:
            self.conn_info = conn_info

    def _get_connection(self):
        conn = psycopg2.connect(**self.conn_info)
        return conn

class UserRepo(BasePostgresRepo):
    def get_by_email(self, email: str):
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "SELECT id, dni, nombre, apellidos, email, password_hash, rol as role, activo as is_active FROM Usuario WHERE email = %s", 
                    (email,)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None

    def get(self, user_id: int):
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "SELECT id, dni, nombre, apellidos, email, password_hash, telefono, rol as role, activo as is_active FROM Usuario WHERE id = %s", 
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None

    def exists_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None
    
    def update(self, user_id: int, fields: dict) -> None:
        if not fields: return
        query = "UPDATE Usuario SET " + ", ".join([f"{k} = %s" for k in fields.keys()]) + " WHERE id = %s"
        params = list(fields.values()) + [user_id]
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
            conn.commit()
    
    def create(self, user_data: dict) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Usuario (dni, nombre, apellidos, email, password_hash, rol) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                    (
                        user_data.get("dni", ""),
                        user_data.get("nombre", ""),
                        user_data.get("apellidos", ""),
                        user_data.get("email"),
                        user_data.get("password_hash"),
                        user_data.get("role")
                    )
                )
                new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id

    def list_by_role(self, role: str) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "SELECT id, dni, nombre, apellidos, email, rol as role FROM Usuario WHERE rol = %s",
                    (role,)
                )
                return [dict(row) for row in cursor.fetchall()]
        
    def delete(self, user_id: int) -> bool:
        if not user_id:
            raise ValueError("user_id required")

        with self._get_connection() as conn:
            try:
                with conn.cursor() as cur:
                    # 1) Borrar paquetes relacionados
                    cur.execute(
                        "DELETE FROM Paquete WHERE id_cliente = %s OR id_mensajero = %s",
                        (user_id, user_id)
                    )
                    # 2) Borrar el usuario
                    cur.execute("DELETE FROM Usuario WHERE id = %s", (user_id,))
                    deleted = cur.rowcount
                conn.commit()
                return deleted > 0
            except Exception:
                conn.rollback()
                raise

class SessionRepo:
    def create_session(self, user_id: int) -> str:
        return f"session_{user_id}_{int(datetime.now().timestamp())}"

class ShipmentRepo(BasePostgresRepo):
    def list_pending(self) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM Paquete WHERE estado = 'REGISTRADO'")
                return [dict(row) for row in cursor.fetchall()]

    def get(self, shipment_id: int) -> dict | None:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM Paquete WHERE id = %s", (shipment_id,))
                row = cursor.fetchone()
                return dict(row) if row else None

    def assign(self, shipment_id: list[int], courier_id: int) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for sid in shipment_id:
                    cursor.execute(
                        "UPDATE Paquete SET id_mensajero = %s, estado = 'ASIGNADO', ultima_incidencia = NULL, fecha_incidencia = NULL WHERE id = %s",
                        (courier_id, sid)
                    )
            conn.commit()

    def unassign(self, shipment_id: int) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE Paquete SET id_mensajero = NULL, estado = 'REGISTRADO' WHERE id = %s",
                    (shipment_id,)
                )
            conn.commit()

    def update(self, shipment_id: int, fields: dict) -> None:
        if not fields: return
        query = "UPDATE Paquete SET " + ", ".join([f"{k} = %s" for k in fields.keys()]) + " WHERE id = %s"
        params = list(fields.values()) + [shipment_id]
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
            conn.commit()

    def set_status(self, shipment_id: int, status: ShipmentStatus, delivered_at: datetime | None = None) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                if delivered_at:
                    cursor.execute(
                        "UPDATE Paquete SET estado = %s, fecha_entrega_real = %s WHERE id = %s",
                        (status.value, delivered_at, shipment_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE Paquete SET estado = %s WHERE id = %s",
                        (status.value, shipment_id)
                    )
            conn.commit()

    def create(self, shipment_data: dict) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Paquete (
                        codigo_seguimiento, descripcion, peso, direccion_origen, direccion_destino, 
                        latitud, longitud, id_cliente, id_mensajero, estado, fecha_entrega_real
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, 'REGISTRADO', NULL) RETURNING id
                    """,
                    (
                        shipment_data['codigo_seguimiento'],
                        shipment_data['descripcion'],
                        shipment_data['peso'],
                        shipment_data['direccion_origen'],
                        shipment_data['direccion_destino'],
                        shipment_data['latitud'],
                        shipment_data['longitud'],
                        shipment_data['id_cliente']
                    )
                )
                new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id

    def create_copy(self, original_shipment: dict) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                new_code = f"{original_shipment['codigo_seguimiento']}-R"
                cursor.execute(
                    """
                    INSERT INTO Paquete (
                        codigo_seguimiento, descripcion, peso, direccion_origen, direccion_destino, 
                        latitud, longitud, id_cliente, id_mensajero, estado, fecha_entrega_real
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, 'REGISTRADO', NULL) RETURNING id
                    """,
                    (
                        new_code,
                        original_shipment['descripcion'],
                        original_shipment['peso'],
                        original_shipment['direccion_origen'],
                        original_shipment['direccion_destino'],
                        original_shipment['latitud'],
                        original_shipment['longitud'],
                        original_shipment['id_cliente']
                    )
                )
                new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id

    def list_all(self, filters: dict | None = None) -> List[dict]:
        query = """
            SELECT p.*, u.nombre || ' ' || u.apellidos as cliente_nombre 
            FROM Paquete p
            JOIN Usuario u ON p.id_cliente = u.id
        """
        params = []
        if filters:
            conditions = [f"p.{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(filters.values())
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(query, params)
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
    
    def find_next_delivered_unnotified_for_customer(self, customer_id):
        pass

    def get_customer_notifications(self, customer_id: int) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM Paquete 
                    WHERE id_cliente = %s 
                      AND estado = 'ENTREGADO'
                    ORDER BY fecha_entrega_real DESC
                    LIMIT 20
                """, (customer_id,))
                return [dict(row) for row in cursor.fetchall()]

    def mark_notifications_as_read(self, customer_id: int):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Paquete 
                    SET notificado_cliente = 1 
                    WHERE id_cliente = %s AND estado = 'ENTREGADO' AND (notificado_cliente IS NULL OR notificado_cliente = 0)
                """, (customer_id,))
            conn.commit()

class CourierRepo(BasePostgresRepo):
    def list_available(self) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT u.* FROM Usuario u
                    JOIN Jornada j ON u.id = j.id_mensajero
                    WHERE u.rol = 'COURIER' AND j.estado = 'ACTIVA'
                """)
                return [dict(row) for row in cursor.fetchall()]

    def list_all_couriers(self) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM Usuario WHERE rol = 'COURIER'")
                return [dict(row) for row in cursor.fetchall()]

    def can_take_more(self, courier_id: int, limit: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Paquete WHERE id_mensajero = %s AND estado IN ('ASIGNADO', 'EN_REPARTO')",
                    (courier_id,)
                )
                row = cursor.fetchone()
                return row["count"] < limit

    def get(self, courier_id: int) -> dict | None:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM Usuario WHERE id = %s AND rol = 'COURIER'", (courier_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                
                courier = dict(row)
                cursor.execute(
                    "SELECT id FROM Jornada WHERE id_mensajero = %s AND estado = 'ACTIVA'", 
                    (courier_id,)
                )
                courier["status"] = "AVAILABLE" if cursor.fetchone() else "UNAVAILABLE"
                return courier

    def list_all_with_workday_info(self) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                query = """
                    SELECT 
                        u.id, u.nombre, u.apellidos, u.email,
                        j.fecha_inicio,
                        j.fecha_fin,
                        j.estado as estado_jornada,
                        (SELECT AVG(puntuacion) FROM Valoracion v 
                        JOIN Paquete p ON v.id_paquete = p.id 
                        WHERE p.id_mensajero = u.id) as media
                    FROM Usuario u
                    LEFT JOIN (
                        SELECT id, id_mensajero, fecha_inicio, fecha_fin, estado
                        FROM Jornada j1
                        WHERE id = (SELECT MAX(id) FROM Jornada j2 WHERE j2.id_mensajero = j1.id_mensajero)
                    ) j ON u.id = j.id_mensajero
                    WHERE u.rol = 'COURIER'
                """
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]


class RatingRepo(BasePostgresRepo):
    def create_delivery_rating(self, shipment_id: int, customer_id: int, courier_id: int, score: int, comment: str | None):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Valoracion (id_paquete, id_autor, puntuacion, comentario) VALUES (%s, %s, %s, %s)",
                    (shipment_id, customer_id, score, comment)
                )
            conn.commit()

    def recalc_courier_avg(self, courier_id: int) -> None:
        pass

    def has_rating_for_shipment(self, shipment_id: int, customer_id: int) -> bool:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM Valoracion WHERE id_paquete = %s AND id_autor = %s",
                    (shipment_id, customer_id)
                )
                return cursor.fetchone() is not None

    def average_by_courier(self, courier_id: int) -> float | None:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT AVG(v.puntuacion) as avg_score 
                    FROM Valoracion v
                    JOIN Paquete p ON v.id_paquete = p.id
                    WHERE p.id_mensajero = %s
                """, (courier_id,))
                row = cursor.fetchone()
                val = row["avg_score"]
                return float(val) if val else None

    def has_rating_for_workday(self, workday_id: int, customer_id: int) -> bool:
        return False

    def create_workday_rating(self, workday_id: int, customer_id: int, courier_id: int, score: int, comment: str | None, created_at=None) -> dict:
        return {"id": 0, "status": "not_implemented_in_db"}

    def list_all(self) -> List[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        v.id, 
                        v.puntuacion, 
                        v.comentario, 
                        v.fecha,
                        u_autor.nombre || ' ' || u_autor.apellidos as autor,
                        u_mensajero.nombre || ' ' || u_mensajero.apellidos as mensajero
                    FROM Valoracion v
                    JOIN Usuario u_autor ON v.id_autor = u_autor.id
                    JOIN Paquete p ON v.id_paquete = p.id
                    LEFT JOIN Usuario u_mensajero ON p.id_mensajero = u_mensajero.id
                    ORDER BY v.fecha DESC
                """)
                return [dict(row) for row in cursor.fetchall()]


class IncidentRepo(BasePostgresRepo):
    def create_incident(self, shipment_id: int, reported_id: int, description: str):
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Incidencia (id_paquete, id_usuario, titulo, descripcion, tipo) VALUES (%s, %s, %s, %s, %s)",
                    (shipment_id, reported_id, "Incidencia", description, "GENERIC")
                )
            conn.commit()

    def get_latest_by_shipment(self, shipment_id: int) -> dict | None:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM Incidencia WHERE id_paquete = %s ORDER BY fecha_reporte DESC LIMIT 1",
                    (shipment_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None

class HelpRepo:
    def load_help_content(self) -> str:
        return "Contactar soporte..."

class WorkdayRepo(BasePostgresRepo):
    def get_active_workday(self, courier_id: int) -> dict | None:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM Jornada WHERE id_mensajero = %s AND estado = 'ACTIVA'",
                    (courier_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None

    def create_workday(self, courier_id: int, start_ts) -> dict:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Jornada (id_mensajero, fecha_inicio, estado) VALUES (%s, %s, 'ACTIVA') RETURNING id",
                    (courier_id, start_ts)
                )
                new_id = cursor.fetchone()[0]
            conn.commit()
            return {"id": new_id, "id_mensajero": courier_id, "fecha_inicio": start_ts}

    def close_workday(self, workday_id: int, end_ts) -> dict:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE Jornada SET fecha_fin = %s, estado = 'FINALIZADA' WHERE id = %s",
                    (end_ts, workday_id)
                )
            conn.commit()
            return {"id": workday_id, "fecha_fin": end_ts}

    def get_by_id(self, workday_id: int) -> dict | None:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM Jornada WHERE id = %s", (workday_id,))
                row = cursor.fetchone()
                return dict(row) if row else None