from app.graph.workflows.order_management.types import CheckoutState
from langchain_core.runnables import RunnableConfig
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate

async def checkout_failure_handler_node(state: CheckoutState, config: RunnableConfig | None = None) -> CheckoutState:
    """Handle checkout failure scenarios."""
    
    try:
        error_message = state.get("error_message", "Unknown checkout error")
        checkout_type = state.get("checkout_type", "unknown")
        current_step = state.get("current_step", "unknown")
        
        # Generate user-friendly error message using LLM
        failure_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a helpful e-commerce assistant handling a checkout error.
                
                Generate a friendly, apologetic error message that:
                1. Acknowledges the issue without being overly technical
                2. Suggests helpful next steps based on the error type
                3. Maintains a supportive, solution-oriented tone
                4. Offers assistance or alternatives
                5. Keeps it brief and actionable
                
                Common error types and suggestions:
                - Cart empty: Suggest adding items to cart
                - Product unavailable: Suggest similar products
                - Address issues: Suggest adding/updating address
                - Payment issues: Suggest checking payment details
                - Authentication: Suggest signing in
                
                Keep it conversational and under 3 sentences.
            """),
            ("user", f"Checkout failed at step '{current_step}' for {checkout_type} checkout. Error: {error_message}")
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({}))
        
        failure_message = str(response.content).strip()
        
        # Set workflow outputs
        state["workflow_output_text"] = failure_message
        
        # Prepare JSON response for frontend
        suggested_actions = get_suggested_actions_for_error(error_message, current_step)
        
        state["workflow_output_json"] = {
            "success": False,
            "message": "Checkout failed",
            "error": error_message,
            "step": current_step,
            "checkout_type": checkout_type,
            "suggested_actions": suggested_actions
        }
        
        print(f"Checkout failure: {current_step} - {error_message}")
        
        return state
        
    except Exception as e:
        print(f"Error in checkout failure handler: {e}")
        # Fallback error message
        state["workflow_output_text"] = "I'm sorry, there was an issue with your checkout. Please try again or contact support."
        state["workflow_output_json"] = {
            "success": False,
            "message": "Checkout failed",
            "error": "Unexpected error occurred",
            "suggested_actions": ["Try again", "Contact support", "View cart"]
        }
        return state

def get_suggested_actions_for_error(error_message: str, current_step: str) -> list[str]:
    """Get contextual suggested actions based on error type."""
    
    error_lower = error_message.lower()
    
    if "empty" in error_lower or "no items" in error_lower:
        return ["Add items to cart", "Browse products", "View recommendations"]
    
    elif "address" in error_lower:
        return ["Add shipping address", "Update address", "View saved addresses"]
    
    elif "product not found" in error_lower or "unavailable" in error_lower:
        return ["Search for similar products", "Browse categories", "Check availability"]
    
    elif "authentication" in error_lower or "sign in" in error_lower:
        return ["Sign in to your account", "Create new account", "Continue as guest"]
    
    elif "payment" in error_lower:
        return ["Check payment details", "Try different payment method", "Contact bank"]
    
    elif current_step == "validation":
        return ["Check cart items", "Update quantities", "Remove unavailable items"]
    
    elif current_step == "address":
        return ["Add shipping address", "Select different address", "Update address"]
    
    elif current_step == "payment":
        return ["Check payment information", "Try different card", "Contact support"]
    
    else:
        return ["Try again", "View cart", "Contact support", "Browse products"]
