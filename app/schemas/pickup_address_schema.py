from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
from datetime import datetime

class PickupAddress(BaseModel):
    """Pickup address information with all necessary details."""
    
    # FIELD GROUP 1: Company and Contact Information
    company: Optional[str] = Field(None, description="Company name at the pickup location")
    first_name: Optional[str] = Field(None, description="First name of contact person at pickup")
    last_name: Optional[str] = Field(None, description="Last name of contact person at pickup")
    
    # FIELD GROUP 2: Location Information
    street: Optional[str] = Field(None, description="Street name and house/building number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: Optional[str] = Field(None, description="Postal code / ZIP code in the local format")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country code (ISO 2-letter code)")
    
    # FIELD GROUP 3: Communication Information
    phone: Optional[str] = Field(None, description="Phone number for pickup contact")
    email: Optional[str] = Field(None, description="Email address for pickup contact")
    pickup_reference: Optional[str] = Field(None, description="Reference number or code for pickup")
    
    # FIELD GROUP 4: Time Information
    pickup_date: Optional[str] = Field(None, description="Pickup date in format DD.MM.YYYY")
    pickup_time_from: Optional[str] = Field(None, description="Start of pickup time window (HH:MM)")
    pickup_time_to: Optional[str] = Field(None, description="End of pickup time window (HH:MM)")
    
    # FIELD GROUP 5: Additional Notes
    pickup_notes: Optional[str] = Field(None, description="Special instructions for pickup location, access, or loading")
