from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    COURIER = "COURIER"
    CUSTOMER = "CUSTOMER"

class ShipmentStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    DELIVERED = "DELIVERED"
    INCIDENT = "INCIDENT"

    