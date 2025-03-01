"""
Extraktionsknoten für Sendungsdaten.

Diese Datei enthält die Extraktionsknoten für Sendungsdaten.
"""
import os
import json

try:
    from trustcall import create_extractor
except ImportError:
    # Fallback auf Mock-Version
    from app.utils.mock_trustcall import create_extractor

from app.schemas.shipment_schemas import (
    ShipmentItemBasics,
    ShipmentItemDimensions,
    ShipmentNotes,
)
from app.utils.model_setup import get_anthropic_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

# Lade Prompt-Templates
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

with open(os.path.join(prompt_dir, "shipment-item-basics-prompt.md"), "r", encoding="utf-8") as f:
    shipment_basics_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    shipment_basics_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "shipment-item-dimensions-prompt.md"), "r", encoding="utf-8") as f:
    shipment_dimensions_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    shipment_dimensions_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

with open(os.path.join(prompt_dir, "general-shipment-notes-prompt.md"), "r", encoding="utf-8") as f:
    shipment_notes_prompt_text = f.read()
    # Füge Optimierungsanweisungen hinzu
    shipment_notes_prompt_text += """
# Task
Extract ONLY the requested fields - no explanations or additional text.

# Output format
Return ONLY the structured data in JSON format. Do not include any reasoning or explanations.
"""

# Basis-LLM-Konfiguration mit API-Key 2
base_llm = get_anthropic_llm(
    model="claude-3-7-sonnet-20250219",
    temperature=0,
    key_index=2  # Verwendet ANTHROPIC_API_KEY_2
)

# Erstelle LLMs mit spezifischen Systemnachrichten
llm_basics = base_llm.with_config({"default_system_message": shipment_basics_prompt_text})
llm_dimensions = base_llm.with_config({"default_system_message": shipment_dimensions_prompt_text})
llm_notes = base_llm.with_config({"default_system_message": shipment_notes_prompt_text})

# Erstelle Extraktoren mit den spezifischen LLMs und den entsprechenden Tools
shipment_basics_extractor = create_extractor(
    llm_basics,
    tools=[ShipmentItemBasics],
    tool_choice="ShipmentItemBasics"
)

shipment_dimensions_extractor = create_extractor(
    llm_dimensions,
    tools=[ShipmentItemDimensions],
    tool_choice="ShipmentItemDimensions"
)

shipment_notes_extractor = create_extractor(
    llm_notes,
    tools=[ShipmentNotes],
    tool_choice="ShipmentNotes"
)

# Konfiguriere max_attempts für jeden Extraktor
def extract_shipment_basics(state):
    """Extract shipment basic information."""
    result = shipment_basics_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"shipment_basics": [result["responses"][0].model_dump()]}

def extract_shipment_dimensions(state):
    """Extract shipment dimensions information."""
    result = shipment_dimensions_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"shipment_dimensions": [result["responses"][0].model_dump()]}

def extract_shipment_notes(state):
    """Extract shipment notes information."""
    result = shipment_notes_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Begrenze Retries auf 2
    )
    return {"shipment_notes": result["responses"][0].model_dump()} 