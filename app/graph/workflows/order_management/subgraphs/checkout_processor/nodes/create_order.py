from app.graph.workflows.order_management.types import CheckoutProcessorState
from langchain_core.runnables import RunnableConfig
from app.services.db.order import order_service
from app.services.db.cart import cart_service

async def create_order_node(state: CheckoutProcessorState, config: RunnableConfig | None = None) -> CheckoutProcessorState:
    """Create order and order items in the database."""
    
    try:
        user_id = state.get("user_id")
        cart_items = state.get("cart_items", [])
        selected_address_id = state.get("selected_address_id")
        payment_method = state.get("payment_method")
        payment_details = state.get("payment_details", {})
        total_amount = state.get("total_amount", 0)
        checkout_type = state.get("checkout_type")
        
        # Validate required data
        if not user_id:
            state["error_message"] = "User authentication required"
            state["checkout_success"] = False
            return state
        
        if not cart_items:
            state["error_message"] = "No items to create order"
            state["checkout_success"] = False
            return state
        
        if total_amount <= 0:
            state["error_message"] = "Invalid order total"
            state["checkout_success"] = False
            return state
        
        if not selected_address_id:
            state["error_message"] = "Shipping address required"
            state["checkout_success"] = False
            return state
        
        # Prepare order notes with payment and checkout info
        order_notes = f"Checkout type: {checkout_type}, Payment: {payment_method}"
        if payment_details.get("transaction_id"):
            order_notes += f", Transaction: {payment_details['transaction_id']}"
        
        # Create the order using OrderService
        order_result = await order_service.create_order(
            user_id=user_id,
            cart_items=cart_items,
            shipping_address_id=selected_address_id,
            payment_method=payment_method,
            notes=order_notes
        )
        
        if not order_result:
            state["error_message"] = "Failed to create order"
            state["checkout_success"] = False
            return state
        
        # Store order details in state
        state["order_id"] = order_result["order_id"]
        state["order_number"] = order_result["order_number"]
        state["checkout_success"] = True
        
        # Clear cart if this was a cart checkout
        if checkout_type == "cart":
            try:
                await cart_service.clear_cart(user_id)
                print(f"Cart cleared for user {user_id}")
            except Exception as e:
                print(f"Warning: Failed to clear cart after order creation: {e}")
                # Don't fail the order creation if cart clearing fails
        
        print(f"Order created successfully: {order_result['order_number']} - ${total_amount:.2f}")
        
        return state
        
    except Exception as e:
        print(f"Error creating order: {e}")
        state["error_message"] = f"Order creation failed: {str(e)}"
        state["checkout_success"] = False
        return state
