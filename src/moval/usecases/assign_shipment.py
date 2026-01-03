from moval.usecases.errors import ValidationError, PermissionError, NotFoundError, ConflictError

class AssignShipments:
    def __init__(self, shipment_repo, courier_repo):
        self.shipment_repo = shipment_repo
        self.courier_repo = courier_repo

    def execute(self, actor: dict, shipment_ids: list[int], courier_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor must be authenticated")

        if actor["role"] != "ADMIN":
            raise PermissionError("Only ADMIN can assign shipments")

        if not shipment_ids or not isinstance(shipment_ids, list):
            raise ValidationError("At least one shipment_id must be provided")

        if not courier_id:
            raise ValidationError("courier_id must be provided")

        courier = self.courier_repo.get_by_id(courier_id)
        if not courier:
            raise NotFoundError(f"Courier with id {courier_id} not found")

        if courier["status"] != "AVAILABLE":
            raise ConflictError(f"Courier with id {courier_id} is not available")

        shipments = []
        for shipment_id in shipment_ids:
            shipment = self.shipment_repo.get(shipment_id)
            if not shipment:
                raise NotFoundError(f"Shipment with id {shipment_id} not found")

            if shipment["status"] != "PENDING":
                raise ConflictError(f"Shipment with id {shipment_id} is not PENDING")

            shipments.append(shipment)

        assigned_shipments = []
        for shipment in shipments:
            updated = self.shipment_repo.set_status(
                shipment_id=shipment["id"],
                status="ASSIGNED",
                courier_id=courier_id
            )
            assigned_shipments.append(updated)

        return {"assigned_shipments": assigned_shipments}
