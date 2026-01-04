from datetime import timedelta
from moval.usecases.errors import ValidationError, PermissionError, NotFoundError
from moval.domain.enums import ShipmentStatus

class CalculateETA:
    """
    Calcula el Tiempo Estimado de Llegada (ETA) de un paquete.
    Utiliza heurísticas simples basadas en el peso y el estado actual.
    """
    def __init__(self, shipment_repo, clock=None):
        self.shipment_repo = shipment_repo
        self.clock = clock

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if not shipment_id:
            raise ValidationError("ID del paquete requerido")

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Paquete no encontrado")

        role = actor["role"]
        actor_id = actor["id"]

        # Verificación de permisos
        if role == "ADMIN":
            pass
        elif role == "COURIER":
            if shipment.get("id_mensajero") != actor_id:
                raise PermissionError("Este paquete no está asignado a usted")
        elif role == "CUSTOMER":
            if shipment.get("id_cliente") != actor_id:
                raise PermissionError("Este paquete no le pertenece")
        else:
            raise PermissionError("Rol no autorizado para calcular ETA")

        # Caso especial: ya entregado
        if shipment.get("estado") == ShipmentStatus.DELIVERED.value:
            return {
                "id_paquete": shipment_id,
                "estado": ShipmentStatus.DELIVERED.value,
                "eta_minutos": 0,
                "fecha_estimada": shipment.get("fecha_entrega_real")
            }

        # Cálculo de ETA simulado (Regla de negocio simple)
        # Base: 60 minutos
        base_eta = 60

        # Ajuste por peso: +5 minutos por cada kg
        peso = shipment.get("peso", 0)
        if peso:
            base_eta += int(peso * 5)

        # Ajuste por estado
        estado = shipment.get("estado")
        if estado == ShipmentStatus.EN_ROUTE.value:
            # Si ya está en reparto, reducimos a la mitad
            base_eta = max(15, base_eta // 2)
        elif estado == ShipmentStatus.PENDING.value:
            # Si aún no está asignado, sumamos tiempo de gestión
            base_eta += 120

        estimated_arrival_ts = None
        if self.clock:
            estimated_arrival_ts = self.clock.now_utc() + timedelta(minutes=base_eta)

        return {
            "id_paquete": shipment_id,
            "estado": estado,
            "eta_minutos": base_eta,
            "fecha_estimada": estimated_arrival_ts
        }
