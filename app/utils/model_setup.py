"""
Konfiguration für LLM-Modelle mit Unterstützung für mehrere API-Keys.
"""
import os
from langchain_anthropic import ChatAnthropic
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    # Versuche zuerst, den spezifischen API-Key zu bekommen
    api_key = os.environ.get(f"ANTHROPIC_API_KEY_{key_index}")
    
    # Wenn der spezifische Key nicht gefunden wurde, versuche den Standard-Key
    if not api_key:
        logger.warning(f"ANTHROPIC_API_KEY_{key_index} nicht gefunden. Versuche ANTHROPIC_API_KEY...")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Wenn immer noch kein Key gefunden wurde, gib eine klare Fehlermeldung aus
    if not api_key:
        available_keys = [k for k in os.environ.keys() if k.startswith("ANTHROPIC_API_KEY")]
        error_msg = (
            f"Kein API-Key für Anthropic gefunden. Weder ANTHROPIC_API_KEY_{key_index} "
            f"noch ANTHROPIC_API_KEY sind in den Umgebungsvariablen gesetzt. "
            f"Verfügbare Anthropic-Keys: {available_keys}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Verwende API-Key für Index {key_index}")
    
    return ChatAnthropic(
        model=model,
        anthropic_api_key=api_key,
        temperature=temperature,
        max_tokens=1000,
        timeout=10,
    ) 