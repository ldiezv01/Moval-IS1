from moval.usecases.errors import ValidationError, PermissionError, ConflictError, NotFoundError

class RateDelivery:
    def __init__(self, shipment_repo, rating_repo, courier_repo=None):
        self.shipment_repo = shipment_repo
        self.rating_repo = rating_repo
        self.courier_repo = courier_repo  # optional: for recalculating averages

    def execute(self, actor: dict, shipment_id: int, score: int, comment: str | None = None) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor["role"] != "CUSTOMER":
            raise PermissionError("Only customers can rate deliveries")
        
        if not isinstance(score, int) or score < 1 or score > 5:
            raise ValidationError("Score must be an integer between 1 and 5")   
        
        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found")

        if shipment["status"] != "DELIVERED":
            raise ConflictError("Only delivered shipments can be rated")

        if shipment["customer_id"] != actor["id"]:
            raise PermissionError("Shipment does not belong to customer")

        if self.rating_repo.has_rating_for_shipment(shipment_id, actor["id"]):
            raise ConflictError("Customer has already rated this shipment")

        self.rating_repo.create_delivery_rating(
            shipment_id=shipment_id,
            customer_id=actor["id"],
            courier_id=shipment["courier_id"],
            score=score,
            comment=comment
        )

        if self.courier_repo:
            self.courier_repo.recalc_courier_avg(shipment["courier_id"])

        return {"message": "Delivery rated successfully"}