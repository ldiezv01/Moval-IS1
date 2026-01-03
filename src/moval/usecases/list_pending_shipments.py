from moval.usecases.errors import ValidationError, PermissionError

class ListPendingShipments:
    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict) -> list[dict]:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")
        
        if actor.get("role") != "ADMIN":
            raise PermissionError("Only ADMIN can list pending shipments")

        pending_shipments = self.shipment_repo.list_pending()
        return pending_shipments
