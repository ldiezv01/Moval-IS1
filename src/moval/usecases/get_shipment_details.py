from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class GetShipmentDetails:
    """
    Obtiene los detalles de un paquete específico, aplicando reglas de privacidad
    según el rol del solicitante.
    """

    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, shipment_id: int) -> dict:
        """
        Recupera un paquete por ID.

        Args:
            actor (dict): Usuario solicitante.
            shipment_id (int): ID del paquete.

        Returns:
            dict: Datos del paquete.

        Raises:
            ValidationError: Datos incompletos.
            NotFoundError: Paquete no existe.
            PermissionError: Acceso denegado al paquete.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if not shipment_id:
            raise ValidationError("ID de paquete requerido")

        actor_id = actor["id"]
        role = actor["role"]

        shipment = self.shipment_repo.get(shipment_id)
        if not shipment:
            raise NotFoundError("Paquete no encontrado")

        if role == "ADMIN":
            return shipment

        elif role == "COURIER":
            # Verificar asignación (campo BD: id_mensajero)
            if shipment.get("id_mensajero") != actor_id:
                raise PermissionError("Este paquete no está asignado a su ruta")
            return shipment

        elif role == "CUSTOMER":
            # Verificar propiedad (campo BD: id_cliente)
            if shipment.get("id_cliente") != actor_id:
                raise PermissionError("Este paquete no le pertenece")
            return shipment

        else:
            raise PermissionError("Rol no autorizado para ver detalles")
