from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re
from datetime import datetime

class DeliveryAddress(BaseModel):
    """Delivery address information with all necessary details."""
    
    # FIELD GROUP 1: Company and Contact Information
    company: Optional[str] = Field(None, description="Company name at the delivery location")
    first_name: Optional[str] = Field(None, description="First name of contact person at delivery")
    last_name: Optional[str] = Field(None, description="Last name of contact person at delivery")
    
    # FIELD GROUP 2: Location Information
    street: Optional[str] = Field(None, description="Street name and house/building number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: Optional[str] = Field(None, description="Postal code / ZIP code in the local format")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country code (ISO 2-letter code)")
    
    # FIELD GROUP 3: Communication Information
    phone: Optional[str] = Field(None, description="Phone number for delivery contact")
    email: Optional[str] = Field(None, description="Email address for delivery contact")
    delivery_reference: Optional[str] = Field(None, description="Reference number or code for delivery")
    
    # FIELD GROUP 4: Time Information
    delivery_date: Optional[str] = Field(None, description="Delivery date in format DD.MM.YYYY")
    delivery_time_from: Optional[str] = Field(None, description="Start of delivery time window (HH:MM)")
    delivery_time_to: Optional[str] = Field(None, description="End of delivery time window (HH:MM)")
    
    # FIELD GROUP 5: Additional Notes
    delivery_notes: Optional[str] = Field(None, description="Special instructions for delivery location, access, or unloading")
    
    # Validators
    @field_validator('delivery_date')
    def validate_delivery_date(cls, v):
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
                    raise ValueError("Delivery date should be in DD.MM.YYYY format")
        return v
    
    @field_validator('delivery_time_from', 'delivery_time_to')
    def validate_delivery_time(cls, v):
        if v:
            try:
                datetime.strptime(v, '%H:%M')
            except ValueError:
                raise ValueError("Delivery time must be in HH:MM format")
        return v