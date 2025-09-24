"""Handle successful user addresses fetch operations."""

from app.graph.workflows.user_management.types import UserAddressesState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_addresses_fetch_success_node(state: UserAddressesState) -> UserAddressesState:
    """Handle successful user addresses fetch operation with LLM-generated response."""

    # Generate contextual success response using LLM
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant showing a user their saved addresses.

        Generate a friendly, informative response displaying their saved addresses.

        Guidelines:
        - Be welcoming and helpful
        - Show a summary of their saved addresses
        - Mention how many addresses they have and types (billing/shipping)
        - If they have a default address, mention it
        - Keep the tone conversational and helpful
        - Keep the response concise but informative
        - If no addresses, encourage them to add one

        Context:
        - Number of addresses: {address_count}
        - Has addresses: {has_addresses}
        - Has default address: {has_default}
        - Address types: {address_types}

        """),
        ("user", """Please generate a friendly response showing the user's saved addresses.""")
    ])

    try:
        user_addresses = state.get("user_addresses", [])
        
        # Prepare data for LLM
        address_count = len(user_addresses)
        has_addresses = address_count > 0
        has_default = any(addr.is_default for addr in user_addresses) if user_addresses else False
        
        # Get unique address types
        address_types = list(set(addr.type for addr in user_addresses)) if user_addresses else []
        address_types_str = ", ".join(address_types) if address_types else "None"

        # Generate LLM response
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({
            "address_count": address_count,
            "has_addresses": "Yes" if has_addresses else "No",
            "has_default": "Yes" if has_default else "No",
            "address_types": address_types_str
        }))

        success_message = str(response.content).strip()

    except Exception as e:
        print(f"Error in handle_addresses_fetch_success_node: {e}")
        # Fallback success message if LLM fails
        address_count = len(user_addresses)
        if address_count > 0:
            success_message = f"Here are your {address_count} saved address(es). You can manage them or add new ones as needed."
        else:
            success_message = "You don't have any saved addresses yet. Would you like to add one to make checkout faster?"

    # Convert addresses to dictionaries for JSON serialization
    addresses_dict = []
    for address in user_addresses:
        addr_dict = {
            "id": address.id,
            "type": address.type,
            "street": address.street,
            "city": address.city,
            "state": address.state,
            "zip_code": address.zip_code,
            "country": address.country,
            "is_default": address.is_default,
            "full_address": f"{address.street}, {address.city}, {address.state} {address.zip_code}, {address.country}"
        }
        addresses_dict.append(addr_dict)

    # Set success response in workflow widget
    state["workflow_widget_json"] = {
        "template": "user_addresses",
        "payload": {
            "addresses": addresses_dict,
        }
    }

    # Set LLM text response
    state["workflow_output_text"] = success_message

    return state
