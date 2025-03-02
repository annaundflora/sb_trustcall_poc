# ShipmentBot

ShipmentBot is an LLM-based application for automated extraction and structuring of transport data from unstructured user inputs. The application processes free-text inputs such as emails or copied documents and converts them into structured data for transport bookings.

## Features

- **Intelligent data extraction** from unstructured texts
- **Processing of three address types**: pickup address, delivery address, billing address
- **Extraction of shipment data**: package types, dimensions, weight, stackability
- **Recognition of additional notes** for pickup, delivery, and general requirements
- **Validation and error correction** of extracted data
- **Structured output** as JSON for further processing

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd sb_trustcall
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file with the following variables:
   ```
   ANTHROPIC_API_KEY=your_anthropic_key
   LANGSMITH_API_KEY=your_langsmith_key
   LANGSMITH_ENDPOINT=your_langsmith_endpoint
   LANGSMITH_PROJECT=sb_trustcall
   ```

## Running the Application

Launch the Streamlit application with:

```
streamlit run app.py
```

This will start the web interface where you can enter unstructured text and extract structured shipment data.

## Usage

1. Enter or paste your shipment information into the text area.
2. Click the "Extract Shipping Data" button.
3. View the extracted data in the tabbed interface.
4. Use the raw JSON output for further processing or integration with other systems.

## Project Structure

- `app/schemas/`: Pydantic models for data validation
- `app/nodes/`: Extraction nodes using TrustCall
- `app/utils/`: Utility functions and workflow orchestration
- `instructions/`: Prompt templates for the extraction nodes
- `app.py`: Main Streamlit application

## Technology Stack

- **Python 3.9+**: Base programming language
- **Streamlit**: Frontend framework for the user interface
- **LangChain/LangGraph**: Orchestration of LLM calls and workflow management
- **TrustCall**: JSON schema validation and patch-based error correction
- **LangSmith**: Tracing and debugging of LLM requests

## Proof of Concept

This is a proof of concept application to demonstrate the capabilities of TrustCall and LangChain for structured data extraction. The focus is on optimizing the workflow and instruction templates rather than adding additional features. 