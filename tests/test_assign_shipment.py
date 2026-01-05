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

    def test_assign_success_even_if_unavailable(self):
        # Admin intenta asignar
        actor = {"id": 1, "role": "ADMIN"}
        shipment_ids = [101]
        courier_id = 5
        
        # Mock de mensajero NO disponible (esto antes fallaba, ahora debe pasar)
        self.mock_courier_repo.get.return_value = {"id": courier_id, "status": "UNAVAILABLE"}
        
        # Mock del paquete pendiente
        self.mock_shipment_repo.get.return_value = {"id": 101, "estado": ShipmentStatus.PENDING.value}
        
        # Ejecución
        result = self.usecase.execute(actor, shipment_ids, courier_id)

        # Verificación
        self.assertEqual(len(result["assigned_shipments"]), 1)
        self.assertEqual(result["assigned_shipments"][0]["estado"], ShipmentStatus.ASSIGNED.value)
        self.assertEqual(result["assigned_shipments"][0]["id_mensajero"], courier_id)
        
        # Verificar que se llamó a assign (asignación masiva)
        self.mock_shipment_repo.assign.assert_called_with(
            shipment_id=[101],
            courier_id=courier_id
        )

    def test_only_admin_can_assign(self):
        actor = {"id": 2, "role": "COURIER"} 
        
        with self.assertRaises(PermissionError):
            self.usecase.execute(actor, [101], 5)

    def test_cannot_assign_non_pending_shipment(self):
        actor = {"id": 1, "role": "ADMIN"}
        
        self.mock_courier_repo.get.return_value = {"id": 5, "status": "AVAILABLE"}
        # El paquete ya está en reparto
        self.mock_shipment_repo.get.return_value = {"id": 101, "estado": ShipmentStatus.EN_ROUTE.value}
        
        with self.assertRaises(ConflictError):
            self.usecase.execute(actor, [101], 5)

    def test_courier_not_found(self):
        actor = {"id": 1, "role": "ADMIN"}
        self.mock_courier_repo.get.return_value = None
        
        with self.assertRaises(NotFoundError):
            self.usecase.execute(actor, [101], 999)

if __name__ == '__main__':
    unittest.main()