from moval.usecases.errors import ValidationError, PermissionError

class ListAvailableCouriers:
    """
    Lista los mensajeros que tienen una jornada activa y pueden recibir asignaciones.
    Exclusivo para administradores.
    """

    def __init__(self, courier_repo):
        self.courier_repo = courier_repo

    def execute(self, actor: dict) -> list[dict]:
        """
        Recupera la lista de mensajeros disponibles.

        Args:
            actor (dict): Usuario solicitante (debe ser ADMIN).

        Returns:
            list[dict]: Lista de mensajeros activos.
        """
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if actor.get("role") != "ADMIN":
            raise PermissionError("Solo los administradores pueden listar mensajeros disponibles")

        return self.courier_repo.list_available()
