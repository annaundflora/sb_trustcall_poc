"""
Nodes for extracting shipment item information.
"""
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from trustcall import create_extractor
from app.schemas.shipment_schemas import (
    ShipmentItemBasics,
    ShipmentItemDimensions,
    ShipmentNotes
)

# Set up path to prompt files
current_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(current_dir, "..", "..", "instructions")

# Read prompt templates from files
with open(os.path.join(prompt_dir, "shipment-item-basics-prompt.md"), "r", encoding="utf-8") as f:
    SHIPMENT_BASICS_PROMPT = f.read()

with open(os.path.join(prompt_dir, "shipment-item-dimensions-prompt.md"), "r", encoding="utf-8") as f:
    SHIPMENT_DIMENSIONS_PROMPT = f.read()

with open(os.path.join(prompt_dir, "general-shipment-notes-prompt.md"), "r", encoding="utf-8") as f:
    SHIPMENT_NOTES_PROMPT = f.read()

with open(os.path.join(prompt_dir, "shipment-item-recognition-prompt.md"), "r", encoding="utf-8") as f:
    SHIPMENT_RECOGNITION_PROMPT = f.read()


# Initialize the base LLM
base_llm = ChatAnthropic(
    model="claude-3-7-sonnet-20250219",
    temperature=0,
    max_tokens=4096,
    timeout=10,
    cache=True  # Enable caching for better performance
)

# Create LLMs with specific system messages
llm_basics = base_llm.with_config({"default_system_message": SHIPMENT_BASICS_PROMPT})
llm_dimensions = base_llm.with_config({"default_system_message": SHIPMENT_DIMENSIONS_PROMPT})
llm_notes = base_llm.with_config({"default_system_message": SHIPMENT_NOTES_PROMPT})

# Create shipment item basics extractor
shipment_basics_extractor = create_extractor(
    llm_basics,
    tools=[ShipmentItemBasics],
    tool_choice="ShipmentItemBasics"
)

# Create shipment item dimensions extractor
shipment_dimensions_extractor = create_extractor(
    llm_dimensions,
    tools=[ShipmentItemDimensions],
    tool_choice="ShipmentItemDimensions"
)

# Create shipment notes extractor
shipment_notes_extractor = create_extractor(
    llm_notes,
    tools=[ShipmentNotes],
    tool_choice="ShipmentNotes"
)

# Configure max_attempts for each extractor
def extract_shipment_basics(state):
    """Extract shipment item basic information."""
    result = shipment_basics_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    # This can return multiple items, so we wrap in a list
    return {"shipment_basics": [result["responses"][0].model_dump()]}

def extract_shipment_dimensions(state):
    """Extract shipment item dimensions information."""
    result = shipment_dimensions_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    # This can return multiple items, so we wrap in a list
    return {"shipment_dimensions": [result["responses"][0].model_dump()]}

def extract_shipment_notes(state):
    """Extract shipment notes information."""
    result = shipment_notes_extractor.invoke(
        state["input"],
        config={"configurable": {"max_attempts": 2}}  # Limit retries to 2
    )
    return {"shipment_notes": result["responses"][0].model_dump()} 