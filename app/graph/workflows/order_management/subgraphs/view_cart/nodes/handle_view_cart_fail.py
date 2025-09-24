"""Handle failed view cart operations."""

from app.graph.workflows.order_management.types import ViewCartState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_view_cart_fail_node(state: ViewCartState) -> ViewCartState:
    """Handle failed view cart operation with LLM-generated response."""

    error_message = state.get("error_message", "Unable to retrieve cart details")
    user_query = state.get("search_query", "")

    # Generate contextual failure response using LLM
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant handling view cart failures.

        Generate a friendly, empathetic response when viewing cart contents fails.

        Guidelines:
        - Be understanding and helpful
        - Explain the issue in simple terms
        - Provide clear next steps for the user
        - Keep the tone conversational and reassuring

        Context:
        - User's original request: {user_query}
        - Technical error: {error_message}

        Common issues and appropriate responses:
        - Authentication required: Guide them to sign in or create an account
        - Session expired: Ask them to sign in again
        - Database errors: Apologize and suggest trying again
        - No cart found: Suggest they start shopping
        - Other errors: Apologize and suggest trying again or contacting support
        """),
        ("user", """Please generate a helpful response for this cart viewing failure that will guide the user to resolve the issue.""")
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
            failure_message = "I need you to be signed in to view your cart. Please sign in and try again."
        elif "session" in error_message.lower() if error_message else False or "expired" in error_message.lower() if error_message else False:
            failure_message = "Your session has expired. Please sign in again to view your cart."
        elif "database" in error_message.lower() if error_message else False or "connection" in error_message.lower() if error_message else False:
            failure_message = "I'm having trouble accessing your cart right now. Please try again in a moment."
        elif "not found" in error_message.lower() if error_message else False or "empty" in error_message.lower() if error_message else False:
            failure_message = "You don't have any items in your cart yet. Start browsing to add some products!"
        else:
            failure_message = "I encountered an issue showing your cart. Please try again or contact support if the problem continues."

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
    state["workflow_widget_json"] = {
        "template": "error_message",
        "payload": {
            "error_type": "view_cart_failure",
            "error_message": failure_message,
            "recovery_options": recovery_options,
            "workflow_name": "view_cart"
        }
    }

    return state
