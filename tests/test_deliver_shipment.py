import unittest
from unittest.mock import MagicMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.usecases.deliver_shipment import DeliverShipment
from moval.usecases.errors import PermissionError, ValidationError, NotFoundError, ConflictError
from moval.domain.enums import ShipmentStatus

class TestDeliverShipment(unittest.TestCase):
    
    def setUp(self):
        self.mock_shipment_repo = MagicMock()
        self.mock_clock = MagicMock()
        self.usecase = DeliverShipment(self.mock_shipment_repo, self.mock_clock)

    def test_deliver_success(self):
        courier_id = 5
        shipment_id = 202
        actor = {"id": courier_id, "role": "COURIER"}
        
        # El paquete está asignado a ESTE mensajero
        # Usamos nombres de columna reales (id_mensajero, estado) y valores en español
        self.mock_shipment_repo.get.return_value = {
            "id": shipment_id, 
            "estado": ShipmentStatus.ASSIGNED.value, 
            "id_mensajero": courier_id
        }
        
        now = datetime.now()
        self.mock_clock.now.return_value = now
        
        self.mock_shipment_repo.set_status.return_value = {
            "id": shipment_id, 
            "estado": ShipmentStatus.DELIVERED.value, 
            "delivered_at": now
        }

        result = self.usecase.execute(actor, shipment_id)

        self.assertEqual(result["estado"], ShipmentStatus.DELIVERED.value)
        self.mock_shipment_repo.set_status.assert_called_with(
            shipment_id=shipment_id,
            status=ShipmentStatus.DELIVERED,
            delivered_at=now
        )

    def test_cannot_deliver_others_shipment(self):
        actor = {"id": 5, "role": "COURIER"}
        # El paquete pertenece al mensajero 99
        self.mock_shipment_repo.get.return_value = {
            "id": 202, 
            "estado": ShipmentStatus.ASSIGNED.value, 
            "id_mensajero": 99
        }
        
        with self.assertRaises(PermissionError):
            self.usecase.execute(actor, 202)

    def test_cannot_deliver_already_delivered(self):
        actor = {"id": 5, "role": "COURIER"}
        self.mock_shipment_repo.get.return_value = {
            "id": 202, 
            "estado": ShipmentStatus.DELIVERED.value, 
            "id_mensajero": 5
        }
        
        with self.assertRaises(ConflictError):
            self.usecase.execute(actor, 202)

if __name__ == '__main__':
    unittest.main()
