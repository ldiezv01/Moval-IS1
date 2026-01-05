from moval.usecases.errors import ValidationError, PermissionError

class ListAvailableCouriers:
    """
    Lista todos los mensajeros (activos o no) para propósitos de administración/asignación.
    """

    def __init__(self, courier_repo):
        self.courier_repo = courier_repo

    def execute(self, actor: dict) -> list[dict]:
        """
        Recupera la lista de todos los mensajeros.

        Args:
            actor (dict): Usuario solicitante (debe ser ADMIN).

        Returns:
            list[dict]: Lista de todos los mensajeros.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if actor.get("role") != "ADMIN":
            raise PermissionError("Solo los administradores pueden listar mensajeros disponibles")

        return self.courier_repo.list_all_couriers()
