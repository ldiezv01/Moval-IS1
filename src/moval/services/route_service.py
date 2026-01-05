import requests
import folium
import os
import json
import webbrowser

class RouteService:
    # Coordinates for Universidad de León (Campus de Vegazana)
    WAREHOUSE_LAT = 42.6136
    WAREHOUSE_LON = -5.5583
    
    # OSRM Trip API endpoint
    OSRM_API_URL = "http://router.project-osrm.org/trip/v1/driving/{coords}"

    def calculate_optimized_route(self, packages: list, start_coords: tuple = None) -> dict:
        """
        Calculates optimized route.
        If start_coords (lat, lon) is provided, starts from there.
        Otherwise starts from Warehouse.
        Ends at Warehouse.
        """
        try:
            # Empty check removed to allow Return Trip (Start -> Warehouse)
            # if not packages: raise ValueError("The package list is empty.")

            coords_list = []
            
            # 1. Determine Start Point
            if start_coords:
                # Custom Start (Last delivery)
                coords_list.append(f"{start_coords[1]},{start_coords[0]}")
            else:
                # Warehouse Start
                coords_list.append(f"{self.WAREHOUSE_LON},{self.WAREHOUSE_LAT}")
            
            # Add Packages
            def get_val(obj, key):
                return getattr(obj, key) if hasattr(obj, key) else obj[key]

            for pkg in packages:
                lat = float(get_val(pkg, 'latitud'))
                lon = float(get_val(pkg, 'longitud'))
                coords_list.append(f"{lon},{lat}")
            
            # End at Warehouse
            coords_list.append(f"{self.WAREHOUSE_LON},{self.WAREHOUSE_LAT}")
            
            coords_str = ";".join(coords_list)

            # Call OSRM API
            params = {
                "source": "first",
                "destination": "last",
                "roundtrip": "false", 
                "overview": "full",
                "geometries": "geojson"
            }
            
            url = self.OSRM_API_URL.format(coords=coords_str)
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != "Ok":
                raise Exception(f"OSRM API Error: {data.get('code')} - {data.get('message')}")

            trips = data.get("trips", [])
            if not trips:
                raise Exception("No route found.")
            
            trip = trips[0]
            geometry = trip["geometry"]
            total_duration_sec = trip["duration"]
            total_distance_meters = trip["distance"]
            
            # Generate Map
            # Center on Start
            start_lat = start_coords[0] if start_coords else self.WAREHOUSE_LAT
            start_lon = start_coords[1] if start_coords else self.WAREHOUSE_LON
            m = folium.Map(location=[start_lat, start_lon], zoom_start=13)

            # Mark Start
            folium.Marker(
                [start_lat, start_lon],
                tooltip="Inicio (Actual)",
                icon=folium.Icon(color="green", icon="play")
            ).add_to(m)

            # Mark Warehouse (End)
            folium.Marker(
                [self.WAREHOUSE_LAT, self.WAREHOUSE_LON],
                tooltip="Almacén (Fin)",
                icon=folium.Icon(color="red", icon="home")
            ).add_to(m)

            folium.GeoJson(
                geometry,
                name="Ruta Optimizada",
                style_function=lambda x: {'color': 'blue', 'weight': 5, 'opacity': 0.7}
            ).add_to(m)

            optimized_indices = []
            
            for i, wp in enumerate(data.get("waypoints", [])):
                original_idx = wp['waypoint_index']
                optimized_indices.append(original_idx)

                # Skip start (0) and end (len-1) for package markers
                if original_idx == 0 or original_idx == len(coords_list) - 1:
                    continue
                
                # Pkg Index
                pkg_idx = original_idx - 1
                if 0 <= pkg_idx < len(packages):
                    pkg = packages[pkg_idx]
                    p_lat = float(get_val(pkg, 'latitud'))
                    p_lon = float(get_val(pkg, 'longitud'))
                    p_dir = get_val(pkg, 'direccion')
                    
                    folium.Marker(
                        [p_lat, p_lon],
                        tooltip=f"{i}. {p_dir}",
                        icon=folium.Icon(color="blue", icon="box", prefix="fa"),
                        popup=f"Entrega #{i}<br>{p_dir}"
                    ).add_to(m)

            output_dir = os.path.join(os.getcwd(), 'docs', 'exports')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            map_filename = "ruta_optimizada.html"
            map_path = os.path.join(output_dir, map_filename)
            m.save(map_path)

            return {
                "total_time_minutes": int(total_duration_sec / 60),
                "total_distance_km": round(total_distance_meters / 1000, 2),
                "map_path": map_path,
                "waypoints_order": optimized_indices,
                "legs": trip.get("legs", [])
            }

        except Exception as e:
            print(f"Error calculating route: {e}")
            raise e

if __name__ == "__main__":
    pass