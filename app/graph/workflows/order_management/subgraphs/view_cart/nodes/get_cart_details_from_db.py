

from app.graph.workflows.order_management.types import ViewCartState
from app.services.db.cart import cart_service

async def get_cart_details_from_db_node(state: ViewCartState) -> ViewCartState:
    """Get the cart details from the database."""

    user_id = state.get('user_id')
    cart_items = []

    try:
        if user_id:
            cart_items = await cart_service.get_cart_items_with_product_details(user_id)
        else:
            # No user ID - authentication required
            state['error_message'] = "Authentication required to view cart"
            state['cart_details'] = []
            return state

        # Set cart details in state
        state['cart_details'] = cart_items if cart_items else []
        state['error_message'] = None  # Clear any error message

    except Exception as e:
        # Handle database errors or other exceptions
        state['cart_details'] = []
        state['error_message'] = f"Unable to retrieve cart details: {str(e)}"

    return state