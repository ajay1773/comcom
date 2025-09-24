"""Validate that the user can delete the address and fetch existing address data."""

from app.graph.workflows.user_management.types import DeleteAddressState
from app.services.db.user import user_service


async def validate_delete_permissions_node(state: DeleteAddressState) -> DeleteAddressState:
    """Validate that the user can delete the address and fetch existing address data."""
    
    try:
        address_id = state.get("address_id")
        user_id = state.get("user_id")
        
        if not address_id:
            state["address_delete_success"] = False
            state["error_message"] = "Address ID is required for deletion"
            return state
            
        if not user_id:
            state["address_delete_success"] = False
            state["error_message"] = "User not authenticated"
            return state
        
        # Fetch the existing address
        existing_address = await user_service.get_user_address_by_id(user_id, address_id)
        
        if not existing_address:
            state["address_delete_success"] = False
            state["error_message"] = f"Address with ID {address_id} not found or you don't have permission to delete it"
            return state
        
        # Store existing address data in state
        state["existing_address"] = {
            "id": existing_address.id,
            "user_id": existing_address.user_id,
            "type": existing_address.type,
            "street": existing_address.street,
            "city": existing_address.city,
            "state": existing_address.state,
            "zip_code": existing_address.zip_code,
            "country": existing_address.country,
            "is_default": existing_address.is_default,
            "created_at": str(existing_address.created_at) if existing_address.created_at else None,
            "updated_at": str(existing_address.updated_at) if existing_address.updated_at else None
        }
        
        # Check if this is the user's only address
        user_addresses = await user_service.get_user_addresses(user_id)
        if len(user_addresses) <= 1:
            state["address_delete_success"] = False
            state["error_message"] = "Cannot delete your only address. Please add another address first."
            return state
        
        # Optional: Check if this is the default address and warn user
        if existing_address.is_default:
            # We'll allow deletion but mention in the response that another address will become default
            print(f"Warning: Deleting default address {address_id}. Another address will be set as default.")
        
        print(f"Successfully validated delete permissions for address {address_id} for user {user_id}")
        
    except Exception as e:
        print(f"Error in validate_delete_permissions_node: {e}")
        state["address_delete_success"] = False
        state["error_message"] = f"Failed to validate delete permissions: {str(e)}"
    
    return state
