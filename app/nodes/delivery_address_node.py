"""
Extraction node for delivery addresses.

This file contains the extraction node for delivery addresses.
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback to mock version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.delivery_address_schema import DeliveryAddress
from app.utils.model_setup import get_anthropic_llm

# Load prompt template
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "delivery_address_system_prompt.md"), "r", encoding="utf-8") as f:
    delivery_address_prompt_text = f.read()
    # Add optimization instructions
    delivery_address_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

# Base LLM configuration with API key 1
base_llm = get_anthropic_llm(
    model="claude-3-7-sonnet-20250219",
    temperature=0,
    key_index=1  # API key 1 for group 1
)

# Create LLM with specific system message
llm_delivery = base_llm.with_config({"default_system_message": delivery_address_prompt_text})

# Create extractor with the specific LLM and corresponding tool
delivery_address_extractor = create_extractor(
    llm_delivery,
    tools=[DeliveryAddress],
    tool_choice="DeliveryAddress"
)

def extract_delivery_address(state):
    """Extract complete delivery address information."""
    result = delivery_address_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    return {"delivery_address": result["responses"][0].model_dump()} 