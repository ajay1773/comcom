"""Handle failed add to cart operations."""

from app.graph.workflows.order_management.types import AddToCartState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_failure_node(state: AddToCartState) -> AddToCartState:
    """Handle failed add to cart operation with LLM-generated response."""
    
    error_message = state.get("error_message", "Unknown error occurred")
    product_details = state.get("product_details", {})
    user_query = state.get("search_query", "")
    
    # Generate contextual failure response using LLM
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant handling delete-from-cart failures.
        
        Generate a friendly, empathetic response when deleting an item from cart fails.
        
        Guidelines:
        - Be understanding and apologetic
        - Explain the issue in simple, non-technical terms
        - Avoid technical jargon
        - Keep the message short and concise
        
        Context:
        - Product they tried to delete: {product_name} by {brand}
        - User's original request: {user_query}
        - Technical error: {error_message}
        
        Common issues and appropriate responses:
        - Authentication required: Guide them to sign in or create an account
        - Product not found: Suggest searching again or browsing
        - Missing information: Ask for more details
        - System errors: Apologize and suggest trying again
        - Other errors: Apologize and suggest trying again
        """),
        ("user", """Please generate a helpful response for this delete-from-cart failure that will guide the user to resolve the issue.""")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({
            "product_name": product_details.get("name", "the item"),
            "brand": product_details.get("brand", ""),
            "user_query": user_query,
            "error_message": error_message
        }))
        
        failure_message = str(response.content).strip()
        
    except Exception:
        # Fallback failure message if LLM fails
        if "authentication" in error_message.lower() or "user" in error_message.lower():
            failure_message = "I need you to be signed in to add items to your cart. Please sign in and try again."
        elif "missing" in error_message.lower() or "required" in error_message.lower():
            failure_message = "I couldn't find all the information needed to add this item. Please provide more details about the product you'd like to add."
        elif not product_details:
            failure_message = "I couldn't find that product in our inventory. Please try searching for it first or check the spelling."
        else:
            failure_message = "I encountered an issue adding the item to your cart. Please try again in a moment."
    
    # Determine recovery options based on error type
    if "authentication" in error_message.lower() or "user" in error_message.lower():
        recovery_options = ["Sign in to your account", "Create a new account"]
    elif not product_details:
        recovery_options = ["Search for products", "Browse categories", "Check spelling"]
    elif "missing" in error_message.lower():
        recovery_options = ["Provide product name and brand", "Search first then add"]
    else:
        recovery_options = ["Try again", "Refresh page", "Contact support"]
    
    # Set failure response in workflow widget
    state["workflow_widget_json"] = {
        "template": "error_message",
        "payload": {
            "error_type": "delete_from_cart_failure",
            "error_message": failure_message,
            "recovery_options": recovery_options,
            "workflow_name": "delete_from_cart"
        }
    }
    
    return state
