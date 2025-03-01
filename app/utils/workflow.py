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
    
    # Final combined result
    result: Dict[str, Any]


def build_shipment_graph():
    """
    Build the LangGraph workflow for extracting shipment data.
    
    Returns:
        StateGraph: A compiled LangGraph workflow.
    """
    # Initialize the workflow graph
    graph = StateGraph(WorkflowState)
    
    # Add nodes for pickup address extraction
    graph.add_node("extract_pickup_basis", extract_pickup_basis)
    graph.add_node("extract_pickup_location", extract_pickup_location)
    graph.add_node("extract_pickup_time", extract_pickup_time)
    graph.add_node("extract_pickup_communication", extract_pickup_communication)
    
    # Add nodes for delivery address extraction
    graph.add_node("extract_delivery_basis", extract_delivery_basis)
    graph.add_node("extract_delivery_location", extract_delivery_location)
    graph.add_node("extract_delivery_time", extract_delivery_time)
    graph.add_node("extract_delivery_communication", extract_delivery_communication)
    
    # Add nodes for billing address extraction
    graph.add_node("extract_billing_basis", extract_billing_basis)
    graph.add_node("extract_billing_location", extract_billing_location)
    graph.add_node("extract_billing_communication", extract_billing_communication)
    
    # Add nodes for shipment items extraction
    graph.add_node("extract_shipment_basics", extract_shipment_basics)
    graph.add_node("extract_shipment_dimensions", extract_shipment_dimensions)
    graph.add_node("extract_shipment_notes", extract_shipment_notes)
    
    # Add node for combining results
    graph.add_node("combine_results", combine_results)
    
    # Define edges (sequential execution to avoid rate limits)
    # Pickup address extraction chain
    graph.add_edge(START, "extract_pickup_basis")
    graph.add_edge("extract_pickup_basis", "extract_pickup_location")
    graph.add_edge("extract_pickup_location", "extract_pickup_time")
    graph.add_edge("extract_pickup_time", "extract_pickup_communication")
    graph.add_edge("extract_pickup_communication", "extract_delivery_basis")
    
    # Delivery address extraction chain
    graph.add_edge("extract_delivery_basis", "extract_delivery_location")
    graph.add_edge("extract_delivery_location", "extract_delivery_time")
    graph.add_edge("extract_delivery_time", "extract_delivery_communication")
    graph.add_edge("extract_delivery_communication", "extract_billing_basis")
    
    # Billing address extraction chain
    graph.add_edge("extract_billing_basis", "extract_billing_location")
    graph.add_edge("extract_billing_location", "extract_billing_communication")
    graph.add_edge("extract_billing_communication", "extract_shipment_basics")
    
    # Shipment extraction chain
    graph.add_edge("extract_shipment_basics", "extract_shipment_dimensions")
    graph.add_edge("extract_shipment_dimensions", "extract_shipment_notes")
    graph.add_edge("extract_shipment_notes", "combine_results")
    
    # End the workflow after combining results
    graph.add_edge("combine_results", END)
    
    # Compile the graph
    return graph.compile()


def combine_results(state):
    """Combine all extraction results into a single structure."""
    # Combine pickup address
    pickup_address = {
        **state.get("pickup_basis", {}),
        **state.get("pickup_location", {}),
        **state.get("pickup_time", {}),
        **state.get("pickup_communication", {}),
    }
    
    # Combine delivery address
    delivery_address = {
        **state.get("delivery_basis", {}),
        **state.get("delivery_location", {}),
        **state.get("delivery_time", {}),
        **state.get("delivery_communication", {}),
    }
    
    # Combine billing address
    billing_address = {
        **state.get("billing_basis", {}),
        **state.get("billing_location", {}),
        **state.get("billing_communication", {}),
    }
    
    # Combine shipment items
    shipment_items = []
    if state.get("shipment_basics") and state.get("shipment_dimensions"):
        # For simplicity, we're assuming there's only one item for this PoC
        # In a real implementation, we'd need to match items by ID or other attributes
        item = {
            **state["shipment_basics"][0],
            **state["shipment_dimensions"][0],
        }
        shipment_items.append(item)
    
    # Create the shipment structure
    shipment = {
        "items": shipment_items,
    }
    
    # Add notes if available
    if state.get("shipment_notes"):
        shipment.update({
            "general_notes": state["shipment_notes"].get("general_notes"),
            "pickup_notes": state["shipment_notes"].get("pickup_notes"),
            "delivery_notes": state["shipment_notes"].get("delivery_notes"),
        })
    
    # Create the final booking
    booking = {
        "pickup_address": pickup_address,
        "delivery_address": delivery_address,
        "billing_address": billing_address,
        "shipment": shipment,
    }
    
    # Return the result
    return {"result": booking} 