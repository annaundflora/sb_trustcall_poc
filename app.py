"""
ShipmentBot - Main Application Entry Point

A Streamlit application for extracting structured shipping data from unstructured text.
"""
import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"Projektverzeichnis zum Python-Pfad hinzugefügt: {current_dir}")

# Lade .env-Datei, bevor andere Importe erfolgen
load_dotenv()
# Wenn das nicht funktioniert, versuche es mit dem absoluten Pfad
if not os.environ.get("ANTHROPIC_API_KEY_1"):
    # Bestimme den Pfad zur .env-Datei relativ zum aktuellen Skript
    current_dir = Path(__file__).parent.absolute()
    env_path = current_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Umgebungsvariablen aus {env_path} geladen")
    else:
        print(f"WARNUNG: .env-Datei nicht gefunden unter {env_path}")
        # Liste alle verfügbaren Umgebungsvariablen auf, die mit ANTHROPIC beginnen
        anthropic_vars = [k for k in os.environ.keys() if k.startswith("ANTHROPIC")]
        print(f"Verfügbare Anthropic-Variablen: {anthropic_vars}")

import streamlit as st
from langsmith import Client
import traceback
from langchain_core.callbacks import BaseCallbackHandler

# Import ShipmentBot components
from app.utils.config import load_environment
from app.utils.workflow import build_shipment_graph

# Setup page configuration
st.set_page_config(
    page_title="ShipmentBot",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables and initialize cache
load_environment()

# Initialize LangSmith client for tracing
client = Client(
    api_key=os.environ.get("LANGSMITH_API_KEY"),
    api_url=os.environ.get("LANGSMITH_ENDPOINT")
)

# Build the extraction workflow
shipment_graph = build_shipment_graph()


def process_input(input_text):
    """
    Process input text through the ShipmentBot extraction workflow.
    
    Args:
        input_text (str): The input text to process
        
    Returns:
        dict: The extracted shipment data
    """
    # Set up the initial state
    state = {"input": input_text}
    
    # Execute the workflow with tracing
    try:
        with st.spinner("Daten werden extrahiert..."):
            with st.expander("Verarbeitungslog", expanded=False):
                progress = st.empty()
                
                # Erstelle einen benutzerdefinierten Callback-Handler
                class StreamlitCallbackHandler(BaseCallbackHandler):
                    """Callback-Handler für Streamlit-Fortschrittsanzeige."""
                    
                    def on_chain_start(self, serialized, inputs, **kwargs):
                        """Wird aufgerufen, wenn eine Chain startet."""
                        pass
                    
                    def on_chain_end(self, outputs, **kwargs):
                        """Wird aufgerufen, wenn eine Chain endet."""
                        pass
                    
                    def on_llm_start(self, serialized, prompts, **kwargs):
                        """Wird aufgerufen, wenn ein LLM startet."""
                        pass
                    
                    def on_llm_end(self, response, **kwargs):
                        """Wird aufgerufen, wenn ein LLM endet."""
                        pass
                    
                    def on_tool_start(self, serialized, input_str, **kwargs):
                        """Wird aufgerufen, wenn ein Tool startet."""
                        pass
                    
                    def on_tool_end(self, output, **kwargs):
                        """Wird aufgerufen, wenn ein Tool endet."""
                        pass
                    
                    def on_node_start(self, node_name, inputs, **kwargs):
                        """Wird aufgerufen, wenn ein Knoten startet."""
                        pass
                    
                    def on_node_end(self, node_name, outputs, **kwargs):
                        """Wird aufgerufen, wenn ein Knoten endet."""
                        # Formatiere den Knotennamen für bessere Lesbarkeit
                        formatted_name = node_name.replace("extract_", "").replace("_", " ").title()
                        progress.write(f"✅ Abgeschlossen: {formatted_name}")
                    
                    def on_node_error(self, node_name, error, **kwargs):
                        """Wird aufgerufen, wenn ein Fehler in einem Knoten auftritt."""
                        progress.write(f"❌ Fehler bei: {node_name} - {str(error)}")
                
                # Erstelle eine Instanz des Callback-Handlers
                callback_handler = StreamlitCallbackHandler()
                
                config = {
                    "configurable": {
                        "project_name": os.environ.get("LANGSMITH_PROJECT", "sb_trustcall"),
                        "run_name": "ShipmentBot Extraction"
                    },
                    "callbacks": [callback_handler]
                }
                
                # Starte die Extraktion mit Fortschrittsanzeige
                progress.write("🚀 Starte Extraktionsprozess...")
                final_state = shipment_graph.invoke(state, config=config)
                progress.write("✨ Extraktion abgeschlossen!")
                
                # Process the result to handle NULL and <UNKNOWN> values
                result = final_state.get("result", {})
                result = standardize_values(result)
                return result
    except Exception as e:
        st.error(f"Error processing input: {str(e)}")
        st.error(traceback.format_exc())
        return {}


def standardize_values(data):
    """
    Standardize values in the extracted data, handling NULL and <UNKNOWN> values.
    
    Args:
        data (dict): The extracted data
        
    Returns:
        dict: The standardized data
    """
    if isinstance(data, dict):
        for key, value in data.items():
            # Handle NULL and <UNKNOWN> values
            if value == "NULL" or value == "<UNKNOWN>":
                data[key] = "N/A"
            # Recursively process nested dictionaries and lists
            elif isinstance(value, (dict, list)):
                data[key] = standardize_values(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = standardize_values(item)
    
    return data


# Streamlit UI
st.title("🚚 ShipmentBot")
st.markdown("Extract structured shipping data from unstructured text using TrustCall and LangChain.")

# Input area
st.subheader("Input Text")
input_text = st.text_area(
    label="Paste your shipping information below",
    height=300,
    help="Enter details about pickup, delivery, billing addresses and shipment items",
    placeholder="""Example:
    Please arrange transport from Technik GmbH (Thomas Müller, Industriestr. 42, 33602 Bielefeld) to Logistik AG (Hauptstraße 123, 70173 Stuttgart) on March 3rd, 2025. Pickup between 7-9am, delivery between 2:40-4:40pm.
    
    We're shipping 4 pallets of machine parts (non-stackable, 100kg each, 120x80x100cm) and 2 packages of electronic components (stackable, 15kg each, 60x40x30cm).
    
    Please send the invoice to Finanz GmbH (Attn: Mr. Karl Fischer), Rechnungsweg 7, 10115 Berlin. Contact: +49987654321, email: rechnungen@finanz-gmbh.de, VAT ID: DE123456789, PO: PO-2025-4321.
    """
)

# Process button
if st.button("Extract Shipping Data", type="primary"):
    if input_text:
        # Process the input
        result = process_input(input_text)
        
        if result:
            # Display the results
            st.subheader("Extracted Data")
            
            # Create tabs for different sections
            pickup_tab, delivery_tab, billing_tab, shipment_tab, json_tab = st.tabs([
                "Pickup Address", "Delivery Address", "Billing Address", "Shipment Items", "Raw JSON"
            ])
            
            # Pickup Address Tab
            with pickup_tab:
                pickup = result.get("pickup_address", {})
                if pickup:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Company Information")
                        st.write(f"**Company:** {pickup.get('company', 'N/A')}")
                        st.write(f"**Contact:** {pickup.get('first_name', '')} {pickup.get('last_name', '')}")
                        st.write(f"**Phone:** {pickup.get('phone', 'N/A')}")
                        st.write(f"**Email:** {pickup.get('email', 'N/A')}")
                        st.write(f"**Reference:** {pickup.get('pickup_reference', 'N/A')}")
                    
                    with col2:
                        st.markdown("### Address & Schedule")
                        st.write(f"**Street:** {pickup.get('street', 'N/A')}")
                        if pickup.get('address_addition'):
                            st.write(f"**Additional:** {pickup.get('address_addition')}")
                        st.write(f"**City:** {pickup.get('postal_code', '')} {pickup.get('city', '')}")
                        st.write(f"**Country:** {pickup.get('country', 'N/A')}")
                        st.write(f"**Date:** {pickup.get('pickup_date', 'N/A')}")
                        if pickup.get('pickup_time_from') or pickup.get('pickup_time_to'):
                            st.write(f"**Time Window:** {pickup.get('pickup_time_from', '')} - {pickup.get('pickup_time_to', '')}")
                    
                    # Add pickup notes section
                    if pickup.get('pickup_notes'):
                        st.markdown("### Notes")
                        st.write(f"**Pickup Notes:** {pickup.get('pickup_notes', '')}")
                else:
                    st.warning("No pickup address information extracted")
            
            # Delivery Address Tab
            with delivery_tab:
                delivery = result.get("delivery_address", {})
                if delivery:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Company Information")
                        st.write(f"**Company:** {delivery.get('company', 'N/A')}")
                        st.write(f"**Contact:** {delivery.get('first_name', '')} {delivery.get('last_name', '')}")
                        st.write(f"**Phone:** {delivery.get('phone', 'N/A')}")
                        st.write(f"**Email:** {delivery.get('email', 'N/A')}")
                        st.write(f"**Reference:** {delivery.get('delivery_reference', 'N/A')}")
                    
                    with col2:
                        st.markdown("### Address & Schedule")
                        st.write(f"**Street:** {delivery.get('street', 'N/A')}")
                        if delivery.get('address_addition'):
                            st.write(f"**Additional:** {delivery.get('address_addition')}")
                        st.write(f"**City:** {delivery.get('postal_code', '')} {delivery.get('city', '')}")
                        st.write(f"**Country:** {delivery.get('country', 'N/A')}")
                        st.write(f"**Date:** {delivery.get('delivery_date', 'N/A')}")
                        if delivery.get('delivery_time_from') or delivery.get('delivery_time_to'):
                            st.write(f"**Time Window:** {delivery.get('delivery_time_from', '')} - {delivery.get('delivery_time_to', '')}")
                    
                    # Add delivery notes section
                    if delivery.get('delivery_notes'):
                        st.markdown("### Notes")
                        st.write(f"**Delivery Notes:** {delivery.get('delivery_notes', '')}")
                else:
                    st.warning("No delivery address information extracted")
            
            # Billing Address Tab
            with billing_tab:
                billing = result.get("billing_address", {})
                if billing:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Company Information")
                        st.write(f"**Company:** {billing.get('company', 'N/A')}")
                        salutation = f"{billing.get('salutation', '')} " if billing.get('salutation') else ""
                        st.write(f"**Contact:** {salutation}{billing.get('first_name', '')} {billing.get('last_name', '')}")
                        st.write(f"**Phone:** {billing.get('phone', 'N/A')}")
                        st.write(f"**Email:** {billing.get('email', 'N/A')}")
                        if billing.get('billing_email'):
                            st.write(f"**Billing Email:** {billing.get('billing_email')}")
                        st.write(f"**Reference:** {billing.get('reference', 'N/A')}")
                        st.write(f"**VAT ID:** {billing.get('vat_id', 'N/A')}")
                    
                    with col2:
                        st.markdown("### Address")
                        st.write(f"**Street:** {billing.get('street', 'N/A')}")
                        if billing.get('address_addition'):
                            st.write(f"**Additional:** {billing.get('address_addition')}")
                        st.write(f"**City:** {billing.get('postal_code', '')} {billing.get('city', '')}")
                        st.write(f"**Country:** {billing.get('country', 'N/A')}")
                else:
                    st.warning("No billing address information extracted")
            
            # Shipment Items Tab
            with shipment_tab:
                shipment = result.get("shipment", {})
                items = shipment.get("items", [])
                
                if items:
                    st.markdown("### Items")
                    for i, item in enumerate(items):
                        # Map load_carrier to readable category
                        carrier_types = {
                            1: "Pallet",
                            2: "Package",
                            3: "Euro Pallet Cage",
                            4: "Document",
                            5: "Other"
                        }
                        carrier_type = carrier_types.get(item.get('load_carrier', 5), "Unknown")
                        
                        with st.expander(f"Item {i+1}: {carrier_type} - {item.get('name', 'No description')}"):
                            st.write(f"**Category:** {carrier_type}")
                            st.write(f"**Description:** {item.get('name', 'N/A')}")
                            st.write(f"**Quantity:** {item.get('quantity', 'N/A')}")
                            st.write(f"**Stackable:** {'Yes' if item.get('stackable') else 'No'}")
                            st.write(f"**Weight:** {item.get('weight', 'N/A')} kg")
                            
                            dimensions = []
                            if item.get('length'):
                                dimensions.append(f"L: {item.get('length')} cm")
                            if item.get('width'):
                                dimensions.append(f"W: {item.get('width')} cm")
                            if item.get('height'):
                                dimensions.append(f"H: {item.get('height')} cm")
                            
                            if dimensions:
                                st.write(f"**Dimensions:** {' × '.join(dimensions)}")
                
                    # Notes section
                    if shipment.get("shipment_notes"):
                        st.markdown("### Notes")
                        st.write(f"**Shipment Notes:** {shipment.get('shipment_notes')}")
                else:
                    st.warning("No shipment items extracted")
            
            # Raw JSON Tab
            with json_tab:
                st.json(result)
        else:
            st.error("Failed to extract shipping data. Please check your input and try again.")
    else:
        st.warning("Please enter some text before processing")


# Footer
st.markdown("---")
st.markdown("ShipmentBot Proof of Concept | Built with TrustCall, LangChain, LangGraph, and Streamlit")

# Sidebar information
with st.sidebar:
    st.title("About ShipmentBot")
    st.markdown("""
    ShipmentBot is an LLM-based application for automated extraction of transport data from unstructured text.
    
    **Features:**
    - Intelligent data extraction from free text
    - Processing of three address types
    - Extraction of shipment data
    - Recognition of additional notes
    - Structured output as JSON
    
    This application uses TrustCall for JSON validation and extraction.
    """)
    
    # Display example input toggle
    if st.button("Show Example Input"):
        st.session_state["show_example"] = True
    
    if st.session_state.get("show_example", False):
        st.code("""Please arrange transport from Technik GmbH (Thomas Müller, Industriestr. 42, 33602 Bielefeld) to Logistik AG (Hauptstraße 123, 70173 Stuttgart) on March 3rd, 2025. Pickup between 7-9am, delivery between 2:40-4:40pm.

We're shipping 4 pallets of machine parts (non-stackable, 100kg each, 120x80x100cm) and 2 packages of electronic components (stackable, 15kg each, 60x40x30cm).

Please send the invoice to Finanz GmbH (Attn: Mr. Karl Fischer), Rechnungsweg 7, 10115 Berlin. Contact: +49987654321, email: rechnungen@finanz-gmbh.de, VAT ID: DE123456789, PO: PO-2025-4321.""")
        
        if st.button("Hide Example"):
            st.session_state["show_example"] = False


if __name__ == "__main__":
    # Initialize session state
    if "show_example" not in st.session_state:
        st.session_state["show_example"] = False 