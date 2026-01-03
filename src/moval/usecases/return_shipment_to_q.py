from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError

class ReturnShipmentToQueue:
    def __init__(self, shipment_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.clock = clock

    def execute(self,actor: dict,shipment_id: int,reason: str | None = None) -> dict:

        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor["role"] != "COURIER":
            raise PermissionError("Only couriers can return shipments to queue")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found")

        if shipment.get("courier_id") != actor["id"]:
            raise PermissionError("Shipment not assigned to this courier")

        if shipment.get("status") == "DELIVERED":
            raise ConflictError("Shipment already delivered")

        timestamp = self.clock.now_utc() if self.clock else None

        updated_shipment = self.shipment_repo.set_status(shipment_id=shipment_id,status="PENDING",courier_id=None,return_reason=reason,returned_at=timestamp)

        return updated_shipment