"""
Nodes for extracting billing address information.
"""
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from trustcall import create_extractor
from app.schemas.address_schemas import (
    BillingAddressBasis,
    BillingAddressLocation,
    BillingAddressCommunication
)

# Set up path to prompt files
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

# Read prompt templates from files
with open(os.path.join(prompt_dir, "billing-address-basis-prompt.md"), "r", encoding="utf-8") as f:
    BILLING_BASIS_PROMPT = f.read()
    # Add optimization instructions
    BILLING_BASIS_PROMPT += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "billing-address-location-prompt.md"), "r", encoding="utf-8") as f:
    BILLING_LOCATION_PROMPT = f.read()
    # Add optimization instructions
    BILLING_LOCATION_PROMPT += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "billing-address-communication-prompt.md"), "r", encoding="utf-8") as f:
    BILLING_COMMUNICATION_PROMPT = f.read()
    # Add optimization instructions
    BILLING_COMMUNICATION_PROMPT += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "billing-address-detection-prompt.md"), "r", encoding="utf-8") as f:
    BILLING_DETECTION_PROMPT = f.read()
    # Add optimization instructions
    BILLING_DETECTION_PROMPT += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""


# Initialize the base LLM
base_llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0,  # Ensures deterministic and concise responses
    max_tokens=1000,  # Reduced token limit for more efficient responses
    timeout=10,
    cache=True  # Enable caching for better performance
)

# Create LLMs with specific system messages
llm_basis = base_llm.with_config({"default_system_message": BILLING_BASIS_PROMPT})
llm_location = base_llm.with_config({"default_system_message": BILLING_LOCATION_PROMPT})
llm_comm = base_llm.with_config({"default_system_message": BILLING_COMMUNICATION_PROMPT})

# Create billing address basis extractor
billing_basis_extractor = create_extractor(
    llm_basis,
    tools=[BillingAddressBasis],
    tool_choice="BillingAddressBasis"
)

# Create billing address location extractor
billing_location_extractor = create_extractor(
    llm_location,
    tools=[BillingAddressLocation],
    tool_choice="BillingAddressLocation"
)

# Create billing address communication extractor
billing_comm_extractor = create_extractor(
    llm_comm,
    tools=[BillingAddressCommunication],
    tool_choice="BillingAddressCommunication"
)

# Configure max_attempts for each extractor
def extract_billing_basis(state):
    """Extract billing address basic information."""
    result = billing_basis_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    return {"billing_basis": result["responses"][0].model_dump()}

def extract_billing_location(state):
    """Extract billing address location information."""
    result = billing_location_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    return {"billing_location": result["responses"][0].model_dump()}

def extract_billing_communication(state):
    """Extract billing address communication information."""
    result = billing_comm_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    return {"billing_communication": result["responses"][0].model_dump()} 