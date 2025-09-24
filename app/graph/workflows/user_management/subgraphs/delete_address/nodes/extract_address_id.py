"""Extract address ID from user prompt using LLM with structured output."""

from typing import cast
from app.graph.workflows.user_management.types import DeleteAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


class DeleteAddressDetails(BaseModel):
    """Structured address deletion details extracted from user input."""
    address_id: int


async def extract_address_id_node(state: DeleteAddressState) -> DeleteAddressState:
    """Extract address ID from user message using LLM."""
    
    user_message = state.get("search_query", "")

    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert address deletion assistant for an e-commerce system.
        Extract the address ID that the user wants to delete from their message.

        TASK:
        Extract the address ID from user messages about deleting addresses.
        - address_id: The ID of the address to delete (REQUIRED)

        EXAMPLES:
        Input: "Delete address 3"
        Output: {{
            "address_id": 3
        }}

        Input: "Remove my address with ID 7"
        Output: {{
            "address_id": 7
        }}

        Input: "Delete address number 12 please"
        Output: {{
            "address_id": 12
        }}

        Input: "I want to remove address 5 from my account"
        Output: {{
            "address_id": 5
        }}

        RULES:
        1. address_id is REQUIRED and must be extracted from the message
        2. Look for patterns like "address 3", "ID 7", "address number 12", etc.
        3. The address_id must be a positive integer
        4. If no clear address ID is found, the extraction should fail
        """),
        ("user", "{query}")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)

        response = cast(DeleteAddressDetails, await llm.with_structured_output(DeleteAddressDetails).ainvoke(extraction_prompt.invoke({"query": user_message})))

        # Store extracted address ID in state
        state["address_id"] = response.address_id
        
        print(f"Successfully extracted address ID for deletion: {state['address_id']}")
        
    except Exception as e:
        print(f"Error in extract_address_id_node: {e}")
        # Set error state if extraction fails
        state["address_id"] = None
        state["error_message"] = f"Failed to extract address ID: {str(e)}"
    
    return state
