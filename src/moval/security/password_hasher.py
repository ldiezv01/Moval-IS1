from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

class PasswordHasher:
    def __init__(self):
        # Configuracion por defecto de Argon2id (seguro y moderno)
        self.ph = Argon2Hasher()

    def hash(self, password: str) -> str:
        """Devuelve el hash seguro de la contraseña."""
        return self.ph.hash(password)

    def verify(self, password: str, hash_str: str) -> bool:
        """Devuelve True si la contraseña coincide con el hash."""
        if not hash_str:
            return False
        try:
            self.ph.verify(hash_str, password)
            return True
        except VerifyMismatchError:
            return False
        except Exception:
            # Captura errores de formato en el hash
            return False
