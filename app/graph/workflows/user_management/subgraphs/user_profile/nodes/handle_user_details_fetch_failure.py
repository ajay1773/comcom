"""Handle failed user profile details fetch operations."""

from app.graph.workflows.user_management.types import UserProfileState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_user_details_fetch_failure_node(state: UserProfileState) -> UserProfileState:
    """Handle failed user profile fetch operation with LLM-generated response."""

    # Generate contextual failure response using LLM
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a seasoned fashion consultant with deep expertise in style, fit, and trends. Your communication style is sophisticated yet approachable, like a personal stylist who genuinely cares about helping customers find perfect matches.

        Personality attributes:
        - Analytical and detail-oriented about product features
        - Educated in fabrics, sizing, and style combinations
        - Diplomatic when suggesting alternatives
        - Builds trust through knowledgeable recommendations
        - Uses fashion terminology appropriately but explains when needed
        - Focuses on helping customers discover their personal style

        You're not just selling products - you're curating experiences and building confidence.

        Handle an error when trying to access a client's style profile with professional care.
        Format your response in markdown for better readability.

        Generate a short, warm, apologetic response explaining the style profile access issue.

        Guidelines:
        - Be apologetic but reassuring with fashion consultant warmth
        - Keep the response short and concise (1-2 lines)
        - Don't reveal technical details about the error
        - Maintain your professional styling expertise
        - Show you still care about their style journey

        Context:
        - Error occurred while accessing style profile details
        - Client was trying to view their style profile information
        - Error message: {error_message}

        """),
        ("user", """Please generate a warm, professional response explaining the style profile access issue.""")
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
        failure_message = "**I apologize, but I'm having a small issue accessing your style profile right now.** Please try again in a moment, or *let me help you with something else while we resolve this.*"

    # Set LLM text response
    state["workflow_output_text"] = failure_message

    return state
