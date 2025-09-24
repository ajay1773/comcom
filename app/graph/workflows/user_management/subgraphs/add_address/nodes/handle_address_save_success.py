"""Handle successful address save with LLM response."""

from app.graph.workflows.user_management.types import AddAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_address_save_success_node(state: AddAddressState) -> AddAddressState:
    """Generate success response for successfully saved address."""

    extracted_address = state.get("extracted_address", {}) if state.get("extracted_address") else None
    
    # Create success response prompt
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant confirming a successful address save.

        Generate a friendly, concise confirmation message for the user.

        Guidelines:
        - Confirm that the address was successfully saved
        - Mention key details like address type (billing/shipping) and location
        - Keep the tone positive and reassuring
        - Keep response to 1-2 sentences maximum
        - If it's set as default, mention that as well
        - Be conversational and helpful

        Context:
        - User's address has been successfully saved to their account
        - This will help them during future checkouts
        """),
        ("user", f"""Generate a success confirmation for saving this address:
        
        Address Type: {extracted_address.get('type', 'shipping') if extracted_address else 'shipping'}
        Street: {extracted_address.get('street', '') if extracted_address else ''}
        City: {extracted_address.get('city', '') if extracted_address else ''}
        State: {extracted_address.get('state', '') if extracted_address else ''}
        ZIP: {extracted_address.get('zip_code', '') if extracted_address else ''}
        Country: {extracted_address.get('country', 'US') if extracted_address else 'US'}
        Is Default: {extracted_address.get('is_default', False) if extracted_address else False}
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
        address_type = extracted_address.get('type', 'shipping') if extracted_address else 'shipping'
        city = extracted_address.get('city', '') if extracted_address else ''
        is_default = extracted_address.get('is_default', False) if extracted_address else False
        
        default_text = " and set as your default" if is_default else ""
        location_text = f" in {city}, {state}" if city and state else ""
        
        success_message = f"Perfect! Your {address_type} address{location_text} has been saved{default_text}."

    # Set the success response
    state["workflow_output_text"] = success_message
    state["error_message"] = None

    return state
