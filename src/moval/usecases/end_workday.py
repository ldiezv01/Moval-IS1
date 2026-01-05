from moval.usecases.errors import ValidationError, PermissionError, ConflictError

class EndWorkday:
    def __init__(self, workday_repo, clock):
        self.workday_repo = workday_repo
        self.clock = clock

    def execute(self, actor: dict) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if actor["role"] != "COURIER":
            raise PermissionError("Only couriers can end workdays")

        active_workday = self.workday_repo.get_active_workday(actor["id"])
        if not active_workday:
            raise ConflictError("There is no active workday for this courier")

        end_time = self.clock.now()

        workday = self.workday_repo.close_workday(
            workday_id=active_workday["id"],
            end_ts=end_time
        )

        return workday
