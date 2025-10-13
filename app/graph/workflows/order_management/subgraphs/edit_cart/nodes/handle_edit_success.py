from app.graph.workflows.order_management.types import EditCartState
from typing import Dict, Any, List


async def handle_edit_success_node(state: EditCartState) -> EditCartState:
    """
    LangGraph node for handling successful cart edit operations.
    Formats the success response with updated cart information.
    """
    edit_type = state.get("edit_type", "")
    matched_item = state.get("matched_cart_item", {})
    updated_cart_details = state.get("updated_cart_details", [])
    
    # Build a comprehensive success response
    product_name = matched_item.get("product_name", "item")
    
    # Calculate cart summary
    total_items = sum(item.quantity for item in updated_cart_details) if updated_cart_details else 0
    total_amount = sum(item.total_price for item in updated_cart_details) if updated_cart_details else 0.0
    
    # Format cart items for JSON response
    cart_items_json = []
    if updated_cart_details:
        for item in updated_cart_details:
            product = item.product_details
            cart_items_json.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.title if product else "Unknown",
                "brand": product.brand if product else "Unknown",
                "quantity": item.quantity,
                "size": item.size,
                "color": item.color,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "thumbnail": product.thumbnail if product else None
            })
    
    # Get the workflow output text (already set in apply_cart_edit)
    success_message = state.get("workflow_output_text", "Cart updated successfully")
    
    # Add cart summary to the message
    if total_items > 0:
        success_message += f"\n\nYour cart now has {total_items} item(s) for a total of ${total_amount:.2f}."
    else:
        success_message += "\n\nYour cart is now empty."
    
    # Create workflow output JSON
    workflow_output_json: Dict[str, Any] = {
        "success": True,
        "edit_type": edit_type,
        "edited_item": {
            "product_name": product_name,
            "previous_quantity": matched_item.get("quantity"),
            "previous_size": matched_item.get("size"),
            "previous_color": matched_item.get("color")
        },
        "cart_summary": {
            "total_items": total_items,
            "total_amount": total_amount,
            "items": cart_items_json
        }
    }
    
    state["workflow_output_text"] = success_message
    state["workflow_output_json"] = workflow_output_json
    state["error_message"] = None
    
    return state

