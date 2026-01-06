from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class PopNextDeliveryNotification:
    """
    Devuelve y marca como notificado el siguiente envío DELIVERED
    del cliente (actor.role == 'CUSTOMER'). Si no hay ninguno devuelve None.
    """
    def __init__(self, shipment_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.clock = clock

    def execute(self, actor: dict) -> dict | None:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor["role"] != "CUSTOMER":
            raise PermissionError("Only customers can pop their delivery notifications")

        customer_id = actor["id"]


        shipment = self.shipment_repo.find_next_delivered_unnotified_for_customer(customer_id)
        if not shipment:
            return None

        update_fields = {"delivery_notified": True}
        if self.clock:
            update_fields["notified_at"] = self.clock.now()

        self.shipment_repo.update(shipment["id"], update_fields)


        updated = self.shipment_repo.get(shipment["id"])
        return updated if updated else {**shipment, **update_fields}
