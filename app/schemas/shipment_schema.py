from enum import IntEnum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator

class LoadCarrierType(IntEnum):
    PALLET = 1
    PACKAGE = 2
    EURO_PALLET_CAGE = 3
    DOCUMENT = 4
    OTHER = 5

class ShipmentItem(BaseModel):
    """Information about a single shipment item with all necessary details."""
    
    # FIELD GROUP 1: Basic Information
    load_carrier: Optional[LoadCarrierType] = Field(None, description="Type of load carrier (1=pallet, 2=package, 3=euro pallet cage, 4=document, 5=other)")
    name: Optional[str] = Field(None, description="Description of the goods being shipped")
    quantity: Optional[int] = Field(None, description="Number of pieces of this item type")
    
    # FIELD GROUP 2: Dimensions
    length: Optional[float] = Field(None, description="Length in cm")
    width: Optional[float] = Field(None, description="Width in cm")
    height: Optional[float] = Field(None, description="Height in cm")
    weight: Optional[float] = Field(None, description="Weight in kg")
    
    # FIELD GROUP 3: Handling
    stackable: Optional[bool] = Field(None, description="Whether the items can be stacked")
    
    # Validators
    @field_validator('weight')
    def validate_weight(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Weight must be greater than 0")
        return v
    
    @field_validator('quantity')
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v
    
    @field_validator('length', 'width', 'height')
    def validate_dimensions(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Dimensions must be greater than 0")
        return v
    
    @model_validator(mode='after')
    def set_default_dimensions(self):
        # Set standard dimensions for pallets if not specified
        if self.load_carrier == LoadCarrierType.PALLET:
            # Euro pallet standard dimensions
            if self.length is None:
                self.length = 120.0
            if self.width is None:
                self.width = 80.0
        elif self.load_carrier == LoadCarrierType.DOCUMENT:
            # For documents, set dimensions to None
            self.length = None
            self.width = None
            self.height = None
            # Set default weight to 1kg if not specified or very light
            if self.weight is not None and self.weight < 0.1:
                self.weight = 1.0
        
        return self
    
    @model_validator(mode='after')
    def set_default_stackable(self):
        # If stackable wasn't explicitly set, determine based on load carrier
        if self.stackable is None and self.load_carrier is not None:
            if self.load_carrier == LoadCarrierType.PALLET:
                self.stackable = False  # Pallets are not stackable by default
            elif self.load_carrier == LoadCarrierType.PACKAGE:
                self.stackable = True   # Packages are stackable by default
            elif self.load_carrier == LoadCarrierType.EURO_PALLET_CAGE:
                self.stackable = True   # Euro pallet cages are stackable by default
            elif self.load_carrier == LoadCarrierType.DOCUMENT:
                self.stackable = True   # Documents are stackable by default
            else:  # OTHER
                self.stackable = False  # "Other" are not stackable by default
        
        return self


class Shipment(BaseModel):
    """Complete shipment information including items and notes."""
    
    # All items in the shipment
    items: Optional[List[ShipmentItem]] = Field(default_factory=list, description="List of items in the shipment")
    
    # Additional notes about the shipment
    general_notes: Optional[str] = Field(None, description="General notes about the shipment")