"""Delete address from the database."""

from app.graph.workflows.user_management.types import DeleteAddressState
from app.services.db.user import user_service


async def delete_address_node(state: DeleteAddressState) -> DeleteAddressState:
    """Delete the address from the database."""
    
    try:
        # Get required data from state
        address_id = state.get("address_id")
        user_id = state.get("user_id")
        existing_address = state.get("existing_address")
        
        if not address_id or not user_id or not existing_address:
            state["address_delete_success"] = False
            state["error_message"] = "Missing required data for address deletion"
            return state
        
        was_default = existing_address.get("is_default", False)
        address_type = existing_address.get("type")
        
        # Delete address from database
        delete_success = await user_service.delete_user_address(address_id)
        
        if delete_success:
            state["address_delete_success"] = True
            state["error_message"] = None
            print(f"Successfully deleted address {address_id} for user {user_id}")
            
            # If the deleted address was default, set another address of the same type as default
            if was_default and address_type:
                try:
                    await user_service.set_first_address_as_default(user_id, address_type)
                    print(f"Set another {address_type} address as default for user {user_id}")
                except Exception as e:
                    print(f"Warning: Could not set another address as default: {e}")
                    # Don't fail the deletion if we can't set another as default
            
        else:
            state["address_delete_success"] = False
            state["error_message"] = "Failed to delete address from database"
            
    except Exception as e:
        print(f"Error in delete_address_node: {e}")
        state["address_delete_success"] = False
        state["error_message"] = f"Database error while deleting address: {str(e)}"
    
    return state
