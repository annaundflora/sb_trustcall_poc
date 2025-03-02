"""
Schema definitions for the ShipmentBot application.
"""

from app.schemas.shipment_booking_schema import (
    PickupAddress,
    DeliveryAddress,
    BillingAddress,
    ShipmentItem,
    ShipmentInfo as Shipment,
    ShipmentBooking
)

__all__ = [
    "PickupAddress",
    "DeliveryAddress",
    "BillingAddress",
    "Shipment",
    "ShipmentItem",
    "ShipmentBooking",
]