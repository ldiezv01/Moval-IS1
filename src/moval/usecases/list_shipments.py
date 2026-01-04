from moval.usecases.errors import ValidationError, PermissionError

class ListShipments:
    """
    Gestiona el listado de paquetes según el rol del usuario.
    - ADMIN: Ve todos los paquetes.
    - COURIER: Ve solo los paquetes asignados a él.
    - CUSTOMER: Ve solo sus propios envíos.
    """

    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict, filters: dict | None = None) -> list[dict]:
        """
        Ejecuta la consulta de paquetes.

        Args:
            actor (dict): Usuario que realiza la consulta.
            filters (dict, optional): Filtros adicionales para la búsqueda.

        Returns:
            list[dict]: Lista de paquetes encontrados.

        Raises:
            ValidationError: Si faltan datos del actor.
            PermissionError: Si el rol no es válido.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        filters = filters or {}

        role = actor["role"]
        actor_id = actor["id"]

        if role == "ADMIN":
            shipments = self.shipment_repo.list_all(filters)
        elif role == "COURIER":
            # Corregido typo: listby_courier -> list_by_courier
            shipments = self.shipment_repo.list_by_courier(actor_id, filters)
        elif role == "CUSTOMER":
            shipments = self.shipment_repo.list_by_customer(actor_id, filters)
        else:
            raise PermissionError("Rol no válido para listar paquetes")

        return shipments