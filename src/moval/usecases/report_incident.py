from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class ReportIncident:
    def __init__(self, shipment_repo, incident_repo, clock):
        self.shipment_repo = shipment_repo
        self.incident_repo = incident_repo
        self.clock = clock

    def execute(self, actor: dict, shipment_id: int, description: str) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if not shipment_id or not description or not description.strip():
            raise ValidationError("Shipment ID and description are required")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found")

        if actor["role"] == "CUSTOMER":
            if shipment["customer_id"] != actor["id"]:
                raise PermissionError("Customers can report incidents only for their own shipments")
        elif actor["role"] == "COURIER":
            if shipment["courier_id"] != actor["id"]:
                raise PermissionError("Couriers can report incidents only for their assigned shipments")
        elif actor["role"] != "ADMIN":
            raise PermissionError("Invalid role")

        timestamp = self.clock.now_utc()

        incident = self.incident_repo.create_incident(
            shipment_id=shipment_id,
            reported_id=actor["id"],
            description=description.strip(),
            created_at=timestamp
        )

        return incident
