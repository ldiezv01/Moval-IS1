import random
import string
from datetime import datetime

class CreateShipment:
    def __init__(self, shipment_repo, user_repo, geocoding_service):
        self.shipment_repo = shipment_repo
        self.user_repo = user_repo
        self.geocoding_service = geocoding_service

    def execute(self, actor_user: dict, shipment_data: dict) -> int:
        """
        Crea un nuevo paquete.
        actor_user: Usuario que realiza la acción (debe ser ADMIN).
        shipment_data: Diccionario con descripcion, peso, origen, destino, id_cliente.
        """
        # 1. Seguridad
        if actor_user.get('role') != 'ADMIN':
            raise PermissionError("Solo los administradores pueden registrar paquetes manualmente.")

        # 2. Validación Básica
        required = ['descripcion', 'peso', 'direccion_origen', 'direccion_destino', 'id_cliente']
        for field in required:
            if field not in shipment_data or not shipment_data[field]:
                raise ValueError(f"El campo '{field}' es obligatorio.")

        try:
            peso = float(shipment_data['peso'])
            if peso <= 0: raise ValueError
        except:
            raise ValueError("El peso debe ser un número positivo.")

        # 3. Validar Cliente
        cliente = self.user_repo.get(shipment_data['id_cliente'])
        if not cliente:
            raise ValueError("El cliente seleccionado no existe.")

        # 4. Geocodificación (Validación de Dirección)
        # Preparar datos estructurados si están disponibles
        structured = None
        if 'calle' in shipment_data:
            structured = {
                'calle': shipment_data.get('calle'),
                'numero': shipment_data.get('numero'),
                'cp': shipment_data.get('cp'),
                'ciudad': shipment_data.get('ciudad'),
                'provincia': shipment_data.get('provincia')
            }

        coords = self.geocoding_service.geocode_address(shipment_data['direccion_destino'], structured_query=structured)
        if not coords:
            raise ValueError(f"No se pudo validar la dirección: {shipment_data['direccion_destino']}. Verifique calle, número y ciudad.")
        
        lat, lon = coords

        # 5. Generar Código de Seguimiento Único
        # Formato: PKG-YYYYMMDD-XXXX
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        date_str = datetime.now().strftime("%Y%m%d")
        tracking_code = f"PKG-{date_str}-{suffix}"

        # 6. Guardar
        new_shipment = {
            'codigo_seguimiento': tracking_code,
            'descripcion': shipment_data['descripcion'],
            'peso': peso,
            'direccion_origen': shipment_data['direccion_origen'],
            'direccion_destino': shipment_data['direccion_destino'],
            'latitud': lat,
            'longitud': lon,
            'id_cliente': int(shipment_data['id_cliente'])
        }

        return self.shipment_repo.create(new_shipment)
