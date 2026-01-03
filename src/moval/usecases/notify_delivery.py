from moval.usecases.errors import ValidationError, PermissionError,NotFoundError,ConflictError

class NotifyDelivery:
    def __init__(self, shipment_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.clock = clock 

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if not shipment_id:
            raise ValidationError("Shipment ID is required")

        role = actor["role"]
        actor_id = actor["id"]

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError(f"Shipment {shipment_id} not found")

        if shipment.get("status") != "DELIVERED":
            raise ConflictError(f"Shipment {shipment_id} is not delivered")

        if shipment.get("delivery_notified") is True:
            raise ConflictError("Delivery already notified")

        if role == "ADMIN":
            pass
        elif role == "COURIER":
            if shipment.get("courier_id") != actor_id:
                raise PermissionError(
                    "Courier can only notify their own shipments"
                )
        else:
            raise PermissionError(
                "Only ADMIN or assigned COURIER can notify delivery"
            )

        update_fields = {"delivery_notified": True}
        if self.clock:
            update_fields["notified_at"] = self.clock.now_utc()

        self.shipment_repo.update(shipment_id, update_fields)

        updated = self.shipment_repo.get(shipment_id)
        return updated if updated else {**shipment, **update_fields}
