"""Extract address ID and new address details from user prompt using LLM with structured output."""

from typing import cast
from app.graph.workflows.user_management.types import EditAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


class EditAddressDetails(BaseModel):
    """Structured address edit details extracted from user input."""
    address_id: int
    type: str | None = None  # home, work, or other
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    is_default: bool | None = None


async def extract_edit_details_node(state: EditAddressState) -> EditAddressState:
    """Extract address ID and new details from user message using LLM."""
    
    user_message = state.get("search_query", "")

    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert address editing assistant for an e-commerce system.
        Extract address ID and the fields to be updated from user messages.

        TASK:
        Extract these fields for address editing:
        - address_id: The ID of the address to edit (REQUIRED)
        - type: New address type ('home', 'work', or 'other') - only if mentioned
        - street: New street address - only if mentioned
        - city: New city - only if mentioned
        - state: New state/province - only if mentioned
        - zip_code: New ZIP/postal code - only if mentioned
        - country: New country - only if mentioned
        - is_default: Whether to set as default - only if mentioned

        EXAMPLES:
        Input: "Update address 3 with new street: 456 Oak Avenue"
        Output: {{
            "address_id": 3,
            "street": "456 Oak Avenue"
        }}

        Input: "Edit my address ID 1: change city to Los Angeles and zip to 90210"
        Output: {{
            "address_id": 1,
            "city": "Los Angeles",
            "zip_code": "90210"
        }}

        Input: "Change address 2 to my default home address: 789 Pine St, Seattle WA 98101"
        Output: {{
            "address_id": 2,
            "type": "home",
            "street": "789 Pine St",
            "city": "Seattle",
            "state": "WA",
            "zip_code": "98101",
            "is_default": true
        }}

        RULES:
        1. address_id is REQUIRED and must be extracted from the message
        2. Only include fields that the user wants to change
        3. Leave fields as null if not mentioned for updating
        4. Normalize state names to standard abbreviations
        5. Clean up formatting (proper capitalization, remove extra spaces)
        """),
        ("user", "{query}")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)

        response = cast(EditAddressDetails, await llm.with_structured_output(EditAddressDetails).ainvoke(extraction_prompt.invoke({"query": user_message})))

        # Store extracted details in state
        state["address_id"] = response.address_id
        
        # Only include non-null fields in extracted_address
        extracted_address = {}
        if response.type is not None:
            extracted_address["type"] = response.type
        if response.street is not None:
            extracted_address["street"] = response.street
        if response.city is not None:
            extracted_address["city"] = response.city
        if response.state is not None:
            extracted_address["state"] = response.state
        if response.zip_code is not None:
            extracted_address["zip_code"] = response.zip_code
        if response.country is not None:
            extracted_address["country"] = response.country
        if response.is_default is not None:
            extracted_address["is_default"] = response.is_default
            
        state["extracted_address"] = extracted_address if extracted_address else None
        
        print(f"Successfully extracted edit details - Address ID: {state['address_id']}, Updates: {state['extracted_address']}")
        
    except Exception as e:
        print(f"Error in extract_edit_details_node: {e}")
        # Set error state if extraction fails
        state["address_id"] = None
        state["extracted_address"] = None
        state["error_message"] = f"Failed to extract edit details: {str(e)}"
    
    return state
