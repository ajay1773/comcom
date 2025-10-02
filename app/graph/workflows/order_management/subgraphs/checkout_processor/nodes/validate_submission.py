from app.graph.workflows.order_management.types import CheckoutProcessorState
from langchain_core.runnables import RunnableConfig
from app.services.db.user import user_service
from app.services.db.cart import cart_service
from app.services.db.product import product_service

async def validate_submission_node(state: CheckoutProcessorState, config: RunnableConfig | None = None) -> CheckoutProcessorState:
    """Validate the checkout submission details."""
    
    try:
        user_id = state.get("user_id")
        selected_address_id = state.get("selected_address_id")
        payment_method = state.get("payment_method")
        payment_details = state.get("payment_details", {})
        checkout_type = state.get("checkout_type")
        
        
        # Validate user authentication
        if not user_id:
            state["error_message"] = "User authentication required for checkout"
            state["checkout_success"] = False
            return state
        
        # Validate address selection
        await validate_address_selection(state, user_id, selected_address_id)
        if state.get("error_message"):
            return state
        
        # Validate payment method and details
        await validate_payment_details(state, payment_method, payment_details or {})
        if state.get("error_message"):
            return state
        
        # Validate and prepare cart items based on checkout type
        if checkout_type == "cart":
            await validate_cart_items(state, user_id)
        elif checkout_type == "direct":
            await validate_direct_purchase_items(state)
        else:
            state["error_message"] = "Invalid checkout type"
            state["checkout_success"] = False
            return state
        
        if not state.get("error_message"):
            print(f"Submission validation successful for {checkout_type} checkout")
        
        return state
        
    except Exception as e:
        print(f"Error validating submission: {e}")
        state["error_message"] = f"Validation failed: {str(e)}"
        state["checkout_success"] = False
        return state

async def validate_address_selection(state: CheckoutProcessorState, user_id: int, selected_address_id: int | None):
    """Validate the selected address."""
    
    try:
        if not selected_address_id:
            state["error_message"] = "Please select a shipping address"
            state["checkout_success"] = False
            return
        
        # Get user's addresses and verify the selected one exists
        addresses = await user_service.get_user_addresses(user_id)
        
        if not addresses:
            state["error_message"] = "No saved addresses found. Please add a shipping address first."
            state["checkout_success"] = False
            return
        
        # Check if selected address exists
        selected_address = None
        for addr in addresses:
            if addr.id == selected_address_id:
                selected_address = addr
                break
        
        if not selected_address:
            state["error_message"] = f"Selected address (ID: {selected_address_id}) not found"
            state["checkout_success"] = False
            return
        
        print(f"Address validation successful: ID {selected_address_id}")
        
    except Exception as e:
        print(f"Address validation error: {e}")
        state["error_message"] = f"Address validation failed: {str(e)}"
        state["checkout_success"] = False

async def validate_payment_details(state: CheckoutProcessorState, payment_method: str | None, payment_details: dict):
    """Validate payment method and details."""
    
    try:
        if not payment_method:
            state["error_message"] = "Please select a payment method"
            state["checkout_success"] = False
            return
        
        # Validate allowed payment methods
        allowed_methods = ["cash_on_delivery", "credit_card"]
        if payment_method not in allowed_methods:
            state["error_message"] = f"Invalid payment method. Allowed: {', '.join(allowed_methods)}"
            state["checkout_success"] = False
            return
        
        # For credit card, validate card details
        if payment_method == "credit_card":
            card_number = payment_details.get("card_number")
            card_expiry = payment_details.get("card_expiry")
            card_cvv = payment_details.get("card_cvv")
            card_holder_name = payment_details.get("card_holder_name")
            
            if not card_number:
                state["error_message"] = "Credit card number is required"
                state["checkout_success"] = False
                return
            
            if not card_expiry:
                state["error_message"] = "Credit card expiry date is required"
                state["checkout_success"] = False
                return
            
            if not card_cvv:
                state["error_message"] = "Credit card CVV is required"
                state["checkout_success"] = False
                return
            
            if not card_holder_name:
                state["error_message"] = "Cardholder name is required"
                state["checkout_success"] = False
                return
            
            # Basic card number validation (length check)
            if len(card_number.replace(" ", "").replace("-", "")) < 13:
                state["error_message"] = "Invalid credit card number"
                state["checkout_success"] = False
                return
        
        print(f"Payment validation successful: {payment_method}")
        
    except Exception as e:
        print(f"Payment validation error: {e}")
        state["error_message"] = f"Payment validation failed: {str(e)}"
        state["checkout_success"] = False

async def validate_cart_items(state: CheckoutProcessorState, user_id: int):
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
                "name": product_details.name,
                "brand": product_details.brand,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "size": item.size,
                "color": item.color
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

async def validate_direct_purchase_items(state: CheckoutProcessorState):
    """Validate direct purchase items."""
    
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
        unit_price = found_product.price
        total_price = unit_price * quantity
        
        cart_item = {
            "product_id": found_product.id,
            "name": found_product.name,
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
        
        print(f"Direct purchase validation successful: {found_product.name} - ${total_price}")
        
    except Exception as e:
        print(f"Direct purchase validation error: {e}")
        state["error_message"] = f"Product validation failed: {str(e)}"
        state["checkout_success"] = False
