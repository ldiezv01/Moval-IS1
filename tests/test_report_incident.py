import unittest
from unittest.mock import MagicMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.usecases.report_incident import ReportIncident
from moval.usecases.errors import PermissionError, ValidationError, NotFoundError
from moval.domain.enums import ShipmentStatus

class TestReportIncident(unittest.TestCase):
    
    def setUp(self):
        self.mock_shipment_repo = MagicMock()
        self.mock_incident_repo = MagicMock()
        self.mock_clock = MagicMock()
        self.usecase = ReportIncident(self.mock_shipment_repo, self.mock_incident_repo, self.mock_clock)

    def test_courier_report_success(self):
        # Datos
        courier_id = 5
        shipment_id = 300
        actor = {"id": courier_id, "role": "COURIER"}
        
        # Paquete asignado al mensajero
        self.mock_shipment_repo.get.return_value = {
            "id": shipment_id,
            "id_mensajero": courier_id,
            "id_cliente": 99,
            "estado": ShipmentStatus.ASSIGNED.value
        }
        
        now = datetime.now()
        self.mock_clock.now.return_value = now

        # Ejecución
        result = self.usecase.execute(actor, shipment_id, "Paquete dañado")

        # Verificación
        self.assertEqual(result["shipment_id"], shipment_id)
        
        # 1. Se creó la incidencia
        self.mock_incident_repo.create_incident.assert_called_with(
            shipment_id=shipment_id,
            reported_id=courier_id,
            description="Paquete dañado"
        )
        
        # 2. Se actualizó el estado del paquete (sin quitar mensajero)
        self.mock_shipment_repo.update.assert_called_with(
            shipment_id=shipment_id,
            fields={
                "estado": ShipmentStatus.INCIDENT.value
            }
        )
        
        # 3. Se duplicó el paquete
        self.mock_shipment_repo.create_copy.assert_called()

    def test_customer_report_success(self):
        customer_id = 99
        shipment_id = 300
        actor = {"id": customer_id, "role": "CUSTOMER"}
        
        # Paquete pertenece al cliente
        self.mock_shipment_repo.get.return_value = {
            "id": shipment_id,
            "id_mensajero": 5,
            "id_cliente": customer_id,
            "estado": ShipmentStatus.EN_ROUTE.value
        }

        self.usecase.execute(actor, shipment_id, "No estaba en casa")

        # Verificar actualización
        self.mock_shipment_repo.update.assert_called_with(
            shipment_id=shipment_id,
            fields={
                "estado": ShipmentStatus.INCIDENT.value
            }
        )
        self.mock_shipment_repo.create_copy.assert_called()

    def test_courier_cannot_report_others_shipment(self):
        actor = {"id": 5, "role": "COURIER"}
        shipment_id = 300
        
        # Paquete asignado a OTRO mensajero (ID 7)
        self.mock_shipment_repo.get.return_value = {
            "id": shipment_id,
            "id_mensajero": 7,
            "id_cliente": 99
        }

        with self.assertRaises(PermissionError):
            self.usecase.execute(actor, shipment_id, "Problema")
            
        self.mock_incident_repo.create_incident.assert_not_called()
        self.mock_shipment_repo.set_status.assert_not_called()

if __name__ == '__main__':
    unittest.main()
