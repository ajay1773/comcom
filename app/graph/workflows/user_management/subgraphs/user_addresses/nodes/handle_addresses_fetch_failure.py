"""Handle failed user addresses fetch operations."""

from app.graph.workflows.user_management.types import UserAddressesState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_addresses_fetch_failure_node(state: UserAddressesState) -> UserAddressesState:
    """Handle failed user addresses fetch operation with LLM-generated response."""

    # Generate contextual failure response using LLM
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant handling an error when trying to fetch user addresses.

        Generate a friendly, apologetic response explaining that there was an issue retrieving their saved addresses.

        Guidelines:
        - Be apologetic but reassuring
        - Explain that there was a technical issue
        - Suggest alternative actions they can take
        - Keep the tone helpful and supportive
        - Offer to help with other tasks
        - Don't reveal technical details about the error

        Context:
        - Error occurred while fetching saved addresses
        - User was trying to view their addresses
        - Error message: {error_message}

        """),
        ("user", """Please generate a friendly response explaining the addresses fetch error.""")
    ])

    try:
        error_message = state.get("error_message", "Unknown error occurred")

        # Generate LLM response
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({
            "error_message": error_message
        }))

        failure_message = str(response.content).strip()

    except Exception as e:
        print(f"Error in handle_addresses_fetch_failure_node: {e}")
        # Fallback failure message if LLM fails
        failure_message = "I'm sorry, but I'm having trouble retrieving your saved addresses right now. Please try again in a few moments, or let me know if you need help with something else."

    # Set failure response in workflow widget
    state["workflow_widget_json"] = {
        "template": "error_message",
        "payload": {
            "error_message": failure_message,
            "error_type": "addresses_fetch_error",
            "suggested_actions": [
                "Try again later",
                "Add a new address",
                "Contact customer support",
                "Continue shopping"
            ],
            "retry_available": True
        }
    }

    # Set LLM text response
    state["workflow_output_text"] = failure_message

    return state
