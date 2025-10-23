from app.graph.workflows.order_management.types import CheckoutProcessorState
from langchain_core.runnables import RunnableConfig
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.utils.conversation_context import format_conversation_context_with_template

async def processor_success_handler_node(state: CheckoutProcessorState, config: RunnableConfig | None = None) -> CheckoutProcessorState:
    """Handle successful checkout processing."""
    
    try:
        order_number = state.get("order_number")
        order_id = state.get("order_id")
        total_amount = state.get("total_amount", 0)
        cart_items = state.get("cart_items", [])
        checkout_type = state.get("checkout_type", "cart")
        payment_method = state.get("payment_method", "")
        payment_details = state.get("payment_details", {})
        
        if not order_number or not order_id:
            state["error_message"] = "Order information missing"
            state["checkout_success"] = False
            return state
        
        # Get conversation context for personalized success message
        conversation_context = format_conversation_context_with_template(
            state=dict(state),
            template_name="order_processing",
            limit=5,
            fallback_message=""
        )
        
        # Generate success message using LLM
        success_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a helpful e-commerce assistant confirming a successful order placement.
                
                Generate a friendly, enthusiastic confirmation message that:
                1. Congratulates the user on their successful order
                2. Mentions the order number for reference
                3. Shows the total amount and payment method
                4. Mentions next steps (tracking, delivery, etc.)
                5. Keeps a positive, professional tone
                6. If conversation context shows user preferences or concerns, acknowledge them naturally
                
                Keep it conversational and around 2-3 sentences.
            """),
            ("user", f"Order {order_number} placed successfully! Total: ${total_amount:.2f}, Payment: {payment_method}, {len(cart_items)} items, checkout type: {checkout_type}"),
            ("user", "{conversation_context}")
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({"conversation_context": conversation_context}))
        
        success_message = str(response.content).strip()
        
        # Set workflow outputs
        state["workflow_output_text"] = success_message
        
        # Prepare comprehensive JSON response for frontend
        order_summary = {
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total_amount,
            "item_count": len(cart_items),
            "checkout_type": checkout_type,
            "payment_method": payment_method,
            "payment_status": payment_details.get("status", "unknown"),
            "items": cart_items
        }
        
        # Add payment-specific details
        if payment_method == "credit_card":
            order_summary["masked_card"] = payment_details.get("masked_card")
            order_summary["transaction_id"] = payment_details.get("transaction_id")
        elif payment_method == "cash_on_delivery":
            order_summary["cod_amount"] = total_amount
        
        state["workflow_output_json"] = {
            "success": True,
            "message": "Order placed successfully",
            "order_summary": order_summary,
            "suggested_actions": [
                "Track your order",
                "View order details",
                "Continue shopping",
                "Download invoice"
            ]
        }
        
        print(f"Checkout processing success: Order {order_number} - ${total_amount:.2f}")
        
        return state
        
    except Exception as e:
        print(f"Error in processor success handler: {e}")
        state["error_message"] = f"Success handling failed: {str(e)}"
        state["checkout_success"] = False
        return state
