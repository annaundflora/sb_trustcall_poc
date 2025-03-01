"""
Extraktionsknoten für Rechnungsadressen.

Diese Datei enthält die Extraktionsknoten für Rechnungsadressen.
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback auf Mock-Version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.address_schemas import (
    BillingAddressBasis,
    BillingAddressLocation,
    BillingAddressCommunication,
)
from app.utils.model_setup import get_anthropic_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

# Lade Prompt-Templates
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "billing-address-basis-prompt.md"), "r", encoding="utf-8") as f:
    billing_basis_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    billing_basis_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "billing-address-location-prompt.md"), "r", encoding="utf-8") as f:
    billing_location_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    billing_location_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "billing-address-communication-prompt.md"), "r", encoding="utf-8") as f:
    billing_communication_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    billing_communication_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

# Basis-LLM-Konfiguration mit API-Key 2
base_llm = get_anthropic_llm(
    model="claude-3-7-sonnet-20250219",
    temperature=0,
    key_index=2  # API-Key 2 für Gruppe 2
)

# Erstelle LLMs mit spezifischen Systemnachrichten
llm_basis = base_llm.with_config({"default_system_message": billing_basis_prompt_text})
llm_location = base_llm.with_config({"default_system_message": billing_location_prompt_text})
llm_comm = base_llm.with_config({"default_system_message": billing_communication_prompt_text})

# Erstelle Extraktoren mit den spezifischen LLMs und den entsprechenden Tools
billing_basis_extractor = create_extractor(
    llm_basis,
    tools=[BillingAddressBasis],
    tool_choice="BillingAddressBasis"
)

billing_location_extractor = create_extractor(
    llm_location,
    tools=[BillingAddressLocation],
    tool_choice="BillingAddressLocation"
)

billing_comm_extractor = create_extractor(
    llm_comm,
    tools=[BillingAddressCommunication],
    tool_choice="BillingAddressCommunication"
)

# Konfiguriere max_attempts für jeden Extraktor
def extract_billing_basis(state):
    """Extract billing address basic information."""
    result = billing_basis_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"billing_basis": result["responses"][0].model_dump()}

def extract_billing_location(state):
    """Extract billing address location information."""
    result = billing_location_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"billing_location": result["responses"][0].model_dump()}

def extract_billing_communication(state):
    """Extract billing address communication information."""
    result = billing_comm_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"billing_communication": result["responses"][0].model_dump()} 