from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class GetCourierProfile:
    def __init__(self, courier_repo, rating_repo=None, shipment_repo=None):
        self.courier_repo = courier_repo
        self.rating_repo = rating_repo
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, courier_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if courier_id is None:
            raise ValidationError("Courier ID is required")

        if actor["role"] not in ["ADMIN", "CUSTOMER"]:
            raise PermissionError("Invalid role for viewing courier profiles")

        courier = self.courier_repo.get(courier_id)
        if not courier:
            raise NotFoundError("Courier not found")

        if actor["role"] == "CUSTOMER":
            if not self.shipment_repo:
                raise ValidationError("Shipment repository is required for CUSTOMER role")

            delivered = self.shipment_repo.list_by_customer(
                customer_id=actor["id"],
                filters={"courier_id": courier_id, "status": "DELIVERED"}
            )
            if not delivered:
                raise PermissionError("CUSTOMER cannot view this courier profile")

        total_deliveries = 0
        if self.shipment_repo:
            if hasattr(self.shipment_repo, "count_by_courier"):
                total_deliveries = self.shipment_repo.count_by_courier(
                    courier_id,
                    filters={"status": "DELIVERED"}
                )
            else:
                total_deliveries = len(
                    self.shipment_repo.list_by_courier(
                        courier_id,
                        filters={"status": "DELIVERED"}
                    )
                )

        avg_rating = None
        if self.rating_repo and hasattr(self.rating_repo, "average_by_courier"):
            avg_rating = self.rating_repo.average_by_courier(courier_id)

        return {
            "id": courier.get("id"),
            "name": courier.get("name"),
            "status": courier.get("status"),
            "total_deliveries": total_deliveries,
            "avg_rating": avg_rating,
        }

