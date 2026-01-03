from moval.usecases.errors import ValidationError, PermissionError

class ListAvailableCouriers:
    def __init__(self, courier_repo):
        self.courier_repo = courier_repo

    def execute(self, actor: dict) -> list[dict]:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor.get("role") != "ADMIN":
            raise PermissionError("Only ADMIN can list available couriers")

        return self.courier_repo.list_available()
