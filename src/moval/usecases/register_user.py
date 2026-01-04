from moval.usecases.errors import ValidationError, ConflictError

class RegisterUser:
    """
    Gestiona el registro de nuevos usuarios en el sistema, incluyendo validaciones
    de seguridad, hashing de contraseñas y persistencia en base de datos.
    """

    def __init__(self, user_repo, hasher):
        self.user_repo = user_repo
        self.hasher = hasher

    def execute(self, data: dict) -> dict:
        """
        Registra un nuevo usuario con el rol predeterminado de CUSTOMER.

        Args:
            data (dict): Datos del usuario (email, password, dni, nombre, apellidos).

        Returns:
            dict: Datos del usuario creado (excluyendo información sensible).

        Raises:
            ValidationError: Si faltan campos obligatorios o la contraseña es débil.
            ConflictError: Si el email ya está registrado.
        """
        email = data.get("email")
        password = data.get("password")
        dni = data.get("dni")
        nombre = data.get("nombre")
        apellidos = data.get("apellidos")
        
        if not email or not password or not dni or not nombre:
            raise ValidationError("Email, contraseña, DNI y nombre son obligatorios")

        if self.user_repo.exists_email(email):
            raise ConflictError("El email ya está registrado")
        
        if not self._is_valid_password(password):
            raise ValidationError("La contraseña no cumple los requisitos de seguridad")
        
        # El registro público siempre crea roles de cliente.
        # Roles de administrador o mensajero se gestionan mediante procesos internos.
        role = "CUSTOMER"
        
        hashed_password = self.hasher.hash(password)
        
        user_to_create = {
            "dni": dni,
            "nombre": nombre,
            "apellidos": apellidos,
            "email": email,
            "password_hash": hashed_password,
            "role": role
        }

        user_id = self.user_repo.create(user_to_create)
        
        return {
            "id": user_id,
            "email": email,
            "role": role,
            "nombre": nombre
        }

    def _is_valid_password(self, password: str) -> bool:
        """Verifica que la contraseña tenga longitud mínima y complejidad (Mayus, Minus, Núm)."""
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_upper and has_lower and has_digit
    
        