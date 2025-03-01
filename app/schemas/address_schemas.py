"""
Address schemas for the ShipmentBot application.
"""
from pydantic import BaseModel, Field
from typing import Optional


class PickupAddressBasis(BaseModel):
    """Basic information for pickup address."""
    company: str = Field(description="Company name at pickup address")
    first_name: Optional[str] = Field(None, description="First name of contact person at pickup")
    last_name: Optional[str] = Field(None, description="Last name of contact person at pickup")


class PickupAddressLocation(BaseModel):
    """Location information for pickup address."""
    street: str = Field(description="Street name and number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)")


class PickupAddressTime(BaseModel):
    """Time window information for pickup."""
    pickup_date: str = Field(description="Pickup date in format YYYY-MM-DD")
    pickup_time_from: Optional[str] = Field(None, description="Start of pickup time window (HH:MM)")
    pickup_time_to: Optional[str] = Field(None, description="End of pickup time window (HH:MM)")


class PickupAddressCommunication(BaseModel):
    """Communication information for pickup address."""
    phone: Optional[str] = Field(None, description="Phone number for pickup contact")
    email: Optional[str] = Field(None, description="Email address for pickup contact")
    pickup_reference: Optional[str] = Field(None, description="Reference number or code for pickup")


class DeliveryAddressBasis(BaseModel):
    """Basic information for delivery address."""
    company: str = Field(description="Company name at delivery address")
    first_name: Optional[str] = Field(None, description="First name of contact person at delivery")
    last_name: Optional[str] = Field(None, description="Last name of contact person at delivery")


class DeliveryAddressLocation(BaseModel):
    """Location information for delivery address."""
    street: str = Field(description="Street name and number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)")


class DeliveryAddressTime(BaseModel):
    """Time window information for delivery."""
    delivery_date: str = Field(description="Delivery date in format YYYY-MM-DD")
    delivery_time_from: Optional[str] = Field(None, description="Start of delivery time window (HH:MM)")
    delivery_time_to: Optional[str] = Field(None, description="End of delivery time window (HH:MM)")


class DeliveryAddressCommunication(BaseModel):
    """Communication information for delivery address."""
    phone: Optional[str] = Field(None, description="Phone number for delivery contact")
    email: Optional[str] = Field(None, description="Email address for delivery contact")
    delivery_reference: Optional[str] = Field(None, description="Reference number or code for delivery")


class BillingAddressBasis(BaseModel):
    """Basic information for billing address."""
    company: str = Field(description="Company name for billing")
    salutation: Optional[str] = Field(None, description="Salutation for contact person (Mr., Mrs., etc.)")
    first_name: Optional[str] = Field(None, description="First name of contact person for billing")
    last_name: Optional[str] = Field(None, description="Last name of contact person for billing")


class BillingAddressLocation(BaseModel):
    """Location information for billing address."""
    street: str = Field(description="Street name and number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)")


class BillingAddressCommunication(BaseModel):
    """Communication information for billing address."""
    phone: Optional[str] = Field(None, description="Phone number for billing contact")
    email: Optional[str] = Field(None, description="Email address for billing contact")
    billing_email: Optional[str] = Field(None, description="Email address specifically for billing/invoices")
    reference: Optional[str] = Field(None, description="Reference number or code for billing")
    vat_id: Optional[str] = Field(None, description="VAT ID / tax identification number")


class PickupAddress(BaseModel):
    """Complete pickup address schema."""
    company: str = Field(description="Company name at pickup address")
    first_name: Optional[str] = Field(None, description="First name of contact person at pickup")
    last_name: Optional[str] = Field(None, description="Last name of contact person at pickup")
    street: str = Field(description="Street name and number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)")
    phone: Optional[str] = Field(None, description="Phone number for pickup contact")
    email: Optional[str] = Field(None, description="Email address for pickup contact")
    pickup_reference: Optional[str] = Field(None, description="Reference number or code for pickup")
    pickup_date: str = Field(description="Pickup date in format YYYY-MM-DD")
    pickup_time_from: Optional[str] = Field(None, description="Start of pickup time window (HH:MM)")
    pickup_time_to: Optional[str] = Field(None, description="End of pickup time window (HH:MM)")


class DeliveryAddress(BaseModel):
    """Complete delivery address schema."""
    company: str = Field(description="Company name at delivery address")
    first_name: Optional[str] = Field(None, description="First name of contact person at delivery")
    last_name: Optional[str] = Field(None, description="Last name of contact person at delivery")
    street: str = Field(description="Street name and number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)")
    phone: Optional[str] = Field(None, description="Phone number for delivery contact")
    email: Optional[str] = Field(None, description="Email address for delivery contact")
    delivery_reference: Optional[str] = Field(None, description="Reference number or code for delivery")
    delivery_date: str = Field(description="Delivery date in format YYYY-MM-DD")
    delivery_time_from: Optional[str] = Field(None, description="Start of delivery time window (HH:MM)")
    delivery_time_to: Optional[str] = Field(None, description="End of delivery time window (HH:MM)")


class BillingAddress(BaseModel):
    """Complete billing address schema."""
    company: str = Field(description="Company name for billing")
    salutation: Optional[str] = Field(None, description="Salutation for contact person (Mr., Mrs., etc.)")
    first_name: Optional[str] = Field(None, description="First name of contact person for billing")
    last_name: Optional[str] = Field(None, description="Last name of contact person for billing")
    street: str = Field(description="Street name and number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)")
    phone: Optional[str] = Field(None, description="Phone number for billing contact")
    email: Optional[str] = Field(None, description="Email address for billing contact")
    billing_email: Optional[str] = Field(None, description="Email address specifically for billing/invoices")
    reference: Optional[str] = Field(None, description="Reference number or code for billing")
    vat_id: Optional[str] = Field(None, description="VAT ID / tax identification number") 