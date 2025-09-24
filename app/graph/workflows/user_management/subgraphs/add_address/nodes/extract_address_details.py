"""Extract address details from user prompt using LLM with structured output."""

from typing import cast
from app.graph.workflows.user_management.types import AddAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


class AddressDetails(BaseModel):
    """Structured address details extracted from user input."""
    type: str  # home or work or other
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    is_default: bool = False


async def extract_address_details_node(state: AddAddressState) -> AddAddressState:
    """Extract structured address details from user message using LLM."""
    
    user_message = state.get("search_query", "")

    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert address extraction assistant for an e-commerce system.
        Extract complete address information from user messages.

        TASK:
        Extract these EXACT fields:
        - type: Address type ('billing' or 'shipping'). Default to 'shipping' if not specified.
        - street: Complete street address including house number and street name
        - city: City name
        - state: State, province, or region (use standard abbreviations when possible)
        - zip_code: ZIP code, postal code, or equivalent
        - country: Country code or name (default to 'US' if not specified)
        - is_default: Whether this should be the default address (true if mentioned as 'default')

        EXAMPLES:
        Input: "Add my address: 123 Main St, New York, NY 10001"
        Output: {{
            "type": "other",
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "US",
            "is_default": false
        }}

        Input: "Save this billing address: 456 Oak Ave, Los Angeles CA 90210 as default"
        Output: {{
            "type": "other",
            "street": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90210",
            "country": "US",
            "is_default": true
        }}

        RULES:
        1. Extract EXACT address components as they appear
        2. Normalize state names to standard abbreviations (e.g., "Texas" → "TX")
        3. Clean up formatting (proper capitalization, remove extra spaces)
        4. If critical information is missing, use reasonable defaults
        5. Country codes should be standardized (USA/United States → US, UK/Britain → GB)
        """),
        ("user", "{query}")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)

        response = cast(AddressDetails, await llm.with_structured_output(AddressDetails).ainvoke(extraction_prompt.invoke({"query": user_message})))

        # Store extracted address in state
        state["extracted_address"] = {
            "type": response.type,
            "street": response.street,
            "city": response.city,
            "state": response.state,
            "zip_code": response.zip_code,
            "country": response.country,
            "is_default": response.is_default
        }
        
        print(f"Successfully extracted address: {state['extracted_address']}")
        
    except Exception as e:
        print(f"Error in extract_address_details_node: {e}")
        # Set error state if extraction fails
        state["extracted_address"] = None
        state["error_message"] = f"Failed to extract address details: {str(e)}"
    
    return state
