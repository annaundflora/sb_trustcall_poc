from enum import IntEnum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator

class LoadCarrierType(IntEnum):
    PALLET = 1
    PACKAGE = 2
    EURO_PALLET_CAGE = 3
    DOCUMENT = 4
    OTHER = 5

# Base address class for common address fields
class AddressBase(BaseModel):
    """Base address information shared by all address types."""
    
    # FIELD GROUP 1: Basic Location Information
    company: Optional[str] = Field(None, description="Company name")
    first_name: Optional[str] = Field(None, description="First name of contact person")
    last_name: Optional[str] = Field(None, description="Last name of contact person")
    
    # FIELD GROUP 2: Location Information
    street: Optional[str] = Field(None, description="Street name and house/building number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: Optional[str] = Field(None, description="Postal code / ZIP code in the local format")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country code (ISO 2-letter code)")
    
    # FIELD GROUP 3: Communication Information
    phone: Optional[str] = Field(None, description="Phone number for contact")
    email: Optional[str] = Field(None, description="Email address for contact")

class PickupAddress(AddressBase):
    """Pickup address information with pickup-specific details."""
    pickup_reference: Optional[str] = Field(None, description="Reference number or code for pickup")
    pickup_date: Optional[str] = Field(None, description="Pickup date in format DD.MM.YYYY")
    pickup_time_from: Optional[str] = Field(None, description="Start of pickup time window (HH:MM)")
    pickup_time_to: Optional[str] = Field(None, description="End of pickup time window (HH:MM)")
    pickup_notes: Optional[str] = Field(None, description="Special instructions for pickup location, access, or loading")

class DeliveryAddress(AddressBase):
    """Delivery address information with delivery-specific details."""
    delivery_reference: Optional[str] = Field(None, description="Reference number or code for delivery")
    delivery_date: Optional[str] = Field(None, description="Delivery date in format DD.MM.YYYY")
    delivery_time_from: Optional[str] = Field(None, description="Start of delivery time window (HH:MM)")
    delivery_time_to: Optional[str] = Field(None, description="End of delivery time window (HH:MM)")
    delivery_notes: Optional[str] = Field(None, description="Special instructions for delivery location, access, or unloading")

class BillingAddress(AddressBase):
    """Billing address information with billing-specific details."""
    salutation: Optional[str] = Field(None, description="Salutation for contact person (Mr., Mrs., etc.)")
    billing_email: Optional[str] = Field(None, description="Email address specifically for billing/invoices")
    reference: Optional[str] = Field(None, description="Reference number or code for billing")
    vat_id: Optional[str] = Field(None, description="VAT ID / tax identification number")

class ShipmentItem(BaseModel):
    """Information about a single shipment item with all necessary details."""
    
    # FIELD GROUP 1: Basic Information
    load_carrier: Optional[LoadCarrierType] = Field(None, description="Type of load carrier (1=pallet, 2=package, 3=euro pallet cage, 4=document, 5=other)")
    name: Optional[str] = Field(None, description="Description of the goods being shipped")
    quantity: Optional[int] = Field(None, description="Number of pieces of this item type")
    
    # FIELD GROUP 2: Dimensions
    length: Optional[int] = Field(None, description="Length in cm")
    width: Optional[int] = Field(None, description="Width in cm")
    height: Optional[int] = Field(None, description="Height in cm")
    weight: Optional[int] = Field(None, description="Weight in kg")
    
    # FIELD GROUP 3: Handling
    stackable: Optional[bool] = Field(None, description="Whether the items can be stacked")

class ShipmentInfo(BaseModel):
    """Shipment-specific information including items and notes."""
    items: Optional[List[ShipmentItem]] = Field(default_factory=list, description="List of items in the shipment")
    shipment_notes: Optional[str] = Field(None, description="Only very specific notes about the shipment and goods, which are not covered by the other fields.")

class ShipmentBooking(BaseModel):
    """Complete shipment booking with all addresses and shipment details."""
    pickup_address: PickupAddress = Field(default_factory=PickupAddress, description="Address information for pickup location")
    delivery_address: DeliveryAddress = Field(default_factory=DeliveryAddress, description="Address information for delivery location")
    billing_address: BillingAddress = Field(default_factory=BillingAddress, description="Address information for billing")
    shipment: ShipmentInfo = Field(default_factory=ShipmentInfo, description="Information about the shipment and items") 