from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

class BillingAddress(BaseModel):
    """Billing address information with all necessary details."""
    
    # FIELD GROUP 1: Company and Contact Information
    company: str = Field(description="Company name for billing")
    salutation: Optional[str] = Field(None, description="Salutation for contact person (Mr., Mrs., etc.)")
    first_name: Optional[str] = Field(None, description="First name of contact person for billing")
    last_name: Optional[str] = Field(None, description="Last name of contact person for billing")
    
    # FIELD GROUP 2: Location Information
    street: str = Field(description="Street name and house/building number")
    address_addition: Optional[str] = Field(None, description="Additional address information (building, floor, etc.)")
    postal_code: str = Field(description="Postal code / ZIP code in the local format")
    city: str = Field(description="City name")
    country: str = Field(description="Country code (ISO 2-letter code preferred)", default="DE")
    
    # FIELD GROUP 3: Communication and Financial Information
    phone: Optional[str] = Field(None, description="Phone number for billing contact")
    email: Optional[str] = Field(None, description="Email address for billing contact")
    billing_email: Optional[str] = Field(None, description="Email address specifically for billing/invoices")
    reference: Optional[str] = Field(None, description="Reference number or code for billing")
    vat_id: Optional[str] = Field(None, description="VAT ID / tax identification number")