import sys
import os
import webbrowser

# Add src to path to find the module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.services.route_service import RouteService

def test_route_generation():
    print("--- Iniciando prueba de RouteService ---")
    
    service = RouteService()
    
    # Datos de prueba (Puntos en León)
    packages = [
        {
            "id": 1,
            "direccion": "Catedral de León",
            "latitud": 42.5990,
            "longitud": -5.5666
        },
        {
            "id": 2,
            "direccion": "MUSAC (Museo de Arte)",
            "latitud": 42.6063,
            "longitud": -5.5862
        },
        {
            "id": 3,
            "direccion": "Estación de Tren",
            "latitud": 42.5960,
            "longitud": -5.5830
        }
    ]
    
    print(f"Calculando ruta para {len(packages)} paquetes...")
    
    try:
        result = service.calculate_optimized_route(packages)
        
        print("\n¡Ruta calculada con éxito!")
        print(f"Tiempo Total: {result['total_time_minutes']} minutos")
        print(f"Distancia Total: {result['total_distance_km']} km")
        print(f"Archivo de mapa generado: {result['map_path']}")
        print(f"Orden de waypoints (índices): {result['waypoints_order']}")
        
        # Intentar abrir el mapa automáticamente
        print(f"\nAbriendo mapa en el navegador...")
        webbrowser.open('file://' + os.path.realpath(result['map_path']))
        
    except Exception as e:
        print(f"\nERROR: Falló el cálculo de la ruta: {e}")

if __name__ == "__main__":
    test_route_generation()
