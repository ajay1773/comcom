from app.graph.workflows.order_management.types import EditCartState
from app.services.db.cart import cart_service
from app.services.db.product import product_service


async def apply_cart_edit_node(state: EditCartState) -> EditCartState:
    """
    LangGraph node for applying the cart edit operation.
    
    Handles different edit types:
    - remove: Delete the item from cart
    - update_quantity: Change the quantity
    - update_properties: Change size/color
    - replace: Remove old item and add new one
    """
    try:
        user_id = state.get("user_id", None)
        edit_type = state.get("edit_type", None)
        cart_item_id = state.get("cart_item_id", None)
        matched_item = state.get("matched_cart_item", None)
        
        if user_id is None or edit_type is None or cart_item_id is None:
            state["edit_success"] = False
            state["error_message"] = "Missing required information for edit operation"
            return state
        
        # Execute the appropriate edit operation
        if edit_type == "remove":
            success = await cart_service.remove_cart_item_by_cart_item_id(user_id, cart_item_id)
            if success:
                state["edit_success"] = True
                state["workflow_output_text"] = f"Successfully removed {matched_item.get('product_name', 'item')} from your cart."
            else:
                state["edit_success"] = False
                state["error_message"] = "Failed to remove item from cart"
        
        elif edit_type == "update_quantity":
            new_quantity = state.get("new_quantity", None)
            if new_quantity is None or new_quantity <= 0:
                state["edit_success"] = False
                state["error_message"] = "Invalid quantity specified"
                return state
            
            updated_item = await cart_service.update_item_quantity(user_id, cart_item_id, new_quantity)
            if updated_item:
                state["edit_success"] = True
                state["workflow_output_text"] = f"Updated {matched_item.get('product_name', 'item')} quantity to {new_quantity}."
            else:
                state["edit_success"] = False
                state["error_message"] = "Failed to update item quantity"
        
        elif edit_type == "update_properties":
            new_size = state.get("new_size", None)
            new_color = state.get("new_color", None)
            
            if new_size is None and new_color is None:
                state["edit_success"] = False
                state["error_message"] = "No properties specified to update"
                return state
            
            updated_item = await cart_service.update_cart_item_properties(
                user_id, 
                cart_item_id,
                size=new_size,
                color=new_color
            )
            
            if updated_item:
                changes = []
                if new_size:
                    changes.append(f"size to {new_size}")
                if new_color:
                    changes.append(f"color to {new_color}")
                
                state["edit_success"] = True
                state["workflow_output_text"] = f"Updated {matched_item.get('product_name', 'item')} - changed {' and '.join(changes)}."
            else:
                state["edit_success"] = False
                state["error_message"] = "Failed to update item properties"
        
        elif edit_type == "replace":
            replacement_product = state.get("replacement_product", None)
            
            if not replacement_product:
                state["edit_success"] = False
                state["error_message"] = "No replacement product specified"
                return state
            
            replacement_name = replacement_product.get("name", "")
            replacement_brand = replacement_product.get("brand", "")
            
            # Search for the replacement product
            search_filters = {}
            if replacement_brand:
                search_filters["brand"] = replacement_brand
            
            products = await product_service.search_products(
                query=replacement_name,
                filters=search_filters,
                limit=1
            )
            
            if not products:
                state["edit_success"] = False
                state["error_message"] = f"Could not find replacement product: {replacement_name}"
                return state
            
            replacement_product_details = products[0]
            
            # Remove old item
            remove_success = await cart_service.remove_cart_item_by_cart_item_id(user_id, cart_item_id)
            
            if not remove_success:
                state["edit_success"] = False
                state["error_message"] = "Failed to remove original item"
                return state
            
            # Add new item with same quantity
            from app.services.db.db import CartItemCreate
            
            original_quantity = matched_item.get("quantity", 1)
            
            new_cart_item = CartItemCreate(
                product_id=replacement_product_details.id,
                quantity=original_quantity,
                unit_price=replacement_product_details.price,
                size=state.get("new_size", None),  # Allow size specification during replacement
                color=state.get("new_color", None),  # Allow color specification during replacement
                unit=replacement_product_details.unit
            )
            
            await cart_service.add_item_to_cart(user_id, new_cart_item)
            
            state["edit_success"] = True
            state["workflow_output_text"] = (
                f"Successfully replaced {matched_item.get('product_name', 'item')} "
                f"with {replacement_product_details.title}."
            )
        
        else:
            state["edit_success"] = False
            state["error_message"] = f"Unknown edit type: {edit_type}"
            return state
        
        # Get updated cart details for response
        if state.get("edit_success", False):
            updated_cart_items = await cart_service.get_cart_items_with_product_details(user_id)
            state["updated_cart_details"] = updated_cart_items
        
        return state
        
    except Exception as e:
        state["edit_success"] = False
        state["error_message"] = f"Error applying cart edit: {str(e)}"
        return state

