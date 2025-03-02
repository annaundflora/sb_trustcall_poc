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

# Import the combined node instead of individual nodes
from app.nodes.fixed_node import extract_shipment_booking

# Import the combined schema
from app.schemas.shipment_booking_schema import ShipmentBooking

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
    Build workflow with a single unified node for entity extraction.
    
    Returns:
        StateGraph: A compiled LangGraph workflow.
    """
    # Initialize the workflow graph
    graph = StateGraph(WorkflowState)
    
    # Add the combined extraction node
    graph.add_node("extract_shipment_booking", extract_shipment_booking)
    
    # Add node for final result combination
    graph.add_node("combine_results", combine_results)
    
    # Connect the extraction node to the start
    graph.add_edge(START, "extract_shipment_booking")
    
    # Connect the extraction node to the combine_results node
    graph.add_edge("extract_shipment_booking", "combine_results")
    
    # Final node connects to END
    graph.add_edge("combine_results", END)
    
    # Compile the graph
    return graph.compile()
