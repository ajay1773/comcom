"""Handle successful address delete with LLM response."""

from app.graph.workflows.user_management.types import DeleteAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate

from app.services.db.user import user_service


async def handle_address_delete_success_node(state: DeleteAddressState) -> DeleteAddressState:
    """Generate success response for successfully deleted address."""

    existing_address = state.get("existing_address", {}) if state.get("existing_address") else None
    address_id = state.get("address_id")
    user_id = state.get("user_id")
    
    # Create success response prompt
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant confirming a successful address deletion.

        Generate a friendly, concise confirmation message for the user.

        Guidelines:
        - Confirm that the address was successfully deleted
        - Mention key details like address type and location that was removed
        - Keep the tone positive and reassuring
        - Keep response to 1-2 sentences maximum
        - If it was a default address, mention that another address has been set as default
        - Be conversational and helpful
        - Don't be overly detailed - keep it brief and friendly

        Context:
        - User's address has been successfully removed from their account
        - If it was their default address, another one has been automatically set as default
        """),
        ("user", f"""Generate a success confirmation for deleting this address:
        
        Address ID: {address_id}
        Address Type: {existing_address.get('type', 'address') if existing_address else 'address'}
        Street: {existing_address.get('street', '') if existing_address else ''}
        City: {existing_address.get('city', '') if existing_address else ''}
        State: {existing_address.get('state', '') if existing_address else ''}
        ZIP: {existing_address.get('zip_code', '') if existing_address else ''}
        Was Default: {existing_address.get('is_default', False) if existing_address else False}
        """)
    ])

    try:
        # Generate success message using LLM
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({}))
        
        success_message = str(response.content).strip()

    except Exception as e:
        print(f"Error generating success message: {e}")
        # Fallback success message
        if existing_address:
            address_type = existing_address.get('type', 'address')
            city = existing_address.get('city', '')
            was_default = existing_address.get('is_default', False)
            
            location_text = f" in {city}" if city else ""
            default_text = " Another address has been set as your default." if was_default else ""
            
            success_message = f"Perfect! Your {address_type} address{location_text} has been deleted.{default_text}"
        else:
            success_message = f"Address {address_id} has been successfully deleted from your account."

    # Set the success response
    state["workflow_output_text"] = success_message
    state["error_message"] = None

    addresses = await user_service.get_user_addresses(user_id) if user_id else []
    # Prepare JSON response for frontend
    state["workflow_widget_json"] = {
        "template": "user_addresses",
        "message": {
            "text": "Address deleted successfully",
            "type": "success"
        },
        "addresses": addresses,
    }

    return state
