"""
Extraktionsknoten für Abholadressen.

Diese Datei enthält die Extraktionsknoten für Abholadressen.
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback auf Mock-Version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.address_schemas import (
    PickupAddressBasis,
    PickupAddressLocation,
    PickupAddressTime,
    PickupAddressCommunication,
)
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

# Lade Prompt-Templates
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "pickup-address-basis-prompt.md"), "r", encoding="utf-8") as f:
    pickup_basis_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    pickup_basis_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "pickup-address-location-prompt.md"), "r", encoding="utf-8") as f:
    pickup_location_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    pickup_location_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "pickup-address-time-prompt.md"), "r", encoding="utf-8") as f:
    pickup_time_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    pickup_time_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "pickup-address-communication-prompt.md"), "r", encoding="utf-8") as f:
    pickup_communication_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    pickup_communication_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

# Basis-LLM-Konfiguration
base_llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0,  # Stellt sicher, dass die Antworten deterministisch und knapp sind
    max_tokens=1000,  # Reduziertes Token-Limit für effizientere Antworten
    timeout=10,
    cache=True  # Aktiviere Caching für bessere Performance
)

# Erstelle LLMs mit spezifischen Systemnachrichten
llm_basis = base_llm.with_config({"default_system_message": pickup_basis_prompt_text})
llm_location = base_llm.with_config({"default_system_message": pickup_location_prompt_text})
llm_time = base_llm.with_config({"default_system_message": pickup_time_prompt_text})
llm_comm = base_llm.with_config({"default_system_message": pickup_communication_prompt_text})

# Erstelle Extraktoren mit den spezifischen LLMs und den entsprechenden Tools
pickup_basis_extractor = create_extractor(
    llm_basis,
    tools=[PickupAddressBasis],
    tool_choice="PickupAddressBasis"
)

pickup_location_extractor = create_extractor(
    llm_location,
    tools=[PickupAddressLocation],
    tool_choice="PickupAddressLocation"
)

pickup_time_extractor = create_extractor(
    llm_time,
    tools=[PickupAddressTime],
    tool_choice="PickupAddressTime"
)

pickup_comm_extractor = create_extractor(
    llm_comm,
    tools=[PickupAddressCommunication],
    tool_choice="PickupAddressCommunication"
)

# Konfiguriere max_attempts für jeden Extraktor
def extract_pickup_basis(state):
    """Extract pickup address basic information."""
    result = pickup_basis_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"pickup_basis": result["responses"][0].model_dump()}

def extract_pickup_location(state):
    """Extract pickup address location information."""
    result = pickup_location_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"pickup_location": result["responses"][0].model_dump()}

def extract_pickup_time(state):
    """Extract pickup address time information."""
    result = pickup_time_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"pickup_time": result["responses"][0].model_dump()}

def extract_pickup_communication(state):
    """Extract pickup address communication information."""
    result = pickup_comm_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"pickup_communication": result["responses"][0].model_dump()} 