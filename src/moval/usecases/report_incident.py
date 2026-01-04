from moval.usecases.errors import ValidationError, PermissionError, NotFoundError
from moval.domain.enums import ShipmentStatus

class ReportIncident:
    """
    Gestiona el reporte de incidencias asociadas a un paquete.
    Permite a mensajeros y clientes reportar problemas, actualizando el estado del envío.
    """

    def __init__(self, shipment_repo, incident_repo, clock):
        self.shipment_repo = shipment_repo
        self.incident_repo = incident_repo
        self.clock = clock

    def execute(self, actor: dict, shipment_id: int, description: str) -> dict:
        """
        Crea una incidencia y marca el paquete con estado INCIDENCIA.

        Args:
            actor (dict): Usuario que reporta (Mensajero o Cliente).
            shipment_id (int): ID del paquete afectado.
            description (str): Detalle del problema.

        Returns:
            dict: Datos de la incidencia creada.

        Raises:
            ValidationError: Datos incompletos.
            NotFoundError: Paquete no encontrado.
            PermissionError: Si el usuario no tiene relación con el paquete.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if not shipment_id or not description or not description.strip():
            raise ValidationError("ID del paquete y descripción son obligatorios")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Paquete no encontrado")

        # Verificación de permisos según rol
        # BD fields: id_cliente, id_mensajero
        if actor["role"] == "CUSTOMER":
            if shipment["id_cliente"] != actor["id"]:
                raise PermissionError("Un cliente solo puede reportar incidencias en sus propios envíos")
        elif actor["role"] == "COURIER":
            if shipment["id_mensajero"] != actor["id"]:
                raise PermissionError("Un mensajero solo puede reportar incidencias en paquetes asignados")
        elif actor["role"] != "ADMIN":
            # Admin puede reportar en cualquier paquete (implícito por exclusión anterior)
            # Pero si no es ninguno de los 3, error.
            raise PermissionError("Rol no autorizado para reportar incidencias")

        timestamp = self.clock.now_utc()

        # 1. Crear el registro de incidencia
        # create_incident devuelve None o ID? El repo actual inserta pero no retorna nada explícito en el código visto.
        # Asumiremos que retorna algo o modificaremos el repo si es necesario.
        # Revisando repo: incident_repo.create_incident hace un INSERT y no retorna ID.
        # Para mantener consistencia, deberíamos actualizar el repo, pero por ahora seguimos la firma.
        self.incident_repo.create_incident(
            shipment_id=shipment_id,
            reported_id=actor["id"],
            description=description.strip()
        )

        # 2. Actualizar estado del paquete a INCIDENCIA y DESASIGNAR
        # Al desasignar, el paquete se le "quita" al mensajero
        self.shipment_repo.update(
            shipment_id=shipment_id,
            fields={
                "estado": ShipmentStatus.INCIDENT.value,
                "id_mensajero": None
            }
        )

        return {
            "status": "created",
            "shipment_id": shipment_id,
            "created_at": timestamp,
            "description": description
        }
