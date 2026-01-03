from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError

class RateDelivery:
    def __init__(self, shipment_repo, rating_repo):
        self.shipment_repo = shipment_repo
        self.rating_repo = rating_repo

    def execute(self, actor: dict, shipment_id: int, score: int, comment: str | None = None) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor["role"] != "CUSTOMER":
            raise PermissionError("Only customers can rate deliveries")

        customer_id = actor["id"]

        if not shipment_id:
            raise ValidationError("shipment_id is required")
        if not isinstance(score, int) or score < 1 or score > 5:
            raise ValidationError("Score must be an integer between 1 and 5")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found")

        if shipment.get("status") != "DELIVERED":
            raise ConflictError("Only delivered shipments can be rated")

        if shipment.get("customer_id") != customer_id:
            raise PermissionError("You can only rate your own shipments")

        if self.rating_repo.has_rating_for_shipment(shipment_id, customer_id):
            raise ConflictError("You have already rated this shipment")

        courier_id = shipment.get("courier_id")

        rating_info = self.rating_repo.create_delivery_rating(
            shipment_id=shipment_id,
            customer_id=customer_id,
            courier_id=courier_id,
            score=score,
            comment=comment
        )

        if courier_id is not None:
            self.rating_repo.recalc_courier_avg(courier_id)

        return rating_info
