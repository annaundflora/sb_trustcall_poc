"""
Combined schema for the complete shipment booking.
"""
from pydantic import BaseModel
from typing import Optional

from app.schemas.pickup_address_schema import PickupAddress
from app.schemas.delivery_address_schema import DeliveryAddress
from app.schemas.billing_address_schema import BillingAddress
from app.schemas.shipment_schema import Shipment


class ShipmentBooking(BaseModel):
    """Complete shipment booking information."""
    
    pickup_address: PickupAddress
    delivery_address: DeliveryAddress
    billing_address: BillingAddress
    shipment: Shipment 