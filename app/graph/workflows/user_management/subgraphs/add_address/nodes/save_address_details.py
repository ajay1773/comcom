"""Save address details to the database."""

from app.graph.workflows.user_management.types import AddAddressState
from app.services.db.user import user_service


async def save_address_details_node(state: AddAddressState) -> AddAddressState:
    """Save the extracted address details to the database."""
    
    try:
        # Get extracted address and user info
        extracted_address = state.get("extracted_address")
        user_id = state.get("user_id")
        
        if not extracted_address:
            state["address_save_success"] = False
            state["error_message"] = "No address details found to save"
            return state
            
        if not user_id:
            state["address_save_success"] = False
            state["error_message"] = "User not authenticated"
            return state
        
        # Prepare address data for database
        address_data = {
            "user_id": user_id,
            "type": extracted_address.get("type", "shipping"),
            "street": extracted_address.get("street", ""),
            "city": extracted_address.get("city", ""),
            "state": extracted_address.get("state", ""),
            "zip_code": extracted_address.get("zip_code", ""),
            "country": extracted_address.get("country", "US"),
            "is_default": extracted_address.get("is_default", False)
        }
        
        # Validate required fields
        required_fields = ["street", "city", "state", "zip_code"]
        missing_fields = [field for field in required_fields if not address_data.get(field)]
        
        if missing_fields:
            state["address_save_success"] = False
            state["error_message"] = f"Missing required address fields: {', '.join(missing_fields)}"
            return state
        
        # If this is set as default, unset other default addresses for this user
        if address_data["is_default"]:
            await user_service.unset_default_addresses(user_id, address_data["type"])
        
        # Save address to database
        saved_address = await user_service.create_user_address(address_data)
        
        if saved_address:
            state["address_save_success"] = True
            state["error_message"] = None
            print(f"Successfully saved address for user {user_id}: {saved_address}")
        else:
            state["address_save_success"] = False
            state["error_message"] = "Failed to save address to database"
            
    except Exception as e:
        print(f"Error in save_address_details_node: {e}")
        state["address_save_success"] = False
        state["error_message"] = f"Database error: {str(e)}"
    
    return state
