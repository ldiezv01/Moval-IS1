from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError

class DeliverShipment:
    def __init__(self, shipment_repo, clock):
        self.shipment_repo = shipment_repo
        self.clock = clock

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if not shipment_id:
            raise ValidationError("Shipment ID is required")

        if actor["role"] != "COURIER":
            raise PermissionError("Only couriers can deliver shipments")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found")

        if shipment["courier_id"] != actor["id"]:
            raise PermissionError(
                "Couriers can deliver shipments only for their assigned shipments"
            )

        if shipment["status"] == "DELIVERED":
            raise ConflictError("Shipment already delivered")

        timestamp = self.clock.now_utc()

        updated_shipment = self.shipment_repo.set_status(
            shipment_id=shipment_id,
            status="DELIVERED",
            delivered_at=timestamp
        )

        return updated_shipment
