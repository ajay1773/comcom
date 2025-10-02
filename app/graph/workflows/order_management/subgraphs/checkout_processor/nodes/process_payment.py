from app.graph.workflows.order_management.types import CheckoutProcessorState
from langchain_core.runnables import RunnableConfig

async def process_payment_node(state: CheckoutProcessorState, config: RunnableConfig | None = None) -> CheckoutProcessorState:
    """Process payment for the checkout."""
    
    try:
        payment_method = state.get("payment_method")
        payment_details = state.get("payment_details", {})
        total_amount = state.get("total_amount", 0)
        
        if not payment_method or total_amount <= 0:
            state["error_message"] = "Invalid payment details"
            state["checkout_success"] = False
            return state
        
        # Process payment based on method
        if payment_method == "cash_on_delivery":
            await process_cod_payment(state, total_amount)
        elif payment_method == "credit_card":
            await process_credit_card_payment(state, payment_details, total_amount)
        else:
            state["error_message"] = f"Unsupported payment method: {payment_method}"
            state["checkout_success"] = False
            return state
        
        if not state.get("error_message"):
            print(f"Payment processing successful: {payment_method} - ${total_amount:.2f}")
        
        return state
        
    except Exception as e:
        print(f"Error processing payment: {e}")
        state["error_message"] = f"Payment processing failed: {str(e)}"
        state["checkout_success"] = False
        return state

async def process_cod_payment(state: CheckoutProcessorState, total_amount: float):
    """Process cash on delivery payment."""
    
    try:
        # COD doesn't require immediate payment processing
        # Just mark as pending for delivery
        state["payment_details"]["status"] = "pending_delivery"
        state["payment_details"]["amount"] = total_amount
        state["payment_details"]["currency"] = "USD"
        state["payment_details"]["transaction_id"] = f"COD_{int(total_amount * 100)}_{hash(str(state.get('user_id', 0)))}"
        
        print(f"COD payment prepared: ${total_amount:.2f}")
        
    except Exception as e:
        print(f"COD payment processing error: {e}")
        state["error_message"] = f"COD payment setup failed: {str(e)}"
        state["checkout_success"] = False

async def process_credit_card_payment(state: CheckoutProcessorState, payment_details: dict, total_amount: float):
    """Process credit card payment."""
    
    try:
        # In a real implementation, this would integrate with payment gateways
        # For now, we'll simulate the payment processing
        
        card_number = payment_details.get("card_number", "")
        card_holder_name = payment_details.get("card_holder_name", "")
        
        # Simulate payment processing
        # In production, you would:
        # 1. Validate card with payment gateway
        # 2. Process the charge
        # 3. Handle success/failure responses
        # 4. Store transaction details securely
        
        # For simulation, we'll just create a mock transaction
        masked_card = f"****-****-****-{card_number[-4:]}" if len(card_number) >= 4 else "****"
        
        # Update payment details with processing result
        state["payment_details"]["status"] = "completed"
        state["payment_details"]["amount"] = total_amount
        state["payment_details"]["currency"] = "USD"
        state["payment_details"]["transaction_id"] = f"CC_{int(total_amount * 100)}_{hash(card_number)}"
        state["payment_details"]["masked_card"] = masked_card
        state["payment_details"]["card_holder"] = card_holder_name
        
        # Remove sensitive card details from state (security best practice)
        if "card_number" in state["payment_details"]:
            del state["payment_details"]["card_number"]
        if "card_cvv" in state["payment_details"]:
            del state["payment_details"]["card_cvv"]
        
        print(f"Credit card payment processed: {masked_card} - ${total_amount:.2f}")
        
    except Exception as e:
        print(f"Credit card payment processing error: {e}")
        state["error_message"] = f"Credit card payment failed: {str(e)}"
        state["checkout_success"] = False
