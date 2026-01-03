from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class GetShipmentDetails:
    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if not shipment_id:
            raise ValidationError("Shipment ID is required")

        actor_id = actor["id"]
        role = actor["role"]

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found")

        if role == "ADMIN":
            return shipment

        elif role == "COURIER":
            if shipment.get("courier_id") != actor_id:
                raise PermissionError("Shipment not assigned to this courier")
            return shipment

        elif role in ["CUSTOMER", "USER"]:
            if shipment.get("customer_id") != actor_id:
                raise PermissionError("Shipment does not belong to this customer")
            return shipment

        else:
            raise PermissionError("Invalid role for viewing shipment details")
