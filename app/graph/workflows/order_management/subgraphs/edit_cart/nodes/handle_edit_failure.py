from app.graph.workflows.order_management.types import EditCartState
from typing import Dict, Any


async def handle_edit_failure_node(state: EditCartState) -> EditCartState:
    """
    LangGraph node for handling failed cart edit operations.
    Formats helpful error messages for the user.
    """
    error_message = state.get("error_message", "Failed to edit cart item")
    edit_type = state.get("edit_type", "unknown")
    target_reference = state.get("target_product_reference", "the item")
    
    # Create a user-friendly error message
    if "Could not identify" in error_message or "Could not find" in error_message:
        friendly_message = (
            f"I couldn't identify which item you're referring to ({target_reference}). "
            "Could you be more specific? You can view your cart to see all items."
        )
    elif "empty" in error_message.lower():
        friendly_message = "Your cart is empty. There are no items to edit."
    elif "not authenticated" in error_message.lower():
        friendly_message = "You need to be logged in to edit your cart."
    elif "Invalid quantity" in error_message:
        friendly_message = "Please specify a valid quantity (must be greater than 0)."
    elif "No properties specified" in error_message:
        friendly_message = "Please specify which property you'd like to update (size or color)."
    elif "Could not find replacement product" in error_message:
        friendly_message = error_message  # Already user-friendly
    else:
        friendly_message = f"I couldn't complete the cart edit: {error_message}"
    
    # Create workflow output JSON
    workflow_output_json: Dict[str, Any] = {
        "success": False,
        "error": error_message,
        "edit_type": edit_type,
        "target_reference": target_reference,
        "suggestions": [
            "View your cart to see all items",
            "Try being more specific about which item you want to edit",
            "Make sure the item is actually in your cart"
        ]
    }
    
    state["workflow_output_text"] = friendly_message
    state["workflow_output_json"] = workflow_output_json
    state["edit_success"] = False
    
    return state

