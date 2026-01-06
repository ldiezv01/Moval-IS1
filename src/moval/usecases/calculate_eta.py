from datetime import timedelta
from moval.usecases.errors import ValidationError, PermissionError, NotFoundError
from moval.domain.enums import ShipmentStatus

class CalculateETA:
    """
    Calcula el ETA usando el RouteService para obtener tiempos reales de ruta.
    """
    def __init__(self, shipment_repo, route_service, clock, workday_repo):
        self.shipment_repo = shipment_repo
        self.route_service = route_service
        self.clock = clock
        self.workday_repo = workday_repo
        self.SERVICE_TIME_PER_STOP_MIN = 10 # Tiempo estimado por entrega

    def execute(self, actor: dict, shipment_id: int) -> dict:
        if not actor: raise ValidationError("Auth required")
        
        shipment = self.shipment_repo.get(shipment_id)
        if not shipment: raise NotFoundError("Paquete no encontrado")

        # Permisos
        if actor["role"] == "CUSTOMER" and shipment["id_cliente"] != actor["id"]:
            raise PermissionError("No es tu paquete")
        if actor["role"] == "COURIER" and shipment["id_mensajero"] != actor["id"]:
            raise PermissionError("No es tu paquete")

        status = shipment["estado"]
        
        # 1. Entregado
        if status == ShipmentStatus.DELIVERED.value:
            return {
                "eta_minutos": 0, 
                "fecha_estimada": shipment.get("fecha_entrega_real"),
                "texto_mostrar": "Entregado"
            }

        # 2. No asignado -> ETA genérico (ej. 24h)
        if not shipment.get("id_mensajero") or status == ShipmentStatus.PENDING.value:
             return {
                 "eta_minutos": None, 
                 "info": "Pendiente de asignación",
                 "texto_mostrar": "Aún no ha salido del almacén"
             }

        # 3. Calculo Real con Ruta
        courier_id = shipment["id_mensajero"]
        
        # Verificar si el repartidor tiene jornada activa
        active_wd = self.workday_repo.get_active_workday(courier_id)
        if not active_wd:
             return {
                 "eta_minutos": None,
                 "info": "Repartidor inactivo",
                 "texto_mostrar": "Repartidor en espera"
             }
        
        # Obtener todos los paquetes activos del mensajero
        all_pkgs = self.shipment_repo.list_by_courier(courier_id)
        active_pkgs = [
            p for p in all_pkgs 
            if p['estado'] in [ShipmentStatus.ASSIGNED.value, ShipmentStatus.EN_ROUTE.value]
            and p.get('latitud') and p.get('longitud')
        ]
        
        # Si el paquete actual no tiene coords o no está en la lista activa (raro)
        if str(shipment_id) not in [str(p['id']) for p in active_pkgs]:
             # Fallback heurístico
             return {"eta_minutos": 60, "info": "Aprox (Sin ruta)"}

        # Preparar datos para RouteService
        route_input = []
        for p in active_pkgs:
            route_input.append({
                "id": p['id'],
                "latitud": p['latitud'],
                "longitud": p['longitud'],
                "direccion": p['direccion_destino']
            })

        try:
            route_data = self.route_service.calculate_optimized_route(route_input)
            
            # Analizar la ruta para encontrar nuestro paquete
            # waypoints_order: índices de la lista route_input. 
            # 0 es Warehouse, 1..N son pkgs, N+1 es Warehouse.
            # legs: duraciones entre paradas. legs[0] es Warehouse -> 1er Stop.
            
            accumulated_seconds = 0
            found = False
            
            # route_data['waypoints_order'] son los indices originales
            # route_data['legs'] son los tramos. len(legs) == len(waypoints) - 1
            
            waypoints = route_data['waypoints_order']
            legs = route_data['legs']
            
            # Recorremos la ruta parada a parada
            # i va de 0 a len(legs)-1
            for i in range(len(legs)):
                # Sumamos el viaje hasta el siguiente punto
                leg_duration = legs[i]['duration']
                accumulated_seconds += leg_duration
                
                # El punto al que llegamos es waypoints[i+1]
                next_stop_idx = waypoints[i+1]
                
                # Es el warehouse final?
                if next_stop_idx == len(route_input) + 1:
                    break
                    
                # Es un paquete?
                # Indice en route_input es next_stop_idx - 1
                pkg_idx = next_stop_idx - 1
                
                if 0 <= pkg_idx < len(route_input):
                    pkg = route_input[pkg_idx]
                    
                    if pkg['id'] == shipment_id:
                        found = True
                        break
                    
                    # Si no es nuestro paquete, añadimos tiempo de servicio (entrega)
                    accumulated_seconds += (self.SERVICE_TIME_PER_STOP_MIN * 60)

            if found:
                eta_min = int(accumulated_seconds / 60)
                arrival_time = self.clock.now() + timedelta(minutes=eta_min)
                return {
                    "eta_minutos": eta_min,
                    "fecha_estimada": arrival_time,
                    "info": "Calculado por ruta óptima",
                    "texto_mostrar": f"{eta_min} min"
                }
            else:
                return {
                    "eta_minutos": 60, 
                    "info": "No encontrado en ruta",
                    "texto_mostrar": "60 min (Aprox)"
                }

        except Exception as e:
            print(f"Error calculando ETA real: {e}")
            return {
                "eta_minutos": 60, 
                "info": "Error ruta",
                "texto_mostrar": "Calculando..."
            }