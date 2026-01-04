import unittest
from unittest.mock import MagicMock
from datetime import datetime

import sys
import os
# Ajuste de path para importar src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.usecases.start_workday import StartWorkday
from moval.usecases.errors import PermissionError, ConflictError

class TestStartWorkday(unittest.TestCase):
    
    def setUp(self):
        # Se ejecuta antes de cada test
        self.mock_repo = MagicMock()
        self.mock_clock = MagicMock()
        
        # El caso de uso a probar, inyectando los mocks
        self.usecase = StartWorkday(self.mock_repo, self.mock_clock)

    def test_start_workday_success(self):
        # Preparación (Arrange)
        courier_id = 10
        actor = {"id": courier_id, "role": "COURIER"}
        
        # El repo dice que NO hay jornada activa (retorna None)
        self.mock_repo.get_active_workday.return_value = None
        
        # El reloj devuelve una fecha fija
        fixed_time = datetime(2026, 1, 4, 10, 0, 0)
        self.mock_clock.now_utc.return_value = fixed_time
        
        # El repo debe simular la creación devolviendo un dict con los datos
        expected_workday = {"id": 1, "id_mensajero": courier_id, "fecha_inicio": fixed_time}
        self.mock_repo.create_workday.return_value = expected_workday

        # Ejecución (Act)
        result = self.usecase.execute(actor)

        # Verificación (Assert)
        self.assertEqual(result, expected_workday)
        
        # Verificar que se llamó al repositorio correctamente
        self.mock_repo.get_active_workday.assert_called_with(courier_id)
        self.mock_repo.create_workday.assert_called_with(
            courier_id=courier_id,
            start_time=fixed_time
        )

    def test_only_courier_can_start_workday(self):
        # Intentamos con un cliente
        actor = {"id": 20, "role": "CUSTOMER"}
        
        with self.assertRaises(PermissionError):
            self.usecase.execute(actor)
            
        # No se debió llamar al repositorio para crear nada
        self.mock_repo.create_workday.assert_not_called()

    def test_cannot_start_if_already_active(self):
        courier_id = 10
        actor = {"id": courier_id, "role": "COURIER"}
        
        # El repo dice que SÍ hay jornada activa
        self.mock_repo.get_active_workday.return_value = {"id": 999, "estado": "ACTIVA"}
        
        with self.assertRaises(ConflictError):
            self.usecase.execute(actor)
            
        # No se debió crear una nueva jornada
        self.mock_repo.create_workday.assert_not_called()

if __name__ == '__main__':
    unittest.main()
