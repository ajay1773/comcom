"""Handle failed user profile details fetch operations."""

from app.graph.workflows.user_management.types import UserProfileState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_user_details_fetch_failure_node(state: UserProfileState) -> UserProfileState:
    """Handle failed user profile fetch operation with LLM-generated response."""

    # Generate contextual failure response using LLM
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant handling an error when trying to fetch user profile details.

        Generate a short one line friendly, apologetic response explaining that there was an issue retrieving their profile information.

        Guidelines:
        - Be apologetic but reassuring
        - Keep the response short and concise of 1-2 lines
        - Don't reveal technical details about the error

        Context:
        - Error occurred while fetching profile details
        - User was trying to view their profile information
        - Error message: {error_message}

        """),
        ("user", """Please generate a friendly response explaining the profile fetch error.""")
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
        print(f"Error in handle_user_details_fetch_failure_node: {e}")
        # Fallback failure message if LLM fails
        failure_message = "I'm sorry, but I'm having trouble retrieving your profile details right now. Please try again in a few moments, or let me know if you need help with something else."

    # Set failure response in workflow widget
    state["workflow_widget_json"] = {
        "template": "error_message",
        "payload": {
            "error_message": failure_message,
            "error_type": "profile_fetch_error",
            "suggested_actions": [
                "Try again later",
                "Contact customer support",
                "Continue shopping",
                "View your cart"
            ],
            "retry_available": True
        }
    }

    # Set LLM text response
    state["workflow_output_text"] = failure_message

    return state
