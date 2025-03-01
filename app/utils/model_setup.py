"""
Konfiguration für LLM-Modelle mit Unterstützung für mehrere API-Keys.
"""
import os
from langchain_anthropic import ChatAnthropic

def get_anthropic_llm(model="claude-3-7-sonnet-20250219", temperature=0, key_index=1):
    """
    Get a ChatAnthropic LLM with the specified parameters.
    
    Args:
        model (str): The model to use.
        temperature (float): The temperature for generation.
        key_index (int): Which API key to use (1 or 2)
        
    Returns:
        ChatAnthropic: A ChatAnthropic model instance.
    """
    # Wähle den passenden API-Key basierend auf dem Index
    api_key = os.environ.get(f"ANTHROPIC_API_KEY_{key_index}")
    
    return ChatAnthropic(
        model=model,
        anthropic_api_key=api_key,
        temperature=temperature,
        max_tokens=1000,
        timeout=10,
        cache=True  # Aktiviere Caching für bessere Performance
    ) 