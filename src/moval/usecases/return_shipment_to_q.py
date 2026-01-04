from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class ReturnShipmentToQueue:
    """
    Permite a un mensajero devolver un paquete a la cola de pendientes si no puede entregarlo.
    """
    def __init__(self, shipment_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.clock = clock

    def execute(self, actor: dict, shipment_id: int, reason: str | None = None) -> dict:

        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if actor["role"] != "COURIER":
            raise PermissionError("Solo los mensajeros pueden devolver paquetes a la cola")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Paquete no encontrado")

        # Campo BD: id_mensajero
        if shipment.get("id_mensajero") != actor["id"]:
            raise PermissionError("Este paquete no está asignado a usted")

        if shipment.get("estado") == ShipmentStatus.DELIVERED.value:
            raise ConflictError("El paquete ya ha sido entregado y no se puede devolver")

        # Devolver a estado pendiente y quitar el mensajero asignado
        updated_shipment = self.shipment_repo.set_status(
            shipment_id=shipment_id,
            status=ShipmentStatus.PENDING,
            courier_id=None
        )

        return updated_shipment