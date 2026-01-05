from moval.persistence.repositories import ShipmentRepo
from moval.services.route_service import RouteService
from moval.domain.enums import ShipmentStatus
from datetime import datetime

class GenerateDeliveryRoute:
    def __init__(self, shipment_repo: ShipmentRepo, route_service: RouteService, workday_repo):
        self.shipment_repo = shipment_repo
        self.route_service = route_service
        self.workday_repo = workday_repo

    def execute(self, courier_id: int) -> dict:
        """
        Generates an optimized route for all active shipments assigned to the courier.
        Starts from the last delivered location *within the current workday*, or Warehouse if none.
        """
        # 1. Get shipments assigned to courier
        all_shipments = self.shipment_repo.list_by_courier(courier_id)
        
        # Filter for active shipments
        active_statuses = ['ASIGNADO', 'EN_REPARTO']
        active_shipments = [s for s in all_shipments if s['estado'] in active_statuses]

        if not active_shipments:
            raise ValueError("No active shipments found for this courier.")

        # 2. Check for last delivery location IN CURRENT WORKDAY
        start_coords = None
        
        active_workday = self.workday_repo.get_active_workday(courier_id)
        
        if active_workday and active_workday.get('fecha_inicio'):
            wd_start = str(active_workday['fecha_inicio'])
            
            # Get delivered shipments 
            delivered_shipments = [
                s for s in all_shipments 
                if s['estado'] == 'ENTREGADO' 
                and s.get('fecha_entrega_real')
                # Filter: Delivery time > Workday Start time
                and str(s.get('fecha_entrega_real')) >= wd_start
            ]
            
            if delivered_shipments:
                # Sort by delivery date descending to get the latest
                delivered_shipments.sort(key=lambda x: str(x.get('fecha_entrega_real') or ""), reverse=True)
                
                last_delivered = delivered_shipments[0]
                if last_delivered.get('latitud') and last_delivered.get('longitud'):
                    start_coords = (float(last_delivered['latitud']), float(last_delivered['longitud']))

        # 3. Prepare data for RouteService
        route_packages = []
        for s in active_shipments:
            if s.get('latitud') is None or s.get('longitud') is None:
                continue
            
            route_packages.append({
                "id": s['id'], 
                "codigo": s['codigo_seguimiento'],
                "direccion": s['direccion_destino'],
                "latitud": s['latitud'],
                "longitud": s['longitud'],
                "estado": s['estado'],
                "descripcion": s.get('descripcion', '')
            })

        if not route_packages:
            raise ValueError("No shipments with valid coordinates found.")

        # 4. Calculate Route
        route_result = self.route_service.calculate_optimized_route(route_packages, start_coords)
        
        # 5. Map back ordered shipments
        ordered_shipments = []
        for idx in route_result['waypoints_order']:
            # 0 is Start Point (Warehouse or Last Delivery)
            # len+1 is End Point (Warehouse)
            if idx == 0 or idx == len(route_packages) + 1:
                continue
            
            pkg_idx = idx - 1
            if 0 <= pkg_idx < len(route_packages):
                ordered_shipments.append(route_packages[pkg_idx])
        
        route_result['ordered_shipments'] = ordered_shipments
        
        return route_result
