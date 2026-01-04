from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class UpdateUserData:
    """
    Permite a un usuario actualizar su información de perfil.
    """
    ALLOWED_FIELDS = {"nombre", "apellidos", "telefono", "email"}

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, actor: dict, fields: dict) -> dict:
        if not actor or "id" not in actor or "role" not in actor:
            raise ValidationError("Datos de usuario requeridos")

        if not fields or not isinstance(fields, dict):
            raise ValidationError("Debe proporcionar los campos a actualizar")

        # Filtrar campos no permitidos
        invalid = [k for k in fields.keys() if k not in self.ALLOWED_FIELDS]
        if invalid:
            raise ValidationError(f"Campos no permitidos: {', '.join(invalid)}")

        user_id = actor["id"]
        user = self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")

        # Si cambia el email, verificar que no esté duplicado
        if "email" in fields and fields["email"] != user.get("email"):
            if self.user_repo.exists_email(fields["email"]):
                raise ValidationError("El correo electrónico ya está en uso por otro usuario")

        # Realizar la actualización
        self.user_repo.update(user_id, fields)
        
        # Devolver el usuario actualizado
        return self.user_repo.get(user_id)
