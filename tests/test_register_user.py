import unittest
from unittest.mock import MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.usecases.register_user import RegisterUser
from moval.usecases.errors import ValidationError, ConflictError

class TestRegisterUser(unittest.TestCase):
    
    def setUp(self):
        self.mock_user_repo = MagicMock()
        self.mock_hasher = MagicMock()
        self.usecase = RegisterUser(self.mock_user_repo, self.mock_hasher)

    def test_register_success(self):
        # Datos de entrada válidos
        data = {
            "dni": "12345678A",
            "nombre": "Nuevo",
            "apellidos": "Usuario",
            "email": "new@moval.com",
            "password": "Password123" # Cumple requisitos
        }
        
        # Mocks
        self.mock_user_repo.exists_email.return_value = False
        self.mock_hasher.hash.return_value = "hashed_secret"
        self.mock_user_repo.create.return_value = 100 # Nuevo ID simulado

        # Ejecución
        result = self.usecase.execute(data)

        # Verificación
        self.assertEqual(result["id"], 100)
        self.assertEqual(result["email"], "new@moval.com")
        self.assertEqual(result["role"], "CUSTOMER")
        
        # Verificar que se llamó al hasher y al repo
        self.mock_hasher.hash.assert_called_with("Password123")
        self.mock_user_repo.create.assert_called()
        
        # Verificar argumentos de create (no podemos comprobar el dict exacto fácilmente si no guardamos ref, 
        # pero podemos ver si password_hash es el correcto)
        args, _ = self.mock_user_repo.create.call_args
        created_user = args[0]
        self.assertEqual(created_user["password_hash"], "hashed_secret")
        self.assertEqual(created_user["role"], "CUSTOMER")

    def test_register_duplicate_email(self):
        data = {
            "dni": "12345678A",
            "nombre": "Duplicado",
            "apellidos": "User",
            "email": "exists@moval.com",
            "password": "Password123"
        }
        
        # Simulamos que el email ya existe
        self.mock_user_repo.exists_email.return_value = True
        
        with self.assertRaises(ConflictError):
            self.usecase.execute(data)
            
        self.mock_user_repo.create.assert_not_called()

    def test_register_weak_password(self):
        data = {
            "dni": "12345678A",
            "nombre": "Weak",
            "apellidos": "User",
            "email": "weak@moval.com",
            "password": "123" # Muy corta y simple
        }
        
        # Email no existe, pero pass es mala
        self.mock_user_repo.exists_email.return_value = False
        
        with self.assertRaises(ValidationError):
            self.usecase.execute(data)

    def test_register_missing_fields(self):
        data = {
            "email": "incomplete@moval.com",
            "password": "Password123"
            # Falta DNI y nombre
        }
        
        with self.assertRaises(ValidationError):
            self.usecase.execute(data)

if __name__ == '__main__':
    unittest.main()
