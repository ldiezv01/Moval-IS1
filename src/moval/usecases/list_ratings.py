from moval.usecases.errors import ValidationError, PermissionError

class ListRatings:
    """
    Permite al administrador consultar todas las valoraciones recibidas.
    """
    def __init__(self, rating_repo):
        self.rating_repo = rating_repo

    def execute(self, actor: dict) -> list[dict]:
        if not actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if actor["role"] != "ADMIN":
            raise PermissionError("Solo el administrador puede ver el listado de valoraciones")

        return self.rating_repo.list_all()
