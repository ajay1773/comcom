from app.graph.workflows.order_management.types import CheckoutProcessorState
from langchain_core.runnables import RunnableConfig
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate

async def processor_failure_handler_node(state: CheckoutProcessorState, config: RunnableConfig | None = None) -> CheckoutProcessorState:
    """Handle checkout processing failure scenarios."""
    
    try:
        error_message = state.get("error_message", "Unknown checkout processing error")
        checkout_type = state.get("checkout_type", "unknown")
        payment_method = state.get("payment_method", "unknown")
        
        # Generate user-friendly error message using LLM
        failure_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a helpful e-commerce assistant handling a checkout processing error.
                
                Generate a friendly, apologetic error message that:
                1. Acknowledges the issue without being overly technical
                2. Suggests helpful next steps based on the error type
                3. Maintains a supportive, solution-oriented tone
                4. Offers assistance or alternatives
                5. Keeps it brief and actionable
                
                Common error types and suggestions:
                - Address issues: Suggest updating or selecting different address
                - Payment issues: Suggest checking payment details or trying different method
                - Product unavailable: Suggest checking cart or trying again
                - Validation errors: Suggest reviewing submission details
                - Order creation: Suggest trying again or contacting support
                
                Keep it conversational and under 3 sentences.
            """),
            ("user", f"Checkout processing failed for {checkout_type} checkout with {payment_method} payment. Error: {error_message}")
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({}))
        
        failure_message = str(response.content).strip()
        
        # Set workflow outputs
        state["workflow_output_text"] = failure_message
        
        # Prepare JSON response for frontend with suggested actions
        suggested_actions = get_suggested_actions_for_error(error_message)
        
        state["workflow_output_json"] = {
            "success": False,
            "message": "Checkout processing failed",
            "error": error_message,
            "checkout_type": checkout_type,
            "payment_method": payment_method,
            "suggested_actions": suggested_actions,
            "order_summary": None
        }
        
        print(f"Checkout processing failure: {error_message}")
        
        return state
        
    except Exception as e:
        print(f"Error in processor failure handler: {e}")
        # Fallback error message
        state["workflow_output_text"] = "I'm sorry, there was an issue processing your checkout. Please try again or contact support."
        state["workflow_output_json"] = {
            "success": False,
            "message": "Checkout processing failed",
            "error": "Unexpected error occurred",
            "suggested_actions": ["Try again", "Contact support", "Check cart"],
            "order_summary": None
        }
        return state

def get_suggested_actions_for_error(error_message: str) -> list[str]:
    """Get contextual suggested actions based on error type."""
    
    error_lower = error_message.lower()
    
    if "address" in error_lower:
        return ["Select different address", "Update address details", "Add new address"]
    
    elif "payment" in error_lower or "card" in error_lower:
        return ["Check payment details", "Try different payment method", "Use cash on delivery", "Contact bank"]
    
    elif "empty" in error_lower or "no items" in error_lower:
        return ["Add items to cart", "Browse products", "View recommendations"]
    
    elif "product not found" in error_lower or "unavailable" in error_lower:
        return ["Check cart items", "Search for alternatives", "Update quantities"]
    
    elif "authentication" in error_lower or "sign in" in error_lower:
        return ["Sign in to your account", "Create new account", "Reset password"]
    
    elif "validation" in error_lower or "invalid" in error_lower:
        return ["Review submission details", "Check required fields", "Try again"]
    
    elif "order creation" in error_lower or "failed to create" in error_lower:
        return ["Try again", "Contact support", "Check cart", "Verify payment"]
    
    else:
        return ["Try again", "Contact support", "Check cart", "Review details"]
