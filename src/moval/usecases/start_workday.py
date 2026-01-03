from moval.usecases.errors import ValidationError, PermissionError, ConflictError

class StartWorkday:
    def __init__(self, workday_repo, clock):
        self.workday_repo = workday_repo
        self.clock = clock

    def execute(self, actor: dict) -> dict:
        if actor["role"] != "COURIER":
            raise PermissionError("Only couriers can start a workday")

        if self.workday_repo.get_active_workday(actor["id"]):
            raise ConflictError(
                "There is already an active workday for this courier"
            )

        start_time = self.clock.now_utc()

        workday = self.workday_repo.create_workday(
            courier_id=actor["id"],
            start_time=start_time
        )

        return workday
