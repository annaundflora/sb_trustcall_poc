"""
Shipment schemas for the ShipmentBot application.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ShipmentItemBasics(BaseModel):
    """Basic information about a shipment item."""
    category: Literal["Pallet", "Package", "Cage", "Document", "Other"] = Field(
        description="Category of shipment item (Pallet, Package, Cage, Document, Other)"
    )
    description: str = Field(description="Description of the goods being shipped")
    quantity: int = Field(description="Number of pieces of this item type")
    stackable: bool = Field(description="Whether the items can be stacked")


class ShipmentItemDimensions(BaseModel):
    """Dimension information about a shipment item."""
    weight: float = Field(description="Weight in kg")
    length: Optional[float] = Field(None, description="Length in cm")
    width: Optional[float] = Field(None, description="Width in cm")
    height: Optional[float] = Field(None, description="Height in cm")


class ShipmentItem(BaseModel):
    """Complete shipment item schema."""
    category: Literal["Pallet", "Package", "Cage", "Document", "Other"] = Field(
        description="Category of shipment item (Pallet, Package, Cage, Document, Other)"
    )
    description: str = Field(description="Description of the goods being shipped")
    quantity: int = Field(description="Number of pieces of this item type")
    stackable: bool = Field(description="Whether the items can be stacked")
    weight: float = Field(description="Weight in kg")
    length: Optional[float] = Field(None, description="Length in cm")
    width: Optional[float] = Field(None, description="Width in cm")
    height: Optional[float] = Field(None, description="Height in cm")


class ShipmentNotes(BaseModel):
    """Notes and special instructions for the shipment."""
    general_notes: Optional[str] = Field(None, description="General notes about the shipment")
    pickup_notes: Optional[str] = Field(None, description="Special instructions for pickup")
    delivery_notes: Optional[str] = Field(None, description="Special instructions for delivery")


class Shipment(BaseModel):
    """Complete shipment schema with items."""
    items: List[ShipmentItem] = Field(description="List of items in the shipment")
    general_notes: Optional[str] = Field(None, description="General notes about the shipment")
    pickup_notes: Optional[str] = Field(None, description="Special instructions for pickup")
    delivery_notes: Optional[str] = Field(None, description="Special instructions for delivery") 