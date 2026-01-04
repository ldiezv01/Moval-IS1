import sys
import os
import webbrowser

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.persistence.repositories import ShipmentRepo
from moval.services.route_service import RouteService
from moval.usecases.generate_delivery_route import GenerateDeliveryRoute

def test_usecase():
    print("--- Probando Use Case: Generar Ruta de Reparto ---")
    
    # 1. Setup Dependencies
    repo = ShipmentRepo()
    service = RouteService()
    usecase = GenerateDeliveryRoute(repo, service)
    
    # Courier ID 2 (Juan) has assigned packages in init_db.py
    courier_id = 2
    
    try:
        print(f"Generando ruta para Mensajero ID {courier_id}...")
        result = usecase.execute(courier_id)
        
        print("\n¡Éxito!")
        print(f"Tiempo estimado: {result['total_time_minutes']} min")
        print(f"Distancia: {result['total_distance_km']} km")
        print(f"Mapa: {result['map_path']}")
        
        print("\nOrden optimizado de entrega:")
        for i, pkg in enumerate(result['ordered_shipments'], 1):
            print(f" {i}. {pkg['codigo']} - {pkg['direccion']}")
            
        # Abrir mapa
        webbrowser.open('file://' + os.path.realpath(result['map_path']))
        
    except ValueError as ve:
        print(f"Validación: {ve}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_usecase()
