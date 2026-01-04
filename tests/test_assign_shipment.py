import unittest
from unittest.mock import MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.usecases.assign_shipment import AssignShipments
from moval.usecases.errors import PermissionError, ValidationError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class TestAssignShipment(unittest.TestCase):
    
    def setUp(self):
        self.mock_shipment_repo = MagicMock()
        self.mock_courier_repo = MagicMock()
        self.usecase = AssignShipments(self.mock_shipment_repo, self.mock_courier_repo)

    def test_assign_success(self):
        # Admin intenta asignar
        actor = {"id": 1, "role": "ADMIN"}
        shipment_ids = [101]
        courier_id = 5
        
        # Mocks de respuesta
        self.mock_courier_repo.get_by_id.return_value = {"id": courier_id, "status": "AVAILABLE"}
        # DEBE devolver 'estado' (columna BD) y valor 'REGISTRADO' (Enum español)
        self.mock_shipment_repo.get.return_value = {"id": 101, "estado": ShipmentStatus.PENDING.value}
        
        # El repo devuelve el objeto actualizado
        self.mock_shipment_repo.set_status.return_value = {"id": 101, "estado": ShipmentStatus.ASSIGNED.value, "courier_id": courier_id}

        result = self.usecase.execute(actor, shipment_ids, courier_id)

        self.assertEqual(len(result["assigned_shipments"]), 1)
        self.assertEqual(result["assigned_shipments"][0]["estado"], ShipmentStatus.ASSIGNED.value)
        
        # Verificar que se llamó con los parámetros correctos (pasando el Enum object)
        self.mock_shipment_repo.set_status.assert_called_with(
            shipment_id=101,
            status=ShipmentStatus.ASSIGNED,
            courier_id=courier_id
        )

    def test_only_admin_can_assign(self):
        actor = {"id": 2, "role": "COURIER"} 
        
        with self.assertRaises(PermissionError):
            self.usecase.execute(actor, [101], 5)

    def test_cannot_assign_non_pending_shipment(self):
        actor = {"id": 1, "role": "ADMIN"}
        
        self.mock_courier_repo.get_by_id.return_value = {"id": 5, "status": "AVAILABLE"}
        # El paquete ya está en reparto
        self.mock_shipment_repo.get.return_value = {"id": 101, "estado": ShipmentStatus.EN_ROUTE.value}
        
        with self.assertRaises(ConflictError):
            self.usecase.execute(actor, [101], 5)

if __name__ == '__main__':
    unittest.main()
