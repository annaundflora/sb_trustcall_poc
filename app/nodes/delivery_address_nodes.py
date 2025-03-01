"""
Extraktionsknoten für Lieferadressen.

Diese Datei enthält die Extraktionsknoten für Lieferadressen.
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback auf Mock-Version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.address_schemas import (
    DeliveryAddressBasis,
    DeliveryAddressLocation,
    DeliveryAddressTime,
    DeliveryAddressCommunication,
)
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

# Lade Prompt-Templates
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "delivery-address-basis-prompt.md"), "r", encoding="utf-8") as f:
    delivery_basis_prompt_text = f.read()

with open(os.path.join(prompt_dir, "delivery-address-location-prompt.md"), "r", encoding="utf-8") as f:
    delivery_location_prompt_text = f.read()

with open(os.path.join(prompt_dir, "delivery-address-time-prompt.md"), "r", encoding="utf-8") as f:
    delivery_time_prompt_text = f.read()

with open(os.path.join(prompt_dir, "delivery-address-communication-prompt.md"), "r", encoding="utf-8") as f:
    delivery_communication_prompt_text = f.read()

# Basis-LLM-Konfiguration
base_llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0,
    max_tokens=4096,
    timeout=10,
    cache=True  # Aktiviere Caching für bessere Performance
)

# Erstelle LLMs mit spezifischen Systemnachrichten
llm_basis = base_llm.with_config({"default_system_message": delivery_basis_prompt_text})
llm_location = base_llm.with_config({"default_system_message": delivery_location_prompt_text})
llm_time = base_llm.with_config({"default_system_message": delivery_time_prompt_text})
llm_comm = base_llm.with_config({"default_system_message": delivery_communication_prompt_text})

# Erstelle Extraktoren mit den spezifischen LLMs und den entsprechenden Tools
delivery_basis_extractor = create_extractor(
    llm_basis,
    tools=[DeliveryAddressBasis],
    tool_choice="DeliveryAddressBasis"
)

delivery_location_extractor = create_extractor(
    llm_location,
    tools=[DeliveryAddressLocation],
    tool_choice="DeliveryAddressLocation"
)

delivery_time_extractor = create_extractor(
    llm_time,
    tools=[DeliveryAddressTime],
    tool_choice="DeliveryAddressTime"
)

delivery_comm_extractor = create_extractor(
    llm_comm,
    tools=[DeliveryAddressCommunication],
    tool_choice="DeliveryAddressCommunication"
)

# Konfiguriere max_attempts für jeden Extraktor
def extract_delivery_basis(state):
    """Extract delivery address basic information."""
    result = delivery_basis_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"delivery_basis": result["responses"][0].model_dump()}

def extract_delivery_location(state):
    """Extract delivery address location information."""
    result = delivery_location_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"delivery_location": result["responses"][0].model_dump()}

def extract_delivery_time(state):
    """Extract delivery address time information."""
    result = delivery_time_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"delivery_time": result["responses"][0].model_dump()}

def extract_delivery_communication(state):
    """Extract delivery address communication information."""
    result = delivery_comm_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"delivery_communication": result["responses"][0].model_dump()} 