from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError

class UpdateShipment:
    ALLOWED_FIELDS = {
        "description",
        "weight",
        "category",
        "length",
        "width",
        "height",
        "notes",
        "special_handling",
    }

    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, shipment_id: int, updates: dict) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor["role"] != "ADMIN":
            raise PermissionError("Only ADMIN users can update shipments")

        if shipment_id is None:
            raise ValidationError("Shipment ID is required")

        if not updates or not isinstance(updates, dict):
            raise ValidationError("Updates must be a non-empty dict")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError(f"Shipment with id {shipment_id} not found")

        if shipment.get("status") == "DELIVERED":
            raise ConflictError("Delivered shipments cannot be modified")

        invalid_fields = [f for f in updates.keys() if f not in self.ALLOWED_FIELDS]
        if invalid_fields:
            raise ValidationError(f"Invalid fields for update: {', '.join(invalid_fields)}")

        if "weight" in updates and updates["weight"] is not None and updates["weight"] <= 0:
            raise ValidationError("Weight must be > 0")

        for dim in ("length", "width", "height"):
            if dim in updates and updates[dim] is not None and updates[dim] <= 0:
                raise ValidationError(f"{dim} must be > 0")

        if "category" in updates and updates["category"] is not None and not str(updates["category"]).strip():
            raise ValidationError("Category cannot be empty")

        self.shipment_repo.update(shipment_id, updates)

        updated_shipment = self.shipment_repo.get(shipment_id)
        if not updated_shipment:
            raise NotFoundError(f"Shipment with id {shipment_id} not found after update")

        return updated_shipment

