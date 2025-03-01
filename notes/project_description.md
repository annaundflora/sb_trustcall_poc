# Shipmentbot

## Product Description

Shipmentbot is an LLM-based application for automated extraction and structuring of transport data from unstructured user inputs. The application processes free-text inputs such as emails or copied documents and converts them into structured data for transport bookings.

## Core Functionalities

- **Intelligent data extraction** from unstructured texts
- **Processing of three address types**: pickup address, delivery address, billing address
- **Extraction of shipment data**: package types, dimensions, weight, stackability
- **Recognition of additional notes** for pickup, delivery, and general requirements
- **Validation and error correction** of extracted data
- **Structured output** as JSON for further processing

## Data Modeling

### Address Data

The system extracts three different types of addresses:

1. **Pickup Address**:
   - Company, contact person (first/last name)
   - Location data (street, address addition, postal code, city, country)
   - Contact data (phone for loading)
   - Time window (pickup date, time period)
   - Loading reference and notes

2. **Delivery Address**:
   - Similar structure to pickup address
   - Specific fields for unloading
   - Delivery time window and references

3. **Billing Address**:
   - Company, salutation, contact person
   - Location data
   - Communication data (email, phone)
   - Special fields: VAT ID, billing email, reference

### Shipment Data

- **Item types**: pallets, packages, cage pallets, documents, other
- **Quantity data**: number of pieces
- **Dimensions**: weight (kg), length, width, height (cm)
- **Properties**: stackability, description of goods
- **Additional information**: e.g., ADR, hazardous materials notes

### Notes

- **General instructions** for the shipment
- **Specific instructions** for pickup and delivery
- **Handling instructions** for the goods

## Technology Stack

### Main Components

- **Python 3.9+**: Base programming language
- **Streamlit**: Frontend framework for the user interface
- **LangChain/LangGraph**: Orchestration of LLM calls and workflow management
- **TrustCall**: JSON schema validation and patch-based error correction
- **LangSmith**: Tracing and debugging of LLM requests

### LLMs Used

- **Claude 3.7 Sonnet**: Primary model for precise data extraction (model="claude-3-7-sonnet-20250219",)
- **GPT-4**: Secondary model for fallbacks and specific tasks

### Python Packages

```
langchain
langchain-core
langchain-anthropic>
langchain-openai
langgraph
streamlit
pydantic
python-dotenv
langsmith
jsonpatch
trustcall
```

## Workflow Architecture

Shipmentbot uses a field-group-oriented extractor approach with TrustCall:

1. **Parallelized extraction** of different data types
2. **Incremental refinement** through specialized extractors
3. **Automatic validation** against Pydantic schemas
4. **Intelligent error correction** through JSON patches

The workflow is implemented as a directed acyclic graph (DAG) in LangGraph, resulting in a highly customizable and extensible system.

## API and Integration

Shipmentbot can be integrated into existing transport systems through:

- **Streamlit-based web interface** for direct user input
- **REST API** for integration with other systems
- **Webhook support** for email parsers or document processing systems

## Example Output

The system generates structured JSON data like the following example:

```json
{
  "pickup_address": {
    "company": "Technik GmbH",
    "first_name": "Thomas",
    "last_name": "Müller",
    "street": "Industriestr. 42",
    "postal_code": "33602",
    "city": "Bielefeld",
    "country": "DE",
    "phone": "+49123456789",
    "pickup_date": "2025-03-03",
    "pickup_time_from": "07:00",
    "pickup_time_to": "09:00"
  },
  "delivery_address": {
    "company": "Logistik AG",
    "street": "Hauptstraße 123",
    "postal_code": "70173",
    "city": "Stuttgart",
    "country": "DE",
    "delivery_date": "2025-03-03",
    "delivery_time_from": "14:40",
    "delivery_time_to": "16:40"
  },
  "billing_address": {
    "company": "Finanz GmbH",
    "salutation": "Herr",
    "first_name": "Karl",
    "last_name": "Fischer",
    "street": "Rechnungsweg 7",
    "postal_code": "10115",
    "city": "Berlin",
    "country": "DE",
    "phone": "+49987654321",
    "email": "rechnungen@finanz-gmbh.de",
    "billing_email": "buchhaltung@finanz-gmbh.de",
    "reference": "PO-2025-4321",
    "vat_id": "DE123456789"
  },
  "shipment": {
    "items": [
      {
        "category": "Pallet",
        "description": "Machine parts",
        "quantity": 4,
        "stackable": false,
        "weight": 100,
        "length": 120,
        "width": 80,
        "height": 100
      },
      {
        "category": "Package",
        "description": "Electronic components",
        "quantity": 2,
        "stackable": true,
        "weight": 15,
        "length": 60,
        "width": 40,
        "height": 30
      }
    ]
  }
}
```

## Development Approach

Shipmentbot uses a modular, component-based development approach:

- **Field-group-based extractor modules** for precise data capture
- **Validating Pydantic models** with clear data types and descriptions
- **TrustCall-based schema validation** with automatic error correction mechanisms
- **LangGraph-based workflow control** with state management and parallel processing