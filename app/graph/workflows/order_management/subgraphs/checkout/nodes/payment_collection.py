from app.graph.workflows.order_management.types import CheckoutState
from langchain_core.runnables import RunnableConfig
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate

async def payment_collection_node(state: CheckoutState, config: RunnableConfig | None = None) -> CheckoutState:
    """Handle payment details collection for checkout."""
    
    try:
        total_amount = state.get("total_amount", 0)
        cart_items = state.get("cart_items", [])
        
        if not cart_items or total_amount <= 0:
            state["error_message"] = "Invalid order total for payment"
            state["checkout_success"] = False
            return state
        
        # For now, we'll simulate payment collection
        # In a real implementation, this would integrate with payment gateways
        
        # Set default payment details (simulated)
        state["payment_method"] = "credit_card"
        state["payment_details"] = {
            "method": "credit_card",
            "status": "pending",
            "amount": total_amount,
            "currency": "USD"
        }
        
        state["current_step"] = "order_creation"
        
        # Generate payment confirmation message
        payment_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a helpful e-commerce assistant collecting payment information for checkout.
                
                Generate a brief, friendly message that:
                1. Shows the order total amount
                2. Confirms we're ready to process the payment
                3. Mentions that the order will be created next
                4. Keeps a professional but friendly tone
                
                Keep it conversational and under 2 sentences.
            """),
            ("user", f"Order total: ${total_amount:.2f}, {len(cart_items)} items")
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(payment_prompt.invoke({}))
        
        payment_message = str(response.content).strip()
        
        # Set workflow output for streaming
        state["workflow_output_text"] = payment_message
        
        print(f"Payment details collected: ${total_amount:.2f} via {state['payment_method']}")
        
        return state
        
    except Exception as e:
        print(f"Error in payment collection: {e}")
        state["error_message"] = f"Payment collection failed: {str(e)}"
        state["checkout_success"] = False
        return state
