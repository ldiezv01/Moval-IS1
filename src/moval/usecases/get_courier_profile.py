from moval.usecases.errors import ValidationError, PermissionError, NotFoundError
from moval.domain.enums import ShipmentStatus

class GetCourierProfile:
    """
    Obtiene el perfil público de un mensajero, incluyendo su calificación media
    y el total de entregas realizadas.
    """
    def __init__(self, courier_repo, rating_repo=None, shipment_repo=None):
        self.courier_repo = courier_repo
        self.rating_repo = rating_repo
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, courier_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if courier_id is None:
            raise ValidationError("ID del mensajero requerido")

        # Admin puede ver cualquier perfil. El cliente solo si ha recibido algo de él.
        if actor["role"] not in ["ADMIN", "CUSTOMER"]:
            raise PermissionError("No tiene permiso para ver perfiles de mensajeros")

        courier = self.courier_repo.get(courier_id)
        if not courier:
            raise NotFoundError("Mensajero no encontrado")

        if actor["role"] == "CUSTOMER":
            if not self.shipment_repo:
                raise ValidationError("Repositorio de envíos no disponible")

            # Verificar que el cliente ha tenido relación con este mensajero
            delivered = self.shipment_repo.list_by_customer(
                customer_id=actor["id"],
                filters={"id_mensajero": courier_id, "estado": ShipmentStatus.DELIVERED.value}
            )
            if not delivered:
                raise PermissionError("Solo puede ver perfiles de mensajeros que le hayan entregado paquetes")

        total_deliveries = 0
        if self.shipment_repo:
            total_deliveries = self.shipment_repo.count_by_courier(
                courier_id,
                filters={"estado": ShipmentStatus.DELIVERED.value}
            )

        avg_rating = None
        if self.rating_repo:
            avg_rating = self.rating_repo.average_by_courier(courier_id)

        return {
            "id": courier.get("id"),
            "nombre": courier.get("nombre"),
            "apellidos": courier.get("apellidos"),
            "total_entregas": total_deliveries,
            "puntuacion_media": avg_rating,
        }


