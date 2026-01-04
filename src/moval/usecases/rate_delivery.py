from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class RateDelivery:
    """
    Permite al cliente valorar el servicio de entrega de un paquete.
    """
    def __init__(self, shipment_repo, rating_repo):
        self.shipment_repo = shipment_repo
        self.rating_repo = rating_repo

    def execute(self, actor: dict, shipment_id: int, score: int, comment: str | None = None) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario no válidos")

        if actor["role"] != "CUSTOMER":
            raise PermissionError("Solo los clientes pueden valorar las entregas")

        customer_id = actor["id"]

        if not shipment_id:
            raise ValidationError("El ID del paquete es obligatorio")
        
        if not isinstance(score, int) or score < 1 or score > 5:
            raise ValidationError("La puntuación debe ser un número entero entre 1 y 5")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("No se encontró el paquete")

        # Campo BD: estado
        if shipment.get("estado") != ShipmentStatus.DELIVERED.value:
            raise ConflictError("Solo se pueden valorar paquetes que hayan sido entregados")

        # Campo BD: id_cliente
        if shipment.get("id_cliente") != customer_id:
            raise PermissionError("Solo puede valorar sus propios paquetes")

        if self.rating_repo.has_rating_for_shipment(shipment_id, customer_id):
            raise ConflictError("Ya ha valorado esta entrega anteriormente")

        # Campo BD: id_mensajero
        courier_id = shipment.get("id_mensajero")

        rating_info = self.rating_repo.create_delivery_rating(
            shipment_id=shipment_id,
            customer_id=customer_id,
            courier_id=courier_id,
            score=score,
            comment=comment
        )

        # Si hay mensajero, podríamos recalcular su promedio (opcional según implementación de repo)
        if courier_id is not None:
            self.rating_repo.recalc_courier_avg(courier_id)

        return {"status": "success", "message": "Valoración registrada correctamente"}
