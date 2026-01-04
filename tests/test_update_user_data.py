import unittest
from unittest.mock import MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.usecases.update_user_data import UpdateUserData
from moval.usecases.errors import ValidationError, NotFoundError

class TestUpdateUserData(unittest.TestCase):
    
    def setUp(self):
        self.mock_user_repo = MagicMock()
        self.usecase = UpdateUserData(self.mock_user_repo)

    def test_update_success(self):
        actor = {"id": 1, "role": "CUSTOMER"}
        fields = {"nombre": "NuevoNombre", "telefono": "666555444"}
        
        # Simular que el usuario existe
        self.mock_user_repo.get.return_value = {"id": 1, "email": "test@test.com", "nombre": "Viejo"}
        
        result = self.usecase.execute(actor, fields)
        
        self.mock_user_repo.update.assert_called_with(1, fields)
        self.mock_user_repo.get.assert_called_with(1)

    def test_update_duplicate_email(self):
        actor = {"id": 1, "role": "CUSTOMER"}
        fields = {"email": "existing@test.com"}
        
        self.mock_user_repo.get.return_value = {"id": 1, "email": "my@email.com"}
        # El email ya existe
        self.mock_user_repo.exists_email.return_value = True
        
        with self.assertRaises(ValidationError):
            self.usecase.execute(actor, fields)

if __name__ == '__main__':
    unittest.main()
