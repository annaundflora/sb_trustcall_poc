"""
LangGraph workflow for coordinating extraction.
"""
import os
from typing import Dict, List, Any, TypedDict, Annotated, Callable
import operator
from pydantic import BaseModel

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, END, START
import langgraph.prebuilt as prebuilt

# Importiere die Gruppenfunktionen für kontrollierte Parallelität
from app.utils.parallel_helpers import (
    extract_pickup_group,
    extract_delivery_group,
    extract_billing_group,
    extract_shipment_group
)

# Importiere die einzelnen Extraktoren für die Kombination der Ergebnisse
from app.nodes.pickup_address_nodes import (
    extract_pickup_basis,
    extract_pickup_location,
    extract_pickup_time,
    extract_pickup_communication
)
from app.nodes.delivery_address_nodes import (
    extract_delivery_basis,
    extract_delivery_location,
    extract_delivery_time,
    extract_delivery_communication
)
from app.nodes.billing_address_nodes import (
    extract_billing_basis,
    extract_billing_location,
    extract_billing_communication
)
from app.nodes.shipment_nodes import (
    extract_shipment_basics,
    extract_shipment_dimensions,
    extract_shipment_notes
)
from app.schemas.address_schemas import (
    PickupAddress, DeliveryAddress, BillingAddress
)
from app.schemas.shipment_schemas import (
    ShipmentItem, Shipment
)
from app.schemas.combined_schema import ShipmentBooking


# Hilfsfunktion zum Zusammenführen von Dictionaries
def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Führt zwei Dictionaries zusammen, indem die Werte aus dict2 zu dict1 hinzugefügt werden."""
    result = dict1.copy()
    result.update(dict2)
    return result


# Define the workflow state
class WorkflowState(TypedDict):
    """State for the shipment extraction workflow."""
    # Input text to process
    input: str
    
    # Extraction results for different components
    pickup_basis: Annotated[Dict[str, Any], merge_dicts]
    pickup_location: Annotated[Dict[str, Any], merge_dicts]
    pickup_time: Annotated[Dict[str, Any], merge_dicts]
    pickup_communication: Annotated[Dict[str, Any], merge_dicts]
    
    delivery_basis: Annotated[Dict[str, Any], merge_dicts]
    delivery_location: Annotated[Dict[str, Any], merge_dicts]
    delivery_time: Annotated[Dict[str, Any], merge_dicts]
    delivery_communication: Annotated[Dict[str, Any], merge_dicts]
    
    billing_basis: Annotated[Dict[str, Any], merge_dicts]
    billing_location: Annotated[Dict[str, Any], merge_dicts]
    billing_communication: Annotated[Dict[str, Any], merge_dicts]
    
    shipment_basics: Annotated[List[Dict[str, Any]], operator.add]
    shipment_dimensions: Annotated[List[Dict[str, Any]], operator.add]
    shipment_notes: Annotated[Dict[str, Any], merge_dicts]
    
    # Kombinierte Ergebnisse für jede Gruppe
    pickup_address: Annotated[Dict[str, Any], merge_dicts]
    delivery_address: Annotated[Dict[str, Any], merge_dicts]
    billing_address: Annotated[Dict[str, Any], merge_dicts]
    shipment: Annotated[Dict[str, Any], merge_dicts]
    
    # Final combined result
    result: Dict[str, Any]


def combine_pickup(state):
    """Kombiniert die Pickup-Adressdaten."""
    pickup_address = {
        **state.get("pickup_basis", {}),
        **state.get("pickup_location", {}),
        **state.get("pickup_time", {}),
        **state.get("pickup_communication", {}),
    }
    return {"pickup_address": pickup_address}


def combine_delivery(state):
    """Kombiniert die Delivery-Adressdaten."""
    delivery_address = {
        **state.get("delivery_basis", {}),
        **state.get("delivery_location", {}),
        **state.get("delivery_time", {}),
        **state.get("delivery_communication", {}),
    }
    return {"delivery_address": delivery_address}


def combine_billing(state):
    """Kombiniert die Billing-Adressdaten."""
    billing_address = {
        **state.get("billing_basis", {}),
        **state.get("billing_location", {}),
        **state.get("billing_communication", {}),
    }
    return {"billing_address": billing_address}


def combine_shipment(state):
    """Kombiniert die Shipment-Daten."""
    # Kombiniere Shipment-Items
    shipment_items = []
    if state.get("shipment_basics") and state.get("shipment_dimensions"):
        for i, basics in enumerate(state["shipment_basics"]):
            if i < len(state["shipment_dimensions"]):
                item = {**basics, **state["shipment_dimensions"][i]}
                shipment_items.append(item)
    
    # Erstelle Shipment-Struktur
    shipment = {"items": shipment_items}
    
    # Füge Notizen hinzu, wenn vorhanden
    if state.get("shipment_notes"):
        shipment.update({
            "general_notes": state["shipment_notes"].get("general_notes"),
            "pickup_notes": state["shipment_notes"].get("pickup_notes"),
            "delivery_notes": state["shipment_notes"].get("delivery_notes"),
        })
    
    return {"shipment": shipment}


def build_shipment_graph():
    """
    Build the LangGraph workflow with controlled parallelization to avoid API queueing.
    
    Returns:
        StateGraph: A compiled LangGraph workflow.
    """
    # Initialize the workflow graph
    graph = StateGraph(WorkflowState)
    
    # Füge Gruppenknoten mit kontrollierter Parallelität hinzu
    graph.add_node("extract_pickup_group", extract_pickup_group)
    graph.add_node("extract_delivery_group", extract_delivery_group)
    graph.add_node("extract_billing_group", extract_billing_group)
    graph.add_node("extract_shipment_group", extract_shipment_group)
    
    # Add combination nodes for each group
    graph.add_node("combine_pickup", combine_pickup)
    graph.add_node("combine_delivery", combine_delivery)
    graph.add_node("combine_billing", combine_billing)
    graph.add_node("combine_shipment", combine_shipment)
    
    # Add node for final result combination
    graph.add_node("combine_results", combine_results)
    
    # Verbinde die Gruppenknoten mit dem Start-Knoten
    # Gruppe 1 mit API-Key 1: Pickup und Billing
    graph.add_edge(START, "extract_pickup_group")
    graph.add_edge(START, "extract_billing_group")
    
    # Gruppe 2 mit API-Key 2: Delivery und Shipment
    graph.add_edge(START, "extract_delivery_group")
    graph.add_edge(START, "extract_shipment_group")
    
    # Verbinde die Gruppenknoten mit den Kombinations-Knoten
    graph.add_edge("extract_pickup_group", "combine_pickup")
    graph.add_edge("extract_delivery_group", "combine_delivery")
    graph.add_edge("extract_billing_group", "combine_billing")
    graph.add_edge("extract_shipment_group", "combine_shipment")
    
    # Finaler Combine
    graph.add_edge("combine_pickup", "combine_results")
    graph.add_edge("combine_delivery", "combine_results")
    graph.add_edge("combine_billing", "combine_results")
    graph.add_edge("combine_shipment", "combine_results")
    graph.add_edge("combine_results", END)
    
    # Compile the graph
    return graph.compile()


def combine_results(state):
    """Combine all extraction results into a single structure."""
    # Create the final booking
    booking = {
        "pickup_address": state.get("pickup_address", {}),
        "delivery_address": state.get("delivery_address", {}),
        "billing_address": state.get("billing_address", {}),
        "shipment": state.get("shipment", {"items": []}),
    }
    
    # Return the result
    return {"result": booking} 