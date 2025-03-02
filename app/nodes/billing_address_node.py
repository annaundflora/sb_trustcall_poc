"""
Extraction node for billing addresses.

This file contains the extraction node for billing addresses.
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback to mock version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.billing_address_schema import BillingAddress
from app.utils.model_setup import get_anthropic_llm

# Load prompt template
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "billing_address_system_prompt.md"), "r", encoding="utf-8") as f:
    billing_address_prompt_text = f.read()
    # Add optimization instructions
    billing_address_prompt_text += """
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
llm_billing = base_llm.with_config({"default_system_message": billing_address_prompt_text})

# Create extractor with the specific LLM and corresponding tool
billing_address_extractor = create_extractor(
    llm_billing,
    tools=[BillingAddress],
    tool_choice="BillingAddress"
)

def extract_billing_address(state):
    """Extract complete billing address information."""
    result = billing_address_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    return {"billing_address": result["responses"][0].model_dump()} 