import requests
from typing import Optional, Tuple

class GeocodingService:
    """
    Servicio para convertir direcciones en coordenadas usando OpenStreetMap (Nominatim).
    """
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    def geocode_address(self, address: str, structured_query: Optional[dict] = None) -> Optional[Tuple[float, float]]:
        """
        Dada una dirección en texto, devuelve (latitud, longitud) o None si no se encuentra.
        Si se pasa `structured_query`, se usa búsqueda estructurada (street, city, etc) que es más precisa.
        """
        # Nominatim requiere User-Agent
        headers = {
            'User-Agent': 'MovalApp/1.0 (Student Project)'
        }
        
        params = {
            'format': 'json',
            'limit': 1
        }

        if structured_query:
            # Mapeo de campos internos a campos de Nominatim
            # Internal: calle, numero, cp, ciudad, provincia
            # API: street, postalcode, city, state, country
            
            # Construir street con calle y numero
            calle = structured_query.get('calle', '')
            num = structured_query.get('numero', '')
            street_val = f"{num} {calle}".strip() if num else calle
            
            if street_val: params['street'] = street_val
            if structured_query.get('ciudad'): params['city'] = structured_query.get('ciudad')
            if structured_query.get('cp'): params['postalcode'] = structured_query.get('cp')
            if structured_query.get('provincia'): params['state'] = structured_query.get('provincia')
            params['country'] = 'Spain' # Asumimos ámbito nacional para mejorar precisión
        else:
            if not address: return None
            params['q'] = address
        
        try:
            response = requests.get(self.BASE_URL, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            return None
            
        except Exception as e:
            print(f"[GeocodingService] Error al geocodificar: {e}")
            return None
