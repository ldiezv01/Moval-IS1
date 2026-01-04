from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class GetShipmentDetails:
    """
    Obtiene los detalles de un paquete específico, incluyendo información de incidencias
    y cliente para el administrador.
    """

    def __init__(self, shipment_repo, incident_repo=None, user_repo=None):
        self.shipment_repo = shipment_repo
        self.incident_repo = incident_repo
        self.user_repo = user_repo

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if not shipment_id:
            raise ValidationError("ID de paquete requerido")

        actor_id = actor["id"]
        role = actor["role"]

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Paquete no encontrado")

        # Lógica de permisos básica
        if role == "COURIER" and shipment.get("id_mensajero") != actor_id:
            raise PermissionError("Este paquete no está asignado a su ruta")
        if role == "CUSTOMER" and shipment.get("id_cliente") != actor_id:
            raise PermissionError("Este paquete no le pertenece")

        # Para ADMIN (o si el solicitante tiene permiso), enriquecemos con más datos
        if role == "ADMIN":
            # 1. Obtener datos del cliente
            if self.user_repo and shipment.get("id_cliente"):
                customer = self.user_repo.get(shipment["id_cliente"])
                if customer:
                    shipment["cliente_nombre"] = f"{customer['nombre']} {customer['apellidos']}"
                    shipment["cliente_email"] = customer['email']

            # 2. Obtener última incidencia si existe
            if self.incident_repo:
                incident = self.incident_repo.get_latest_by_shipment(shipment_id)
                if incident:
                    shipment["ultima_incidencia"] = incident["descripcion"]
                    shipment["fecha_incidencia"] = incident["fecha_reporte"]

        return shipment