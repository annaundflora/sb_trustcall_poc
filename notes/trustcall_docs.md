# TrustCall Documentation

## Overview

TrustCall is a Python library designed to handle complex JSON operations with Language Learning Models (LLMs). It solves common issues in LLM JSON interactions by using JSON patch operations, enabling:

- ⚡ Faster & cheaper generation of structured output
- 🐺 Resilient retrying of validation errors, even for complex nested schemas
- 🧩 Accurate updates to existing schemas without undesired data loss

TrustCall excels in these common LLM scenarios:
- ✂️ Data extraction to complex schemas
- 🧭 LLM routing
- 🤖 Multi-step agent tool use

## Installation

```bash
pip install trustcall
```

## Core Concepts

### Problem TrustCall Solves

LLMs often struggle with two common JSON tasks:
1. **Generating complex, nested JSON schemas** completely and correctly
2. **Updating existing JSON data** without losing information

TrustCall takes a "patch-don't-post" approach, using [JSON patch](https://datatracker.ietf.org/doc/html/rfc6902) operations to incrementally modify data rather than regenerating entire structures.

### Key Components

- **Extractors**: Core components that handle LLM input/output and manage schema validation
- **Patches**: JSON patch operations used to modify schemas
- **Tools**: Schemas, functions, or Pydantic models that define the structure of extracted data
- **Validators**: Components that ensure the generated data is valid according to the schema

## API Reference

### Main Functions

#### `create_extractor`

Creates an extractor that generates validated structured outputs using an LLM.

```python
def create_extractor(
    llm: str | BaseChatModel,
    *,
    tools: Sequence[TOOL_T],
    tool_choice: Optional[str] = None,
    enable_inserts: bool = False,
    enable_updates: bool = True,
    enable_deletes: bool = False,
    existing_schema_policy: bool | Literal["ignore"] = True,
) -> Runnable[InputsLike, ExtractionOutputs]:
    """Creates an extractor that generates validated structured outputs using an LLM.
    
    This function binds validators and retry logic to ensure the validity of
    generated tool calls. It uses JSONPatch to correct validation errors caused
    by incorrect or incomplete parameters in previous tool calls.
    
    Args:
        llm: The language model to use (either a string identifier or BaseChatModel instance)
        tools: Sequence of tools (BaseModel classes, functions, or dictionaries)
        tool_choice: The specific tool to use (if None, LLM chooses)
        enable_inserts: Whether to allow extracting new schemas alongside existing ones
        enable_updates: Whether to allow updating existing schemas with PatchDoc
        enable_deletes: Whether to allow deleting existing schemas
        existing_schema_policy: How to handle existing schemas that don't match tools
            - True: Raise an error
            - False: Treat as a dictionary
            - "ignore": Ignore these schemas
    
    Returns:
        A runnable that can be invoked with messages and returns validated AI messages and responses
    """
```

### Key Types

#### `TOOL_T`

```python
TOOL_T = Union[BaseTool, Type[BaseModel], Callable, Dict[str, Any]]
```

Represents the types that can be used as tools in TrustCall:
- Pydantic BaseModel classes
- LangChain BaseTool instances
- Python callable functions
- Dictionary representations of JSON schemas

#### `ExtractionInputs`

```python
class ExtractionInputs(TypedDict, total=False):
    messages: Union[Messages, PromptValue]
    existing: Optional[ExistingType]
    """Existing schemas. Key is the schema name, value is the schema instance.
    If a list, supports duplicate schemas to update.
    """
```

Input format for the extractor.

#### `ExtractionOutputs`

```python
class ExtractionOutputs(TypedDict):
    messages: List[AIMessage]
    responses: List[BaseModel]
    response_metadata: List[dict[str, Any]]
    attempts: int
```

Output format from the extractor.

#### `ExistingType`

```python
ExistingType = Union[
    Dict[str, Any], 
    List[SchemaInstance], 
    List[tuple[str, str, dict[str, Any]]]
]
```

Represents existing schemas for updates, in one of these formats:
- Dictionary mapping schema names to instances
- List of SchemaInstance objects
- List of tuples containing (record_id, schema_name, record_dict)

#### `SchemaInstance`

```python
class SchemaInstance(NamedTuple):
    """Represents an instance of a schema with its associated metadata."""
    record_id: str
    schema_name: str | Literal["__any__"]
    record: Dict[str, Any]
```

Stores information about a specific schema instance.

#### `JsonPatch`

```python
class JsonPatch(BaseModel):
    """A JSON Patch document represents an operation to be performed on a JSON document."""
    op: Literal["add", "remove", "replace"]
    path: str
    value: Union[_JSON_TYPES, List[_JSON_TYPES], Dict[str, _JSON_TYPES]]
```

Represents a single JSON patch operation.

## Usage Examples

### Basic Extraction

Extract structured data from text using a Pydantic model:

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from trustcall import create_extractor

class UserInfo(BaseModel):
    name: str = Field(description="User's full name")
    age: int = Field(description="User's age in years")

llm = ChatOpenAI()
extractor = create_extractor(llm, tools=[UserInfo])

result = extractor.invoke("My name is Alice and I'm 30 years old")
print(result["responses"][0])  # UserInfo(name='Alice', age=30)
```

### Extracting Complex Schemas

Extract data into nested models with validation:

```python
from typing import List, Optional
from pydantic import BaseModel, Field

# Define a complex nested schema
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class Pet(BaseModel):
    kind: str
    name: Optional[str]
    age: Optional[int]

class User(BaseModel):
    name: str
    age: int
    address: Address
    pets: Optional[List[Pet]] = None

# Create an extractor
extractor = create_extractor(llm, tools=[User])

# Extract from text
result = extractor.invoke(
    "John is 35 years old and lives at 123 Main St, New York, USA, 10001. " 
    "He has a 5-year-old dog named Rex."
)
```

### Updating Existing Data

Update existing data with new information:

```python
from trustcall import create_extractor

# Starting data
existing_user = {
    "name": "Alice",
    "age": 30,
    "address": {
        "street": "123 Old Street",
        "city": "San Francisco",
        "country": "USA",
        "postal_code": "94105"
    }
}

extractor = create_extractor(llm, tools=[User])

# Update with new information
result = extractor.invoke({
    "messages": "Alice just moved to 456 New Street, Chicago, still in the USA but postal code 60601.",
    "existing": {"User": existing_user}
})

updated_user = result["responses"][0]
print(updated_user.address.city)  # Chicago
```

### Multiple Tools With Tool Choice

Use multiple models and let the LLM choose which to use:

```python
from typing import List
from pydantic import BaseModel, Field

class UserInfo(BaseModel):
    name: str
    age: int

class Preferences(BaseModel):
    foods: List[str] = Field(description="Favorite foods")

# Create extractor with multiple tools
extractor = create_extractor(
    llm,
    tools=[UserInfo, Preferences],
    # No tool_choice means the LLM can choose which tool to use
)

# Extract using both tools
result = extractor.invoke(
    "I'm Bob, 25 years old, and I love pizza and sushi"
)

# Responses contain instances of both models
print(result["responses"])  # [UserInfo(...), Preferences(...)]
```

### Working With Existing Data (Multiple Records)

Update multiple records from a single source:

```python
from typing import List
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str
    relationship: str
    notes: List[str]

# Initial data
initial_people = [
    ("0", "Person", {
        "name": "Emma Thompson",
        "relationship": "Friend",
        "notes": ["Loves hiking", "Works in marketing"]
    }),
    ("1", "Person", {
        "name": "Michael Chen",
        "relationship": "Coworker",
        "notes": ["Vegetarian", "Plays guitar"]
    })
]

extractor = create_extractor(
    llm,
    tools=[Person],
    enable_inserts=True  # Allow creating new records
)

# Update existing records and create new ones
result = extractor.invoke({
    "messages": "Emma got promoted to Senior Marketing Manager. Also, my neighbor Sarah loves gardening.",
    "existing": initial_people
})

# Check results
for r, meta in zip(result["responses"], result["response_metadata"]):
    print(f"ID: {meta.get('json_doc_id', 'New')}")
    print(r)
```

### Validation With Custom Rules

Apply custom validation rules to extracted data:

```python
from typing import List
from pydantic import BaseModel, Field, validator

class Preferences(BaseModel):
    foods: List[str] = Field(description="Favorite foods")

    @validator("foods")
    def at_least_three_foods(cls, v):
        if len(v) < 3:
            raise ValueError("Must have at least three favorite foods")
        return v

extractor = create_extractor(llm, tools=[Preferences])

# TrustCall will handle retries to meet the validation rule
result = extractor.invoke("I like apple pie and ice cream.")
print(result["responses"][0].foods)  # Will have at least 3 items
```

## Advanced Usage

### Integration With LangGraph

Use TrustCall in LangGraph workflows:

```python
import operator
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import Annotated, TypedDict
from trustcall import create_extractor

# Define your tools and models
def save_user_information(preferences):
    """Save user information to a database."""
    return "User information saved"

def lookup_time(tz: str) -> str:
    """Lookup the current time in a given timezone."""
    # Implementation...

# Create a TrustCall extractor as your agent
agent = create_extractor(llm, tools=[save_user_information, lookup_time])

# Define graph state
class State(TypedDict):
    messages: Annotated[list, operator.add]

# Build the graph
builder = StateGraph(State)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode([save_user_information, lookup_time]))
builder.add_edge("tools", "agent")
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)

# Compile and use
graph = builder.compile()
result = graph.invoke({"messages": [("user", "What time is it in Denver?")]})
```

### Using With Different LLM Providers

TrustCall works with various LLM providers:

```python
# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-opus-20240229")

# Fireworks
from langchain_fireworks import ChatFireworks
llm = ChatFireworks(model="accounts/fireworks/models/firefunction-v2")

# Create extractor with any provider
extractor = create_extractor(llm, tools=[...])
```

### Managing Extraction Policies

Control how TrustCall handles existing schemas and creates new ones:

```python
# Allow updating existing schemas but not creating new ones
extractor = create_extractor(
    llm,
    tools=[User, Preferences],
    enable_updates=True,
    enable_inserts=False
)

# Allow both updates and new schemas
extractor = create_extractor(
    llm,
    tools=[User, Preferences],
    enable_updates=True,
    enable_inserts=True
)

# Control how to handle schema mismatches
extractor = create_extractor(
    llm,
    tools=[User, Preferences],
    existing_schema_policy="ignore"  # Just ignore schemas that don't match
)
```

## Technical Details

### JSON Patch Operations

TrustCall uses [JSON Patch (RFC 6902)](https://datatracker.ietf.org/doc/html/rfc6902) operations to modify JSON documents:

- `add`: Adds a new value to an object or array
- `remove`: Removes a value from an object or array
- `replace`: Replaces an existing value

Example patch operations:

```json
[
  { "op": "replace", "path": "/name", "value": "New Name" },
  { "op": "add", "path": "/tags/-", "value": "new tag" },
  { "op": "remove", "path": "/temporary_field" }
]
```

### Handling Validation Errors

When validation errors occur, TrustCall:

1. Captures the error details
2. Presents the error to the LLM with the schema specification
3. Asks the LLM to generate patches to fix the specific validation issue
4. Applies the patches and re-validates
5. Repeats until valid or max attempts reached

### Supported Schema Formats

TrustCall accepts schemas in multiple formats:

- **Pydantic models** (v1 or v2)
- **Python functions** with typed arguments
- **JSON Schema dictionaries**
- **TypedDict** classes
- **LangChain BaseTool** instances

## Troubleshooting

### Common Issues

1. **Validation errors persist**: Ensure your schemas have clear descriptions for fields
2. **Performance is slow**: Consider simplifying complex schemas or breaking them into smaller parts
3. **LLM fails to generate correct patches**: Try using a more capable model (like GPT-4 or Claude)

### Debugging Tips

1. Enable verbose logging to see what's happening:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Examine the response metadata to understand patch operations:
   ```python
   print(result["response_metadata"])
   ```

3. Check the "attempts" count to see if multiple retries were needed:
   ```python
   print(result["attempts"])
   ```

## Limitations

- Complex validation rules may require more powerful LLMs
- Very large schemas might be challenging for the LLM to process
- Performance depends on the underlying LLM's understanding of JSON
- Requires properly defined schemas with good field descriptions

## Best Practices

1. **Provide clear field descriptions** in your Pydantic models
2. **Start with simpler schemas** and gradually add complexity
3. **Test with different LLMs** to find the best performance
4. **Use appropriate patch operations** when updating data:
   - Use `replace` operations first
   - Use `remove` operations starting with higher array indices
   - Use `add` operations last

5. **Use validation rules** to enforce data quality
6. **Structure messages clearly** when providing context for extraction