

from app.graph.workflows.order_management.types import AddToCartState
from app.services.db.cart import cart_service
from app.services.db.db import CartItemCreate
async def add_product_to_cart_node(state: AddToCartState) -> AddToCartState:
    """Add the product to the cart."""
    
    try:
        user_id = state.get("user_id", None)
        product_details = state.get("product_details", {})
        quantity = state.get("quantity", 1)

        # Validate basic requirements
        if user_id is None or not product_details:
            state["operation_success"] = False
            state["error_message"] = "Missing required information"
            return state

        # Create cart item
        cart_item = CartItemCreate(
            product_id=product_details.get("id", 0),
            quantity=quantity,
            unit_price=product_details.get("max_price", 10),
            size=state.get("size", None),
            color=state.get("color", None),
            unit=product_details.get("unit", "piece")
        )
        
        # Add item to cart
        await cart_service.add_item_to_cart(user_id, cart_item)
        
        # Get updated cart details
        cart_items = await cart_service.get_cart_items(user_id)
        
        # Convert cart items to dictionaries for state
        cart_details = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "size": item.size,
                "color": item.color,
                "unit": item.unit,
                "selected_options": item.selected_options,
                "added_at": item.added_at,
                "updated_at": item.updated_at
            }
            for item in cart_items
        ]
        
        # Set success flag and cart data
        state["operation_success"] = True
        state["cart_details"] = cart_details
        
        return state
        
    except Exception as e:
        # Set failure flag and error message
        state["operation_success"] = False
        state["error_message"] = str(e)
        return state