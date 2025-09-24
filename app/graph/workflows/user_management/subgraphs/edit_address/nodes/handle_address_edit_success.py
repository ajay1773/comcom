"""Handle successful address edit with LLM response."""

from app.graph.workflows.user_management.types import EditAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate

from app.services.db.user import user_service


async def handle_address_edit_success_node(state: EditAddressState) -> EditAddressState:
    """Generate success response for successfully edited address."""

    existing_address = state.get("existing_address", {}) if state.get("existing_address") else None
    address_id = state.get("address_id")
    user_id = state.get("user_id")
    
    # Create success response prompt
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant confirming a successful address update.

        Generate a friendly, concise confirmation message for the user.

        Guidelines:
        - Confirm that the address was successfully updated
        - Keep the tone positive and reassuring
        - Keep response to 1-2 sentences maximum
        - If it was set as default, mention that
        - Be conversational and helpful
        - Don't be overly detailed - keep it brief and friendly

        Context:
        - User's address has been successfully updated in their account
        - This will help them during future checkouts
        """),
        ("user", f"""Generate a success confirmation for updating the address
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
            is_default = existing_address.get('is_default', False)
            
            location_text = f" in {city}" if city else ""
            default_text = " and set as your default" if is_default else ""
            
            success_message = f"Perfect! Your {address_type} address{location_text} has been updated{default_text}."
        else:
            success_message = f"Address {address_id} has been successfully updated."

    # Set the success response
    state["workflow_output_text"] = success_message
    state["error_message"] = None

    # Prepare JSON response for frontend
    addresses = await user_service.get_user_addresses(user_id) if user_id else []
    state["workflow_widget_json"] = {
        "template": "user_addresses",
        "payload": {
            "message": {
                "text": "Your address has been successfully updated.",
                "type": "success"
            },
            "addresses": addresses,
            "suggested_actions": [
                "View all addresses",
                "Add another address",
                "Set a different default address"
            ]
        }
    }

    return state
