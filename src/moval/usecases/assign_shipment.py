from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class AssignShipments:
    """
    Gestiona la asignación masiva de paquetes a mensajeros por parte de un administrador.
    """

    def __init__(self, shipment_repo, courier_repo):
        self.shipment_repo = shipment_repo
        self.courier_repo = courier_repo

    def execute(self, actor: dict, shipment_ids: list[int], courier_id: int) -> dict:
        """
        Asigna una lista de paquetes a un mensajero específico.

        Args:
            actor (dict): Usuario que realiza la acción (debe ser ADMIN).
            shipment_ids (list): IDs de los paquetes a asignar.
            courier_id (int): ID del mensajero.

        Returns:
            dict: Lista de paquetes actualizados.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Se requiere autenticación")

        if actor["role"] != "ADMIN":
            raise PermissionError("Solo un administrador puede asignar paquetes")

        if not shipment_ids or not isinstance(shipment_ids, list):
            raise ValidationError("Debe proporcionar al menos un ID de paquete")

        if not courier_id:
            raise ValidationError("Debe proporcionar el ID del mensajero")

        # Verificar existencia del mensajero
        courier = self.courier_repo.get(courier_id)
        if not courier:
            raise NotFoundError(f"Mensajero {courier_id} no encontrado")

        # Removed availability check to allow assignment even if courier is not active

        shipments = []
        for shipment_id in shipment_ids:
            shipment = self.shipment_repo.get(shipment_id)
            if not shipment:
                raise NotFoundError(f"Paquete {shipment_id} no encontrado")

            # Se pueden asignar paquetes REGISTRADOS o en INCIDENCIA
            if shipment["estado"] not in [ShipmentStatus.PENDING.value, ShipmentStatus.INCIDENT.value]:
                raise ConflictError(f"El paquete {shipment_id} no está disponible para asignación (Estado: {shipment['estado']})")

            # Resetear incidencias previas al reasignar
            if shipment["estado"] == ShipmentStatus.INCIDENT.value:
                shipment["ultima_incidencia"] = None
                shipment["fecha_incidencia"] = None

            shipments.append(shipment)

        # Extraer IDs validados
        valid_ids = [s["id"] for s in shipments]

        # Realizar la asignación en lote usando el método específico del repositorio
        self.shipment_repo.assign(shipment_id=valid_ids, courier_id=courier_id)

        # Actualizar los objetos en memoria para el retorno
        for shipment in shipments:
            shipment["estado"] = ShipmentStatus.ASSIGNED.value
            shipment["id_mensajero"] = courier_id

        return {"assigned_shipments": shipments}
