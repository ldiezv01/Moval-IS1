from datetime import timedelta
from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class CalculateETA:
    def __init__(self, shipment_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.clock = clock

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if not shipment_id:
            raise ValidationError("Shipment ID is required")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Shipment not found")

        role = actor["role"]
        actor_id = actor["id"]

        if role == "ADMIN":
            pass
        elif role == "COURIER":
            if shipment.get("courier_id") != actor_id:
                raise PermissionError("Shipment not assigned to this courier")
        elif role in ["CUSTOMER", "USER"]:
            if shipment.get("customer_id") != actor_id:
                raise PermissionError("Shipment does not belong to this customer")
        else:
            raise PermissionError("Invalid role for calculating ETA")

        # Caso especial: ya entregado
        if shipment.get("status") == "DELIVERED":
            return {
                "shipment_id": shipment_id,
                "status": "DELIVERED",
                "eta_minutes": 0,
                "estimated_arrival_ts": shipment.get("delivered_at")
            }

        # Cálculo ETA simple basado en prioridad, peso y distancia
        base_eta = 30  # minutos base

        if shipment.get("priority") == "HIGH":
            base_eta -= 10

        weight = shipment.get("weight_kg", 0)
        base_eta += min(int(weight), 20) // 4

        distance = shipment.get("distance_km")
        if distance:
            base_eta = max(5, int(distance * 2))

        # Timestamp estimado
        if self.clock:
            estimated_arrival_ts = self.clock.now_utc() + timedelta(minutes=base_eta)
        else:
            estimated_arrival_ts = None

        return {
            "shipment_id": shipment_id,
            "status": shipment.get("status"),
            "eta_minutes": base_eta,
            "estimated_arrival_ts": estimated_arrival_ts
        }
