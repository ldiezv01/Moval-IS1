import unittest
from unittest.mock import MagicMock
from datetime import datetime

import sys
import os
# Ajuste de path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.usecases.end_workday import EndWorkday
from moval.usecases.errors import PermissionError, ConflictError, ValidationError

class TestEndWorkday(unittest.TestCase):
    
    def setUp(self):
        self.mock_repo = MagicMock()
        self.mock_clock = MagicMock()
        self.usecase = EndWorkday(self.mock_repo, self.mock_clock)

    def test_end_workday_success(self):
        # 1. Preparación
        courier_id = 15
        workday_id = 100
        actor = {"id": courier_id, "role": "COURIER"}
        
        # Simulamos que SÍ hay una jornada activa
        active_workday = {"id": workday_id, "id_mensajero": courier_id, "estado": "ACTIVA"}
        self.mock_repo.get_active_workday.return_value = active_workday
        
        # Hora de fin fija
        end_time = datetime(2026, 1, 4, 18, 0, 0)
        self.mock_clock.now_utc.return_value = end_time
        
        # Resultado esperado del repo
        closed_workday = {**active_workday, "fecha_fin": end_time, "estado": "FINALIZADA"}
        self.mock_repo.close_workday.return_value = closed_workday

        # 2. Ejecución
        result = self.usecase.execute(actor)

        # 3. Verificación
        self.assertEqual(result["estado"], "FINALIZADA")
        self.assertEqual(result["fecha_fin"], end_time)
        
        # Verificar llamadas al repo
        self.mock_repo.get_active_workday.assert_called_with(courier_id)
        self.mock_repo.close_workday.assert_called_with(
            workday_id=workday_id,
            end_ts=end_time
        )

    def test_only_courier_can_end_workday(self):
        actor = {"id": 20, "role": "CUSTOMER"}
        
        with self.assertRaises(PermissionError):
            self.usecase.execute(actor)
            
        self.mock_repo.close_workday.assert_not_called()

    def test_cannot_end_if_no_active_workday(self):
        courier_id = 15
        actor = {"id": courier_id, "role": "COURIER"}
        
        # El repo dice que NO hay jornada activa
        self.mock_repo.get_active_workday.return_value = None
        
        with self.assertRaises(ConflictError):
            self.usecase.execute(actor)
            
        self.mock_repo.close_workday.assert_not_called()

if __name__ == '__main__':
    unittest.main()
