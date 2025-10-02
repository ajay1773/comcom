from app.graph.workflows.order_management.types import CheckoutUIProviderState
from langchain_core.runnables import RunnableConfig
from app.services.db.cart import cart_service
from app.services.db.product import product_service
from app.services.db.user import user_service
from app.services.widget_events import widget_event_emitter, WidgetEventType

async def prepare_ui_data_node(state: CheckoutUIProviderState, config: RunnableConfig | None = None) -> CheckoutUIProviderState:
    """Prepare all UI data needed for checkout form rendering."""
    
    try:
        user_id = state.get("user_id")
        checkout_type = state.get("checkout_type")
        
        if not user_id:
            state["error_message"] = "User authentication required for checkout"
            state["ui_data_success"] = False
            return state
        
        # Initialize UI data
        state["product_items"] = []
        state["saved_addresses"] = []
        state["allowed_payment_methods"] = ["cash_on_delivery", "credit_card"]
        state["total_amount"] = 0.0
        
        # Prepare product items based on checkout type
        if checkout_type == "cart":
            await prepare_cart_items(state, user_id)
        elif checkout_type == "direct":
            await prepare_direct_purchase_items(state)
        else:
            state["error_message"] = "Invalid checkout type"
            state["ui_data_success"] = False
            return state
        
        # Get saved addresses
        await prepare_saved_addresses(state, user_id)
        
        # Set success flag
        state["ui_data_success"] = True
        
        print(f"UI data prepared successfully for {checkout_type} checkout")
        print(f"Product items: {len(state.get('product_items', []))}")
        print(f"Saved addresses: {len(state.get('saved_addresses', []))}")
        print(f"Total amount: ${state.get('total_amount', 0):.2f}")
        
        return state
        
    except Exception as e:
        print(f"Error preparing UI data: {e}")
        state["error_message"] = f"Failed to prepare checkout data: {str(e)}"
        state["ui_data_success"] = False
        return state

async def prepare_cart_items(state: CheckoutUIProviderState, user_id: int):
    """Prepare cart items for UI display."""
    
    try:
        # Get cart items with product details
        cart_items = await cart_service.get_cart_items_with_product_details(user_id)
        
        if not cart_items:
            state["error_message"] = "Your cart is empty. Add items to cart before checkout."
            state["ui_data_success"] = False
            return
        
        # Convert cart items to UI format
        
        state["product_items"] = [item.model_dump() for item in cart_items]
        state["total_amount"] = sum(item.total_price for item in cart_items)
        
    except Exception as e:
        print(f"Error preparing cart items: {e}")
        state["error_message"] = f"Failed to load cart items: {str(e)}"
        state["ui_data_success"] = False

async def prepare_direct_purchase_items(state: CheckoutUIProviderState):
    """Prepare direct purchase item for UI display."""
    
    try:
        product_details = state.get("product_details", {})
        
        if not product_details:
            state["error_message"] = "Product details missing for direct purchase"
            state["ui_data_success"] = False
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
            state["ui_data_success"] = False
            return
        
        # Validate size if specified
        requested_size = product_details.get("size")
        if requested_size:
            available_sizes = found_product.available_sizes
            if available_sizes and requested_size not in available_sizes:
                state["error_message"] = f"Size '{requested_size}' not available for this product"
                state["ui_data_success"] = False
                return
        
        # Create UI item for direct purchase
        quantity = product_details.get("quantity", 1)
        unit_price = found_product.price
        total_price = unit_price * quantity
        
        ui_item = {
            "id": found_product.id,
            "name": found_product.name,
            "brand": found_product.brand,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "size": requested_size,
            "color": product_details.get("color"),
            "image_url": getattr(found_product, 'image_url', None),
            "description": getattr(found_product, 'description', None),
            "available_sizes": found_product.available_sizes
        }
        
        state["product_items"] = [ui_item]
        state["total_amount"] = total_price 
        
    except Exception as e:
        print(f"Error preparing direct purchase item: {e}")
        state["error_message"] = f"Product validation failed: {str(e)}"
        state["ui_data_success"] = False

async def prepare_saved_addresses(state: CheckoutUIProviderState, user_id: int):
    """Prepare saved addresses for UI display."""
    
    try:
        # Get user's saved addresses
        addresses = await user_service.get_user_addresses(user_id)
        
        if not addresses:
            state["error_message"] = "No saved addresses found. Please add a shipping address first."
            state["ui_data_success"] = False
            return
        
        # Convert addresses to UI format
        saved_addresses = []
        for addr in addresses:
            ui_address = {
                "id": addr.id,
                "street": addr.street,
                "city": addr.city,
                "state": addr.state,
                "zip_code": addr.zip_code,
                "country": getattr(addr, 'country', 'US'),
                "is_default": addr.is_default,
                "formatted_address": format_address_for_display(addr)
            }
            saved_addresses.append(ui_address)
        
        state["saved_addresses"] = saved_addresses
        
    except Exception as e:
        print(f"Error preparing saved addresses: {e}")
        state["error_message"] = f"Failed to load addresses: {str(e)}"
        state["ui_data_success"] = False

def format_address_for_display(address):
    """Format address for user-friendly display."""
    parts = []
    
    if address.street:
        parts.append(address.street)
    if address.city:
        parts.append(address.city)
    if address.state:
        parts.append(address.state)
    if address.zip_code:
        parts.append(address.zip_code)
    
    return ", ".join(parts) if parts else "Address details incomplete"
