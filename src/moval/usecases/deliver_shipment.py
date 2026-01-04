from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class DeliverShipment:
    """
    Gestiona la entrega final de un paquete por parte de un mensajero.
    """

    def __init__(self, shipment_repo, clock):
        self.shipment_repo = shipment_repo
        self.clock = clock

    def execute(self, actor: dict, shipment_id: int) -> dict:
        """
        Marca un paquete como entregado y registra la fecha/hora actual.

        Args:
            actor (dict): Datos del usuario que realiza la entrega (debe ser el mensajero asignado).
            shipment_id (int): ID del paquete a entregar.

        Returns:
            dict: Datos del paquete actualizado.

        Raises:
            PermissionError: Si el usuario no es mensajero o el paquete no le pertenece.
            ConflictError: Si el paquete ya ha sido entregado.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos del usuario incompletos")

        if not shipment_id:
            raise ValidationError("ID de paquete obligatorio")

        if actor["role"] != "COURIER":
            raise PermissionError("Solo los mensajeros pueden realizar entregas")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Paquete no encontrado")

        # Verificación de propiedad: Un mensajero solo puede entregar sus propios paquetes
        if shipment["id_mensajero"] != actor["id"]:
            raise PermissionError("No tiene permiso para entregar un paquete que no tiene asignado")

        if shipment["estado"] == ShipmentStatus.DELIVERED.value:
            raise ConflictError("El paquete ya consta como entregado")

        timestamp = self.clock.now_utc()

        updated_shipment = self.shipment_repo.set_status(
            shipment_id=shipment_id,
            status=ShipmentStatus.DELIVERED,
            delivered_at=timestamp
        )

        return updated_shipment
