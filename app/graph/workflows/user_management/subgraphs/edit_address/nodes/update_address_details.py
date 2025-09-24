"""Update address details in the database."""

from app.graph.workflows.user_management.types import EditAddressState
from app.services.db.user import user_service


async def update_address_details_node(state: EditAddressState) -> EditAddressState:
    """Update the address details in the database."""
    
    try:
        # Get required data from state
        address_id = state.get("address_id")
        user_id = state.get("user_id")
        extracted_updates = state.get("extracted_address")
        existing_address = state.get("existing_address")
        
        if not address_id or not user_id or not existing_address:
            state["address_edit_success"] = False
            state["error_message"] = "Missing required data for address update"
            return state
            
        if not extracted_updates:
            state["address_edit_success"] = False
            state["error_message"] = "No updates specified for the address"
            return state
        
        # Merge existing address data with updates
        updated_address_data = {
            "user_id": user_id,
            "type": extracted_updates.get("type", existing_address.get("type")),
            "street": extracted_updates.get("street", existing_address.get("street")),
            "city": extracted_updates.get("city", existing_address.get("city")),
            "state": extracted_updates.get("state", existing_address.get("state")),
            "zip_code": extracted_updates.get("zip_code", existing_address.get("zip_code")),
            "country": extracted_updates.get("country", existing_address.get("country")),
            "is_default": extracted_updates.get("is_default", existing_address.get("is_default"))
        }
        
        # Validate required fields after merging
        required_fields = ["street", "city", "state", "zip_code"]
        missing_fields = [field for field in required_fields if not updated_address_data.get(field)]
        
        if missing_fields:
            state["address_edit_success"] = False
            state["error_message"] = f"Cannot update address - missing required fields: {', '.join(missing_fields)}"
            return state
        
        # If setting as default, unset other default addresses for this user and type
        if updated_address_data.get("is_default") and not existing_address.get("is_default"):
            await user_service.unset_default_addresses(user_id, updated_address_data["type"])
        
        # Update address in database
        updated_address = await user_service.update_user_address(address_id, updated_address_data)
        
        if updated_address and state["existing_address"]:
            state["address_edit_success"] = True
            state["error_message"] = None
            print(f"Successfully updated address {address_id} for user {user_id}")
            
            # Update existing_address in state with new values for response
            state["existing_address"].update({
                "type": updated_address.type,
                "street": updated_address.street,
                "city": updated_address.city,
                "state": updated_address.state,
                "zip_code": updated_address.zip_code,
                "country": updated_address.country,
                "is_default": updated_address.is_default,
                "updated_at": str(updated_address.updated_at) if updated_address.updated_at else None
            })
        else:
            state["address_edit_success"] = False
            state["error_message"] = "Failed to update address in database"
            
    except Exception as e:
        print(f"Error in update_address_details_node: {e}")
        state["address_edit_success"] = False
        state["error_message"] = f"Database error while updating address: {str(e)}"
    
    return state
