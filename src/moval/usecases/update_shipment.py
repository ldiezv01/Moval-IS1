from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class UpdateShipment:
    """
    Permite actualizar la información básica de un paquete.
    """
    ALLOWED_FIELDS = {
        "descripcion",
        "peso",
        "direccion_origen",
        "direccion_destino",
    }

    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, shipment_id: int, updates: dict) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if actor["role"] != "ADMIN":
            raise PermissionError("Acceso denegado: Se requiere rol de administrador")

        if shipment_id is None:
            raise ValidationError("ID del paquete requerido")

        if not updates or not isinstance(updates, dict):
            raise ValidationError("Debe proporcionar un diccionario de cambios")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError(f"No se encontró el paquete con ID {shipment_id}")

        if shipment.get("estado") == ShipmentStatus.DELIVERED.value:
            raise ConflictError("No se pueden modificar paquetes que ya han sido entregados")

        invalid_fields = [f for f in updates.keys() if f not in self.ALLOWED_FIELDS]
        if invalid_fields:
            raise ValidationError(f"Campos no permitidos para actualización: {', '.join(invalid_fields)}")

        if "peso" in updates and updates["peso"] is not None and updates["peso"] <= 0:
            raise ValidationError("El peso debe ser mayor que cero")

        self.shipment_repo.update(shipment_id, updates)

        return self.shipment_repo.get(shipment_id)

