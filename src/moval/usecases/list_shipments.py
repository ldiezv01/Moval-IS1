from moval.usecases.errors import ValidationError, PermissionError

class ListShipments:
    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, filters: dict | None = None) -> list[dict]:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        filters = filters or {}

        role = actor["role"]
        actor_id = actor["id"]

        if role == "ADMIN":
            shipments = self.shipment_repo.list_all(filters)
        elif role == "COURIER":
            shipments = self.shipment_repo.listby_courier(actor_id, filters)
        elif role == "CUSTOMER":
            shipments = self.shipment_repo.list_by_customer(actor_id, filters)
        else:
            raise PermissionError("Invalid role for listing shipments")

        return shipments