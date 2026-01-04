from moval.persistence.repositories import ShipmentRepo
from moval.services.route_service import RouteService
from moval.domain.enums import ShipmentStatus

class GenerateDeliveryRoute:
    def __init__(self, shipment_repo: ShipmentRepo, route_service: RouteService):
        self.shipment_repo = shipment_repo
        self.route_service = route_service

    def execute(self, courier_id: int) -> dict:
        """
        Generates an optimized route for all active shipments assigned to the courier.
        """
        # 1. Get shipments assigned to courier that are not yet delivered
        # We can filter locally or add a method to repo. 
        # Using list_by_courier and filtering by status.
        all_shipments = self.shipment_repo.list_by_courier(courier_id)
        
        # Filter for active shipments
        active_statuses = ['ASIGNADO', 'EN_REPARTO']
        active_shipments = [s for s in all_shipments if s['estado'] in active_statuses]

        if not active_shipments:
            raise ValueError("No active shipments found for this courier.")

        # 2. Prepare data for RouteService
        # RouteService expects objects/dicts with latitud, longitud, direccion
        route_packages = []
        for s in active_shipments:
            # Ensure coordinates exist
            if s.get('latitud') is None or s.get('longitud') is None:
                # If any package misses coords, we might skip it or fail.
                # For now, let's skip and log/print? Or fail.
                # Given strict route requirements, failing is safer than giving a wrong route.
                # But to be robust, let's filter them out and warn.
                continue
            
            route_packages.append({
                "id": s['id'], # Keep ID to trace back
                "codigo": s['codigo_seguimiento'],
                "direccion": s['direccion_destino'],
                "latitud": s['latitud'],
                "longitud": s['longitud']
            })

        if not route_packages:
            raise ValueError("No shipments with valid coordinates found.")

        # 3. Calculate Route
        route_result = self.route_service.calculate_optimized_route(route_packages)
        
        # 4. (Optional) Enhance result with Shipment details if needed
        # The result has 'waypoints_order' which are indices in the 'route_packages' list.
        # We might want to map these back to shipment IDs.
        
        ordered_shipments = []
        for idx in route_result['waypoints_order']:
            # warehouse is 0 and last index, so skipped or handled in service?
            # Service implementation returns indices of the input list.
            # wait, service logic:
            # "original_idx = wp['waypoint_index'] ... pkg_idx = original_idx - 1"
            # And it returns `optimized_indices` which are the original OSRM indices.
            # If I want the ordered list of shipments, I need to parse that.
            
            # Actually, `RouteService` returns `waypoints_order` list of "original_idx".
            # 0 is Warehouse.
            # 1 is package[0], 2 is package[1]...
            
            # Let's map it back to provide a clean ordered list of packages.
            if idx == 0 or idx == len(route_packages) + 1:
                # Warehouse
                continue
            
            pkg_idx = idx - 1
            if 0 <= pkg_idx < len(route_packages):
                ordered_shipments.append(route_packages[pkg_idx])
        
        route_result['ordered_shipments'] = ordered_shipments
        
        return route_result
