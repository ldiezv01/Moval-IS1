from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class CalculateWorkdayDuration:
    DEFAULT_MIN_PER_SHIPMENT = 12
    DEFAULT_BASE_MIN = 10

    def __init__(self, shipment_repo, workday_repo=None, clock=None):
        self.shipment_repo = shipment_repo
        self.workday_repo = workday_repo
        self.clock = clock

    def execute(self, actor: dict, courier_id: int | None = None) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is invalid")

        if actor["role"] == "COURIER":
            courier_id = actor["id"]
        elif actor["role"] == "ADMIN":
            if courier_id is None:
                raise ValidationError("courier_id es obligatorio para ADMIN")
        else:
            raise PermissionError("Rol no autorizado para esta operación")

        if self.workday_repo:
            active_workday = self.workday_repo.get_active_workday(courier_id)
            if not active_workday:
                raise NotFoundError("No hay jornada activa para este courier")

        filters = {"status": "PENDING"}
        shipments = self.shipment_repo.list_by_courier(courier_id, filters)
        shipment_count = len(shipments)

        if shipment_count == 0:
            return {
                "courier_id": courier_id,
                "shipment_count": 0,
                "eta_minutes": 0,
                "eta_reason": "No hay envíos pendientes"
            }

        eta_minutes = (                                             #  ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠ ⚠
            shipment_count * self.DEFAULT_MIN_PER_SHIPMENT
            + self.DEFAULT_BASE_MIN
        )

        result = {
            "courier_id": courier_id,
            "shipment_count": shipment_count,
            "eta_minutes": eta_minutes,
            "eta_reason": "Cálculo basado en envíos pendientes"
        }

        if self.clock:
            result["calculated_at"] = self.clock.now().isoformat()

        return result

    

