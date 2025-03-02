"""
Configuration utilities.
"""
import os
from dotenv import load_dotenv
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache


def load_environment():
    """
    Load environment variables from .env file and initialize LangChain cache.
    """
    # Load from .env file
    load_dotenv()
    
    # Initialize LangChain cache
    set_llm_cache(InMemoryCache())
    
    # Verify that required API keys are present
    required_vars = [
        "ANTHROPIC_API_KEY_1",  # API key 1 for pickup and delivery nodes
        "ANTHROPIC_API_KEY_2",  # API key 2 for billing and shipment nodes
        "LANGSMITH_API_KEY",
        "LANGSMITH_ENDPOINT",
        "LANGSMITH_PROJECT"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 