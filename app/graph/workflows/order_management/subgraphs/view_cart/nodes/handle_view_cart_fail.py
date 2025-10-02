"""Handle failed view cart operations."""

from app.graph.workflows.order_management.types import ViewCartState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.services.widget_events import widget_event_emitter, WidgetEventType


async def handle_view_cart_fail_node(state: ViewCartState) -> ViewCartState:
    """Handle failed view cart operation with LLM-generated response."""

    error_message = state.get("error_message", "Unable to retrieve cart details")
    user_query = state.get("search_query", "")

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

        Handle view cart failures with fashion consultant care and professionalism.
        Format your response in markdown for better readability.

        Generate a warm, empathetic response when viewing their curated collection fails.

        Guidelines:
        - Be understanding and helpful with fashion consultant warmth
        - Explain the issue in simple, elegant terms
        - Provide clear next steps with your professional guidance
        - Keep the tone conversational, reassuring, and style-focused

        Context:
        - Client's style request: {user_query}
        - Technical issue: {error_message}

        Common issues and appropriate fashion consultant responses:
        - Authentication required: Guide them to access their style profile
        - Session expired: Ask them to sign in again to their style account
        - Database errors: Apologize professionally and suggest trying again
        - No cart found: Suggest they start curating their style collection
        - Other errors: Apologize with consultant care and suggest alternatives
        """),
        ("user", """Please generate a helpful, fashion-focused response for this style collection viewing issue that will guide the client to resolve it.""")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({
            "user_query": user_query,
            "error_message": error_message
        }))

        failure_message = str(response.content).strip()

    except Exception:
        # Fallback failure message if LLM fails
        if "authentication" in error_message.lower() if error_message else False or "user" in error_message.lower() if error_message else False:
            failure_message = "**I'd love to show you your curated collection!** Please access your style profile first, then we can view your selections together."
        elif "session" in error_message.lower() if error_message else False or "expired" in error_message.lower() if error_message else False:
            failure_message = "**Your style session has expired.** Please sign in again to access your curated collection. *I'm here to help once you're back!*"
        elif "database" in error_message.lower() if error_message else False or "connection" in error_message.lower() if error_message else False:
            failure_message = "**I'm having a small issue accessing your style collection right now.** Please try again in a moment - your curated pieces are worth the wait!"
        elif "not found" in error_message.lower() if error_message else False or "empty" in error_message.lower() if error_message else False:
            failure_message = "**Your style collection is ready for curation!** Let's discover some amazing pieces that reflect your unique taste. *What kind of look are you envisioning?*"
        else:
            failure_message = "**I encountered a small hiccup while accessing your style collection.** Please try again, or *let me help you discover new pieces while we resolve this.*"

    # Determine recovery options based on error type
    if "authentication" in error_message.lower() if error_message else False or "user" in error_message.lower() if error_message else False:
        recovery_options = ["Sign in to your account", "Create a new account"]
    elif "session" in error_message.lower() if error_message else False:
        recovery_options = ["Sign in again", "Continue shopping as guest"]
    elif "database" in error_message.lower() if error_message else False:
        recovery_options = ["Try again", "Refresh page", "Contact support"]
    else:
        recovery_options = ["Try again", "Browse products", "Contact support"] if error_message else None

    # Set failure response in workflow widget
        widget_event_emitter.emit(
            WidgetEventType.VIEW_CART_FAILURE,
            {
            "cart_items": [],
            "cart_summary": {
                "item_count": 0,
                "total_items": 0,
                "total_value": 0
            },
            "success_message": failure_message,
            "recovery_options": recovery_options
            }
        )
    
    return state
