from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
from datetime import datetime

class PickupAddress(BaseModel):
    """Pickup address information with all necessary details."""
    
    # FIELD GROUP 1: Company and Contact Information
    company: str = Field(description="Company name at the pickup location")
    first_name: Optional[str] = Field(None, description="First name of contact person at pickup")
    last_name: Optional[str] = Field(None, description="Last name of contact person at pickup")
    
    # FIELD GROUP 2: Location Information
    street: str = Field(description="Street name and house/building number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code in the local format")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)", default="DE")
    
    # FIELD GROUP 3: Communication Information
    phone: Optional[str] = Field(None, description="Phone number for pickup contact")
    email: Optional[str] = Field(None, description="Email address for pickup contact")
    pickup_reference: Optional[str] = Field(None, description="Reference number or code for pickup")
    
    # FIELD GROUP 4: Time Information
    pickup_date: str = Field(description="Pickup date in format DD.MM.YYYY")
    pickup_time_from: Optional[str] = Field(None, description="Start of pickup time window (HH:MM)")
    pickup_time_to: Optional[str] = Field(None, description="End of pickup time window (HH:MM)")
    
    # FIELD GROUP 5: Additional Notes
    pickup_notes: Optional[str] = Field(None, description="Special instructions for pickup location, access, or loading")
    
    # Validators
    @field_validator('pickup_date')
    def validate_pickup_date(cls, v):
        if v:
            try:
                # Checking format DD.MM.YYYY
                datetime.strptime(v, '%d.%m.%Y')
            except ValueError:
                try:
                    # Try to accept other formats and convert them
                    from dateutil import parser
                    parsed_date = parser.parse(v)
                    return parsed_date.strftime('%d.%m.%Y')
                except:
                    raise ValueError("Pickup date should be in DD.MM.YYYY format")
        return v
    
    @field_validator('pickup_time_from', 'pickup_time_to')
    def validate_pickup_time(cls, v):
        if v:
            try:
                datetime.strptime(v, '%H:%M')
            except ValueError:
                raise ValueError("Pickup time must be in HH:MM format")
        return v