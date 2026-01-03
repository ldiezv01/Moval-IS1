from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class ManageSettings:
    ALLOWED_LANGUAGES = {"es", "en"}
    ALLOWED_THEMES = {"light", "dark"}

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, actor: dict, settings: dict) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if settings is None or not isinstance(settings, dict) or len(settings) == 0:
            raise ValidationError("Settings must be a non-empty dict")

        user_id = actor["id"]

        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")

        if "language" in settings:
            if settings["language"] not in self.ALLOWED_LANGUAGES:
                raise ValidationError("Idioma no soportado")

        if "theme" in settings:
            if settings["theme"] not in self.ALLOWED_THEMES:
                raise ValidationError("Tema no soportado")

        current_settings = user.get("settings") or {}
        if not isinstance(current_settings, dict):
            current_settings = {}

        new_settings = {**current_settings, **settings}

        updated_user = self.user_repo.update(user_id, {"settings": new_settings})
        if not updated_user:
            updated_user = self.user_repo.get(user_id)

        return updated_user
