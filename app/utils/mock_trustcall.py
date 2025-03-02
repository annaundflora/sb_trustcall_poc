"""
Mock implementation of TrustCall for development and testing.

This file provides a simplified version of the TrustCall API for local development
when the actual TrustCall package is not available.
"""
from typing import List, Any, Dict, Optional, Type, TypedDict, Union, Callable, Sequence
from pydantic import BaseModel
import json

# Simple mock version of TrustCall's create_extractor function
def create_extractor(
    llm, 
    tools: List[Type[BaseModel]], 
    tool_choice: Optional[str] = None
):
    """
    Creates a mock extractor that uses LangChain to generate JSON data.
    
    Args:
        llm: The language model to use (ChatAnthropic or compatible model)
        tools: A list of Pydantic models defining the extraction schema
        tool_choice: Optional tool to use (schema name)
        
    Returns:
        A callable that processes input and returns extracted data
    """
    schema_name = None
    schema_class = None
    
    # Determine which schema to use
    if tool_choice:
        for tool in tools:
            if tool.__name__ == tool_choice:
                schema_class = tool
                schema_name = tool.__name__
                break
    else:
        schema_class = tools[0]
        schema_name = schema_class.__name__
    
    # Create schema info for the prompt
    schema_dict = schema_class.schema()
    
    # Basic extractor function
    def invoke(input_text, config=None):
        """
        Process input text and extract structured data.
        
        Args:
            input_text: Text to process
            config: Optional configuration
            
        Returns:
            Dict with extracted data
        """
        # Prepare the message
        if isinstance(input_text, str):
            messages = [{
                "role": "user",
                "content": input_text
            }]
        else:
            # Assume it's already messages or has a messages field
            messages = input_text.get("messages", input_text)
            
        # Generate a JSON response with the LLM
        json_content = f"Extract data according to this schema: {schema_name}"
        if isinstance(messages, str):
            content = messages
        else:
            content = messages[-1].get("content", "") if isinstance(messages, list) else ""
            
        response = llm.invoke(content)
        
        try:
            # Parse the LLM response to JSON
            # This is a simplified approach - real TrustCall has more complex logic
            response_text = response.content
            
            # Extract JSON from the response if there's an explanation
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            if json_start >= 0 and json_end >= 0:
                json_str = response_text[json_start:json_end+1]
                result_dict = json.loads(json_str)
            else:
                # Use empty result if no JSON found
                result_dict = {}
            
            # Create a model instance
            model_instance = schema_class(**result_dict)
            
            # Return in the format expected by the real TrustCall
            return {
                "messages": [response],
                "responses": [model_instance],
                "response_metadata": [{"schema": schema_name}],
                "attempts": 1
            }
        except Exception as e:
            # Simplified error handling
            print(f"Error extracting data: {str(e)}")
            # Return empty model
            model_instance = schema_class()
            return {
                "messages": [response],
                "responses": [model_instance],
                "response_metadata": [{"schema": schema_name, "error": str(e)}],
                "attempts": 1
            }
    
    # Return the extractor function
    extractor = lambda x, **kwargs: invoke(x, **kwargs)
    return extractor
