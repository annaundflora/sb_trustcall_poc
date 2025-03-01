"""
Combined schema for complete shipment bookings.
"""
from pydantic import BaseModel, Field
from app.schemas.address_schemas import PickupAddress, DeliveryAddress, BillingAddress
from app.schemas.shipment_schemas import Shipment


class ShipmentBooking(BaseModel):
    """Complete shipment booking schema."""
    pickup_address: PickupAddress = Field(description="Pickup address details")
    delivery_address: DeliveryAddress = Field(description="Delivery address details")
    billing_address: BillingAddress = Field(description="Billing address details")
    shipment: Shipment = Field(description="Shipment details including items") 