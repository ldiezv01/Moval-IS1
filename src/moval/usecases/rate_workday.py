from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError


class RateWorkday:  
    def __init__(self, shipment_repo, workday_repo, rating_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.workday_repo = workday_repo
        self.rating_repo = rating_repo
        self.clock = clock

    def execute(
        self,
        actor: dict,
        courier_id: int,
        score: int,
        comment: str | None = None,
    ) -> dict:
        if actor["role"] != "CUSTOMER":
            raise PermissionError("Only CUSTOMERS can rate workdays.")

        customer_id = actor["id"]

        if not (1 <= score <= 5):
            raise ValidationError("Score must be an integer between 1 and 5.")

        workday = self.workday_repo.get_active_workday(courier_id)
        if not workday:
            raise NotFoundError("Workday not found for the specified courier.")

        workday_id = workday["id"]

        shipments = self.shipment_repo.list_by_customer(
            customer_id,
            filters={"status": "DELIVERED", "courier_id": courier_id},
        )
        if not shipments:
            raise PermissionError("Customer has no delivered shipments with this courier.")

        existing_rating = self.rating_repo.has_rating_for_workday(workday_id, customer_id)
        if existing_rating:
            raise ConflictError("Customer has already rated this workday.")

        rating_data = {
            "workday_id": workday_id,
            "customer_id": customer_id,
            "score": score,
            "comment": comment,
            "created_at": self.clock.now() if self.clock else None,
        }
        rating = self.rating_repo.create(rating_data)

        return rating
