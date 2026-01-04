from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    COURIER = "COURIER"
    CUSTOMER = "CUSTOMER"

class ShipmentStatus(str, Enum):
    PENDING = "REGISTRADO"
    ASSIGNED = "ASIGNADO"
    EN_ROUTE = "EN_REPARTO"
    DELIVERED = "ENTREGADO"
    INCIDENT = "INCIDENCIA"

    