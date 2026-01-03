from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError

class UnassignShipment:
    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor["role"] != "ADMIN":
            raise PermissionError("Only ADMIN can unassign shipments")

        if shipment_id is None:
            raise ValidationError("Shipment ID is required")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError(f"Shipment with id {shipment_id} not found")

        if shipment["status"] == "DELIVERED":
            raise ConflictError(f"Shipment with id {shipment_id} is already delivered")

        if shipment["status"] != "ASSIGNED":
            raise ConflictError(f"Shipment with id {shipment_id} is not assigned")

        updated_shipment = self.shipment_repo.set_status(
            shipment_id=shipment_id,
            status="PENDING",
            courier_id=None
        )

        return {"unassigned_shipment": updated_shipment}