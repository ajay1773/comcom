from app.graph.workflows.order_management.types import CheckoutUIProviderState
from langchain_core.runnables import RunnableConfig
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.services.widget_events import widget_event_emitter, WidgetEventType
async def ui_failure_handler_node(state: CheckoutUIProviderState, config: RunnableConfig | None = None) -> CheckoutUIProviderState:
    """Handle UI data preparation failure scenarios."""
    
    try:
        error_message = state.get("error_message", "Unknown error occurred")
        checkout_type = state.get("checkout_type", "unknown")
        
        # Generate user-friendly error message using LLM
        failure_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a helpful e-commerce assistant handling a checkout preparation error.
                
                Generate a friendly, apologetic error message that:
                1. Acknowledges the issue without being overly technical
                2. Suggests helpful next steps based on the error type
                3. Maintains a supportive, solution-oriented tone
                4. Offers assistance or alternatives
                5. Keeps it brief and actionable
                
                Common error types and suggestions:
                - Cart empty: Suggest adding items to cart
                - Product unavailable: Suggest similar products or browsing
                - No addresses: Suggest adding a shipping address
                - Authentication: Suggest signing in
                
                Keep it conversational and under 3 sentences.
            """),
            ("user", f"Checkout preparation failed for {checkout_type} checkout. Error: {error_message}")
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({}))
        
        failure_message = str(response.content).strip()
        
        # Set workflow outputs
        state["workflow_output_text"] = failure_message
        
        # Prepare JSON response for frontend with suggested actions
        suggested_actions = get_suggested_actions_for_error(error_message or "")
        
        # widget_event_emitter.emit(
        #     WidgetEventType.CHECKOUT_UI_PROVIDER_DATA,
        #     {
        #         "error": error_message,
        #         "checkout_type": checkout_type,
        #         "suggested_actions": suggested_actions
        #     }
        # )
        
        print(f"UI data failure: {error_message}")
        
        return state
        
    except Exception as e:
        print(f"Error in UI failure handler: {e}")
        # Fallback error message
        state["workflow_output_text"] = "I'm sorry, there was an issue preparing your checkout. Please try again or contact support."
        # widget_event_emitter.emit(
        #     WidgetEventType.CHECKOUT_UI_PROVIDER_DATA,
        #     {
        #         "error": "Unexpected error occurred",
        #         "checkout_type": checkout_type or "unknown",
        #         "suggested_actions": ["Try again", "Contact support", "View cart"]
        #     }
        # )
        return state

def get_suggested_actions_for_error(error_message: str) -> list[str]:
    """Get contextual suggested actions based on error type."""
    
    error_lower = error_message.lower()
    
    if "empty" in error_lower or "no items" in error_lower:
        return ["Add items to cart", "Browse products", "View recommendations"]
    
    elif "address" in error_lower:
        return ["Add shipping address", "Update profile", "View account settings"]
    
    elif "product not found" in error_lower or "unavailable" in error_lower:
        return ["Search for similar products", "Browse categories", "Check availability"]
    
    elif "authentication" in error_lower or "sign in" in error_lower:
        return ["Sign in to your account", "Create new account", "Continue as guest"]
    
    else:
        return ["Try again", "View cart", "Contact support", "Browse products"]
