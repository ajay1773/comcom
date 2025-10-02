from app.graph.workflows.order_management.types import CheckoutState
from langchain_core.runnables import RunnableConfig
from app.services.db.user import user_service
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate

async def address_selection_node(state: CheckoutState, config: RunnableConfig | None = None) -> CheckoutState:
    """Handle address selection for checkout."""
    
    try:
        user_id = state.get("user_id")
        
        if not user_id:
            state["error_message"] = "User authentication required"
            state["checkout_success"] = False
            return state
        
        # Get user's saved addresses
        addresses = await user_service.get_user_addresses(user_id)
        
        if not addresses:
            # No saved addresses - need to collect address
            state["error_message"] = "No saved addresses found. Please add a shipping address first."
            state["checkout_success"] = False
            return state
        
        # Store available addresses
        state["available_addresses"] = addresses
        
        # Find default address or use the first one
        default_address = None
        for addr in addresses:
            if addr.is_default:
                default_address = addr
                break
        
        if not default_address and addresses:
            default_address = addresses[0]  # Use first address if no default
        
        if default_address:
            state["selected_address_id"] = default_address.id
            state["current_step"] = "payment"
            
            # Generate address confirmation message
            address_text = format_address_for_display(default_address)
            
            confirmation_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                    You are a helpful e-commerce assistant confirming the shipping address for checkout.
                    
                    Generate a brief, friendly message that:
                    1. Confirms the selected shipping address
                    2. Asks if the user wants to use this address or select a different one
                    3. Mentions that we'll proceed to payment next
                    
                    Keep it conversational and under 2 sentences.
                """),
                ("user", f"The selected shipping address is: {address_text}")
            ])
            
            llm = llm_service.get_llm_without_tools(disable_streaming=True)
            response = await llm.ainvoke(confirmation_prompt.invoke({}))
            
            confirmation_message = str(response.content).strip()
            
            # Set workflow output for streaming
            state["workflow_output_text"] = confirmation_message
            
            print(f"Address selected: ID {default_address.id} - {default_address.street}")
        else:
            state["error_message"] = "No valid address found for checkout"
            state["checkout_success"] = False
        
        return state
        
    except Exception as e:
        print(f"Error in address selection: {e}")
        state["error_message"] = f"Address selection failed: {str(e)}"
        state["checkout_success"] = False
        return state

def format_address_for_display(address):
    """Format address for user-friendly display."""
    parts = []
    
    if address.street:
        parts.append(address["street"])
    if address.get("city"):
        parts.append(address.city)
    if address.state:
        parts.append(address.state)
    if address.get("zip_code"):
        parts.append(address["zip_code"])
    
    return ", ".join(parts) if parts else "Address details incomplete"
