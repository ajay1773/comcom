

from app.graph.workflows.order_management.types import DeleteFromCartState
from app.services.db.cart import cart_service
from app.services.db.product import product_service


async def delete_product_from_cart_node (state: DeleteFromCartState) -> DeleteFromCartState:
    """Delete the product from the cart."""
    
    try:
        user_id = state.get("user_id", None)
        product_details = state.get("product_details", {})

        # Validate basic requirements
        if user_id is None or not product_details:
            state["cart_delete_success"] = False
            state["error_message"] = "Missing required information"
            return state

        saved_product_details = await product_service.get_product(product_details)

        if not saved_product_details:
            state["cart_delete_success"] = False
            state["error_message"] = "Product not found"
            return state
        
        # Remove item from cart
        await cart_service.remove_item_from_cart_by_id(user_id, saved_product_details["id"])
    
        
        # Set success flag and cart data
        state["cart_delete_success"] = True
        
        return state
        
    except Exception as e:
        # Set failure flag and error message
        state["cart_delete_success"] = False
        state["error_message"] = str(e)
        return state