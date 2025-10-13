from typing import cast
from pydantic import BaseModel
from app.graph.workflows.order_management.types import CheckoutProcessorState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service
from app.utils.conversation_context import format_conversation_context_with_template

class CheckoutSubmission(BaseModel):
    """Checkout submission details extracted from user input."""
    selected_address_id: int | None = None
    payment_method: str | None = None  # "cash_on_delivery" or "credit_card"
    # Credit card details (if payment_method is credit_card)
    card_number: str | None = None
    card_expiry: str | None = None
    card_cvv: str | None = None
    card_holder_name: str | None = None

async def extract_submission_details_node(state: CheckoutProcessorState, config: RunnableConfig | None = None) -> CheckoutProcessorState:
    """Extract checkout submission details from user's message."""
    
    user_message = state.get("search_query", "")
    
    # Get conversation context for better checkout extraction
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="order_processing",
        limit=5,
        fallback_message=""
    )
    
    try:
        # Create LLM prompt to extract checkout submission details
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are an information extractor for e-commerce checkout submissions.
                Extract the following details from the user's checkout submission:

                1. selected_address_id: Look for address selection (e.g., "address 1", "first address", "address ID 123")
                2. payment_method: Either "cash_on_delivery" or "credit_card"
                3. For credit card payments, extract:
                   - card_number: Credit card number (remove spaces/dashes)
                   - card_expiry: Expiry date (MM/YY or MM/YYYY format)
                   - card_cvv: CVV/CVC code
                   - card_holder_name: Name on the card

                EXAMPLES:
                Input: "I'll use address 1 and pay with cash on delivery"
                Output: {{"selected_address_id": 1, "payment_method": "cash_on_delivery", "card_number": null, "card_expiry": null, "card_cvv": null, "card_holder_name": null}}

                Input: "Use my first address and credit card 4532 1234 5678 9012, expires 12/25, CVV 123, John Doe"
                Output: {{"selected_address_id": 1, "payment_method": "credit_card", "card_number": "4532123456789012", "card_expiry": "12/25", "card_cvv": "123", "card_holder_name": "John Doe"}}

                Input: "Address ID 5, pay by card: 5555-4444-3333-2222, 03/2026, 456, Jane Smith"
                Output: {{"selected_address_id": 5, "payment_method": "credit_card", "card_number": "5555444433332222", "card_expiry": "03/2026", "card_cvv": "456", "card_holder_name": "Jane Smith"}}

                RULES:
                - Extract address ID as integer if mentioned specifically
                - If "first address" or similar, use 1
                - Remove spaces and dashes from card numbers
                - Use null for missing information
                - Default payment method to "cash_on_delivery" if unclear
                - If conversation context is available, consider previous address and payment interactions
            """),
            ("user", "{search_query}"),
            ("user", "{conversation_context}"),
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = cast(CheckoutSubmission, await llm.with_structured_output(CheckoutSubmission).ainvoke(
            prompt.invoke({"search_query": user_message, "conversation_context": conversation_context})
        ))
        
        # Set the extracted details in state
        state["selected_address_id"] = response.selected_address_id
        state["payment_method"] = response.payment_method
        
        # If credit card payment, store card details
        if response.payment_method == "credit_card":
            state["payment_details"] = {
                "method": "credit_card",
                "card_number": response.card_number,
                "card_expiry": response.card_expiry,
                "card_cvv": response.card_cvv,
                "card_holder_name": response.card_holder_name
            }
        else:
            state["payment_details"] = {
                "method": "cash_on_delivery"
            }
        
        # Debug: Check if checkout_type is set
        checkout_type = state.get("checkout_type")
        print(f"Extracted submission: Address ID {response.selected_address_id}, Payment: {response.payment_method}")
        print(f"Checkout type in state: {checkout_type}")
        
        # If checkout_type is not set, default to cart checkout
        if not checkout_type:
            print("Warning: checkout_type not set, defaulting to 'cart'")
            state["checkout_type"] = "cart"
        
        return state
        
    except Exception as e:
        print(f"Error extracting submission details: {e}")
        state["error_message"] = f"Failed to understand checkout submission: {str(e)}"
        state["checkout_success"] = False
        return state
