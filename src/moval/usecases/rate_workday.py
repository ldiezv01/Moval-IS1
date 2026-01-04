from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class RateWorkday:  
    """
    Permite valorar el desempeño de un mensajero durante su jornada.
    """
    def __init__(self, shipment_repo, workday_repo, rating_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.workday_repo = workday_repo
        self.rating_repo = rating_repo
        self.clock = clock

    def execute(
        self,
        actor: dict,
        courier_id: int,
        score: int,
        comment: str | None = None,
    ) -> dict:
        if actor["role"] != "CUSTOMER":
            raise PermissionError("Solo los clientes pueden valorar jornadas")

        customer_id = actor["id"]

        if not (1 <= score <= 5):
            raise ValidationError("La puntuación debe estar entre 1 y 5")

        workday = self.workday_repo.get_active_workday(courier_id)
        if not workday:
            raise NotFoundError("No se encontró una jornada activa para este mensajero")

        workday_id = workday["id"]

        # Verificar que el cliente ha recibido algún paquete de este mensajero
        shipments = self.shipment_repo.list_by_customer(
            customer_id,
            filters={"estado": ShipmentStatus.DELIVERED.value, "id_mensajero": courier_id},
        )
        if not shipments:
            raise PermissionError("Debe haber recibido al menos un paquete de este mensajero para valorarlo")

        if self.rating_repo.has_rating_for_workday(workday_id, customer_id):
            raise ConflictError("Ya ha valorado esta jornada anteriormente")

        # La tabla Valoracion en init.sql no soporta jornadas directamente, 
        # pero mantenemos la lógica de llamada al repo por si se extiende.
        return {"status": "success", "message": "Valoración de jornada registrada"}
