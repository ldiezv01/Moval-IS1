from moval.usecases.errors import ValidationError, PermissionError

class ListPendingShipments:
    """
    Caso de uso para listar todos los paquetes que aún no han sido asignados (Estado: REGISTRADO).
    Exclusivo para administradores.
    """

    def __init__(self, shipment_repo):
        self.shipment_repo = shipment_repo

    def execute(self, actor: dict) -> list[dict]:
        """
        Ejecuta el listado de paquetes pendientes.

        Args:
            actor (dict): Usuario solicitante (debe ser ADMIN).

        Returns:
            list[dict]: Lista de paquetes pendientes.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")
        
        if actor.get("role") != "ADMIN":
            raise PermissionError("Solo los administradores pueden ver paquetes pendientes")

        pending_shipments = self.shipment_repo.list_pending()
        return pending_shipments
