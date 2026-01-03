from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class GetActiveWorkday:
    def __init__(self, workday_repo):
        self.workday_repo = workday_repo

    def execute(self, actor: dict, courier_id: int | None = None) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor information is incomplete.")

        actor_id = actor["id"]
        actor_role = actor["role"]

        if actor_role == "COURIER":
            target_courier_id = actor_id
        elif actor_role == "ADMIN":
            if courier_id is None:
                raise ValidationError("courier_id must be provided by ADMIN actors.")
            target_courier_id = courier_id
        else:
            raise PermissionError("Actor does not have permission to view workdays.")

        workday = self.workday_repo.get_active_workday(target_courier_id)

        if workday is None:
            raise NotFoundError(f"No active workday found for courier ID {target_courier_id}.")

        return workday

