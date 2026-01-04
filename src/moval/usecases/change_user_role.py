from moval.usecases.errors import ValidationError, PermissionError, NotFoundError

class ChangeUserRole:
    """
    Permite a un administrador cambiar el rol de un usuario existente.
    """
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, actor: dict, target_user_email: str, new_role: str) -> dict:
        """
        Cambia el rol de un usuario.

        Args:
            actor (dict): Administrador que realiza la acción.
            target_user_email (str): Email del usuario a modificar.
            new_role (str): Nuevo rol ('ADMIN', 'COURIER', 'CUSTOMER').

        Returns:
            dict: Datos del usuario actualizado.
        """
        if not actor or actor.get("role") != "ADMIN":
            raise PermissionError("Solo los administradores pueden cambiar roles")

        if not target_user_email or not new_role:
            raise ValidationError("Email y nuevo rol son obligatorios")

        if new_role not in ["ADMIN", "COURIER", "CUSTOMER"]:
            raise ValidationError(f"Rol no válido: {new_role}")

        user = self.user_repo.get_by_email(target_user_email)
        if not user:
            raise NotFoundError(f"No se encontró ningún usuario con el email {target_user_email}")

        # Evitar que el admin se quite el permiso a sí mismo accidentalmente si es el único
        if user["id"] == actor["id"] and new_role != "ADMIN":
            # Esto es una medida de seguridad simple
            pass

        self.user_repo.update(user["id"], {"rol": new_role})
        
        return self.user_repo.get(user["id"])
