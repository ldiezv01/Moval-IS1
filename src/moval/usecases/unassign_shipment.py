from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class UnassignShipment:
    """
    Permite desasignar un paquete de un mensajero.
    """

    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario no válidos")

        if actor["role"] != "ADMIN":
            raise PermissionError("Acceso denegado: Se requiere rol de administrador")

        if shipment_id is None:
            raise ValidationError("El ID del paquete es obligatorio")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError(f"No se encontró el paquete con ID {shipment_id}")

        # Comprobación de estado usando la columna correcta 'estado'
        if shipment["estado"] == ShipmentStatus.DELIVERED.value:
            raise ConflictError("No se puede desasignar un paquete que ya ha sido entregado")

        if shipment["estado"] != ShipmentStatus.ASSIGNED.value:
            raise ConflictError("El paquete no está asignado a ningún mensajero")

        if shipment["estado"] not in [ShipmentStatus.ASSIGNED.value, ShipmentStatus.EN_ROUTE.value]:
            raise ConflictError(f"El paquete {shipment_id} no está actualmente asignado")

        # Usar el método específico del repositorio para desasignar
        self.shipment_repo.unassign(shipment_id)

        # Retornar estado actualizado manualmente para la respuesta
        return {"id": shipment_id, "estado": ShipmentStatus.PENDING.value, "id_mensajero": None}