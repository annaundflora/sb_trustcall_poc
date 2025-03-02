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
