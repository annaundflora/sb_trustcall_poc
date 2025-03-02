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

from app.nodes.pickup_address_node import extract_pickup_address
from app.nodes.delivery_address_node import extract_delivery_address
from app.nodes.billing_address_node import extract_billing_address
from app.nodes.shipment_node import extract_shipment

from app.schemas.pickup_address_schema import PickupAddress
from app.schemas.delivery_address_schema import DeliveryAddress
from app.schemas.billing_address_schema import BillingAddress
from app.schemas.shipment_schema import Shipment, ShipmentItem


# Helper function to merge dictionaries
def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merges two dictionaries by adding values from dict2 to dict1."""
    result = dict1.copy()
    result.update(dict2)
    return result


# Define the workflow state
class WorkflowState(TypedDict):
    """State for the shipment extraction workflow."""
    # Input text to process
    input: str
    
    # Extraction results for different components
    pickup_address: Annotated[Dict[str, Any], merge_dicts]
    delivery_address: Annotated[Dict[str, Any], merge_dicts]
    billing_address: Annotated[Dict[str, Any], merge_dicts]
    shipment: Annotated[Dict[str, Any], merge_dicts]
    
    # Final combined result
    result: Dict[str, Any]


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


def build_shipment_graph():
    """
    Build workflow with four parallel nodes for entity extraction.
    
    Returns:
        StateGraph: A compiled LangGraph workflow.
    """
    # Initialize the workflow graph
    graph = StateGraph(WorkflowState)
    
    # Add nodes for entity extraction
    graph.add_node("extract_pickup_address", extract_pickup_address)
    graph.add_node("extract_delivery_address", extract_delivery_address)
    graph.add_node("extract_billing_address", extract_billing_address)
    graph.add_node("extract_shipment", extract_shipment)
    
    # Add node for final result combination
    graph.add_node("combine_results", combine_results)
    
    # All extraction nodes start in parallel from the START node
    graph.add_edge(START, "extract_pickup_address")
    graph.add_edge(START, "extract_delivery_address")
    graph.add_edge(START, "extract_billing_address")
    graph.add_edge(START, "extract_shipment")
    
    # All extraction nodes feed into the combine_results node
    graph.add_edge("extract_pickup_address", "combine_results")
    graph.add_edge("extract_delivery_address", "combine_results")
    graph.add_edge("extract_billing_address", "combine_results")
    graph.add_edge("extract_shipment", "combine_results")
    
    # Final node connects to END
    graph.add_edge("combine_results", END)
    
    # Compile the graph
    return graph.compile() 