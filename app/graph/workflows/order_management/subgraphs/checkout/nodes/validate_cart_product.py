from app.graph.workflows.order_management.types import CheckoutState
from langchain_core.runnables import RunnableConfig
from app.services.db.cart import cart_service
from app.services.db.product import product_service

async def validate_cart_product_node(state: CheckoutState, config: RunnableConfig | None = None) -> CheckoutState:
    """Validate cart items or product for checkout."""
    
    try:
        user_id = state.get("user_id")
        checkout_type = state.get("checkout_type")
        
        if not user_id:
            state["error_message"] = "User authentication required for checkout"
            state["checkout_success"] = False
            return state
        
        if checkout_type == "cart":
            # Validate cart checkout
            await validate_cart_checkout(state, user_id)
        elif checkout_type == "direct":
            # Validate direct product purchase
            await validate_direct_purchase(state)
        else:
            state["error_message"] = "Invalid checkout type"
            state["checkout_success"] = False
            return state
        
        if not state.get("error_message"):
            state["current_step"] = "address"
            print(f"Validation successful for {checkout_type} checkout")
        
        return state
        
    except Exception as e:
        print(f"Error validating checkout: {e}")
        state["error_message"] = f"Validation failed: {str(e)}"
        state["checkout_success"] = False
        return state

async def validate_cart_checkout(state: CheckoutState, user_id: int):
    """Validate cart items for checkout."""
    
    try:
        # Get cart items with product details
        cart_items = await cart_service.get_cart_items_with_product_details(user_id)
        
        if not cart_items:
            state["error_message"] = "Your cart is empty. Add items to cart before checkout."
            state["checkout_success"] = False
            return
        total_amount = 0
        validated_items = []
        
        # Validate each cart item
        for item in cart_items:
            product_details = item.product_details
            
            # Check if product still exists and is available
            if not product_details:
                state["error_message"] = f"Product information missing for cart item"
                state["checkout_success"] = False
                return
            
            # Add to validated items with all necessary details for order creation
            validated_item = {
                "product_id": item.product_id,
                "name": product_details.title   ,
                "brand": product_details.brand,
                "quantity": item.quantity,
                "unit_price": product_details.price,
                "total_price": product_details.price * item.quantity,
                "size": item.size,
                "color": product_details.color
            }
            
            validated_items.append(validated_item)
            total_amount += item.total_price
        
        # Store validated cart items
        state["cart_items"] = validated_items
        state["total_amount"] = total_amount
        
        print(f"Cart validation successful: {len(validated_items)} items, total: ${total_amount}")
        
    except Exception as e:
        print(f"Cart validation error: {e}")
        state["error_message"] = f"Cart validation failed: {str(e)}"
        state["checkout_success"] = False

async def validate_direct_purchase(state: CheckoutState):
    """Validate direct product purchase."""
    
    try:
        product_details = state.get("product_details", {})
        
        if not product_details:
            state["error_message"] = "Product details missing for direct purchase"
            state["checkout_success"] = False
            return
        
        # Search for the product in the database
        search_criteria = {}
        if product_details.get("product_name"):
            search_criteria["name"] = product_details["product_name"]
        if product_details.get("brand"):
            search_criteria["brand"] = product_details["brand"]
        if product_details.get("color"):
            search_criteria["color"] = product_details["color"]
        
        # Get matching product
        found_product = await product_service.get_product(search_criteria)
        
        if not found_product:
            state["error_message"] = f"Product '{product_details.get('product_name', 'Unknown')}' not found or unavailable"
            state["checkout_success"] = False
            return
        
        # Validate size if specified
        requested_size = product_details.get("size")
        if requested_size:
            available_sizes = found_product.available_sizes
            if available_sizes and requested_size not in available_sizes:
                state["error_message"] = f"Size '{requested_size}' not available for this product"
                state["checkout_success"] = False
                return
        
        # Create cart items structure for direct purchase
        quantity = product_details.get("quantity", 1)
        unit_price = found_product.price  # Use price from the product
        total_price = unit_price * quantity
        
        cart_item = {
            "product_id": found_product.id,
            "name": found_product.title,
            "brand": found_product.brand,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "size": requested_size,
            "color": product_details.get("color")
        }
        
        # Store as cart items for consistent processing
        state["cart_items"] = [cart_item]
        state["total_amount"] = total_price
        
        print(f"Direct purchase validation successful: {found_product.title} - ${total_price}")
        
    except Exception as e:
        print(f"Direct purchase validation error: {e}")
        state["error_message"] = f"Product validation failed: {str(e)}"
        state["checkout_success"] = False
