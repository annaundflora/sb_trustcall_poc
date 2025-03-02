"""
Schema definitions for the ShipmentBot application.
"""

from app.schemas.pickup_address_schema import PickupAddress
from app.schemas.delivery_address_schema import DeliveryAddress
from app.schemas.billing_address_schema import BillingAddress
from app.schemas.shipment_schema import Shipment, ShipmentItem
from app.schemas.combined_schema import ShipmentBooking

__all__ = [
    "PickupAddress",
    "DeliveryAddress",
    "BillingAddress",
    "Shipment",
    "ShipmentItem",
    "ShipmentBooking",
] 