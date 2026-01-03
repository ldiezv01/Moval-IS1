from moval.usecases.errors import ValidationError

class GetHelpContent:
    def __init__(self, help_repo):
        self.help_repo = help_repo

    def execute(self, actor: dict) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        content = self.help_repo.load_help_content()
        return {"help": content}
