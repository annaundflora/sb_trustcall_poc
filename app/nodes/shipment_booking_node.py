"""
Combined extraction node for complete shipment bookings.

This file contains a single extraction node that handles all aspects of a shipment booking:
- Pickup address
- Delivery address
- Billing address
- Shipment information
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback to mock version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.shipment_booking_schema import ShipmentBooking
from app.utils.model_setup import get_anthropic_llm

# Load prompt template
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "shipment_booking_system_prompt.md"), "r", encoding="utf-8") as f:
    shipment_booking_prompt_text = f.read()

# Base LLM configuration with API key 2 (using the more powerful key for the combined extraction)
base_llm = get_anthropic_llm(
    model="claude-3-7-sonnet-20250219",
    temperature=0,
    key_index=2  # Using API key 2 for the combined extraction
)

# Create LLM with specific system message
llm_booking = base_llm.with_config({"default_system_message": shipment_booking_prompt_text})

# Create extractor with the specific LLM and corresponding tool
shipment_booking_extractor = create_extractor(
    llm_booking,
    tools=[ShipmentBooking],
    tool_choice="ShipmentBooking"
)

def extract_shipment_booking(state):
    """Extract complete shipment booking information in a single call."""
    result = shipment_booking_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Allow up to 2 retries
    )
    
    # Get the model data and standardize unknown values
    booking_data = result["responses"][0].model_dump()
    
    # Extract each component to return in the format expected by the workflow
    pickup_address = booking_data.get("pickup_address", {})
    delivery_address = booking_data.get("delivery_address", {})
    billing_address = booking_data.get("billing_address", {})
    shipment = booking_data.get("shipment", {"items": []})
    
    # Return all components in the structure expected by the workflow
    return {
        "pickup_address": pickup_address,
        "delivery_address": delivery_address,
        "billing_address": billing_address,
        "shipment": shipment
    } 