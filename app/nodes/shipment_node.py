"""
Extraction node for shipment information.

This file contains the extraction node for shipment information.
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback to mock version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.shipment_schema import Shipment, ShipmentItem
from app.utils.model_setup import get_anthropic_llm

# Load prompt template
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "shipment_system_prompt.md"), "r", encoding="utf-8") as f:
    shipment_prompt_text = f.read()
    # Add optimization instructions
    shipment_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

# Base LLM configuration with API key 2
base_llm = get_anthropic_llm(
    model="claude-3-7-sonnet-20250219",
    temperature=0,
    key_index=2  # API key 2 for group 2
)

# Create LLM with specific system message
llm_shipment = base_llm.with_config({"default_system_message": shipment_prompt_text})

# Create extractor with the specific LLM and corresponding tool
shipment_extractor = create_extractor(
    llm_shipment,
    tools=[Shipment],
    tool_choice="Shipment"
)

def extract_shipment(state):
    """Extract complete shipment information."""
    result = shipment_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    return {"shipment": result["responses"][0].model_dump()} 