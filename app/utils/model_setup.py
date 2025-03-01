"""
Utility functions for model setup.
"""
import os
from langchain_anthropic import ChatAnthropic


def get_anthropic_llm(model="claude-3-7-sonnet-20250219", temperature=0):
    """
    Get a ChatAnthropic LLM with the specified parameters.
    
    Args:
        model (str): The model to use.
        temperature (float): The temperature for generation.
        
    Returns:
        ChatAnthropic: A ChatAnthropic model instance.
    """
    return ChatAnthropic(
        model=model,
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        temperature=temperature
    ) 