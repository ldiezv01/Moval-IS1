from moval.usecases.errors import ValidationError, PermissionError, NotFoundError


class UpdateUserData:
    ALLOWED_FIELDS = {"name", "email", "password", "phone"}

    def __init__(self, user_repo, session_repo=None):
        self.user_repo = user_repo
        self.session_repo = session_repo  # opcional

    def execute(self, actor: dict, fields: dict, current_password: str | None = None) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Actor data is required")

        if fields is None or not isinstance(fields, dict) or len(fields) == 0:
            raise ValidationError("Fields must be a non-empty dict")

        invalid = [k for k in fields.keys() if k not in self.ALLOWED_FIELDS]
        if invalid:
            raise ValidationError(f"Campos no permitidos: {', '.join(invalid)}")

        user_id = actor["id"]

        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")

        if "email" in fields and fields["email"] != user.get("email"):
            if self.user_repo.exists_email(fields["email"]):
                raise ValidationError("El correo ya está en uso")

        changing_sensitive = ("email" in fields) or ("password" in fields)
        if changing_sensitive:
            if current_password is None or current_password == "":
                raise ValidationError("Se requiere la contraseña actual para cambiar email o contraseña")

            if not self.user_repo.verify_password(user_id, current_password):
                raise PermissionError("Contraseña actual incorrecta")

        updated_user = self.user_repo.update(user_id, fields)
        if not updated_user:
            updated_user = self.user_repo.get(user_id)
            
        return updated_user
