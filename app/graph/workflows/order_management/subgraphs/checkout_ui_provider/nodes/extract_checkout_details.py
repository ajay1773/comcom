from typing import cast
from pydantic import BaseModel
from app.graph.workflows.order_management.types import CheckoutUIProviderState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service

class CheckoutIntent(BaseModel):
    """Checkout intent extracted from user prompt."""
    checkout_type: str  # "cart" or "direct"
    product_name: str | None = None  # For direct purchase
    brand: str | None = None  # For direct purchase
    size: str | None = None  # For direct purchase
    color: str | None = None  # For direct purchase
    quantity: int | None = None  # For direct purchase

async def extract_checkout_details_node(state: CheckoutUIProviderState, config: RunnableConfig | None = None) -> CheckoutUIProviderState:
    """Extract checkout details and determine checkout type from user's message."""
    
    user_message = state.get("user_message", "")
    
    try:
        # Create LLM prompt to determine checkout type and extract product details
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are an intent classifier for an e-commerce checkout system.
                Analyze the user's message to determine if they want to:
                1. "cart" - Checkout items already in their cart
                2. "direct" - Buy a specific product immediately (direct purchase)

                For CART checkout, look for phrases like:
                - "checkout", "buy my cart", "purchase cart items", "proceed to checkout"
                - "I want to buy these items", "checkout my cart"

                For DIRECT purchase, look for phrases like:
                - "buy this [product]", "purchase [specific product]", "I want to buy [product]"
                - "get me [product]", "order [product]"

                If it's a DIRECT purchase, extract:
                - product_name: The exact product name mentioned
                - brand: Brand name if mentioned  
                - size: Size if specified (S, M, L, XL, 10, 12, etc.)
                - color: Color if specified
                - quantity: Quantity if mentioned (default to 1)

                EXAMPLES:
                Input: "I want to checkout"
                Output: {{"checkout_type": "cart", "product_name": null, "brand": null, "size": null, "color": null, "quantity": null}}

                Input: "Buy the red Nike shirt in size M"
                Output: {{"checkout_type": "direct", "product_name": "shirt", "brand": "Nike", "size": "M", "color": "red", "quantity": 1}}

                Input: "I want to purchase 2 blue jeans from Levi's in size 32"
                Output: {{"checkout_type": "direct", "product_name": "jeans", "brand": "Levi's", "size": "32", "color": "blue", "quantity": 2}}

                RULES:
                - Default to "cart" if intent is unclear
                - Extract exact names and details as mentioned
                - Use null for missing information
                - Quantity defaults to 1 for direct purchases
            """),
            ("user", "{user_message}"),
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = cast(CheckoutIntent, await llm.with_structured_output(CheckoutIntent).ainvoke(
            prompt.invoke({"user_message": user_message})
        ))
        
        # Set the checkout type and product details in state
        state["checkout_type"] = response.checkout_type
        
        # If it's a direct purchase, store product details
        if response.checkout_type == "direct":
            state["product_details"] = {
                "product_name": response.product_name,
                "brand": response.brand,
                "size": response.size,
                "color": response.color,
                "quantity": response.quantity or 1
            }
        
        print(f"Checkout type determined: {response.checkout_type}")
        if response.checkout_type == "direct":
            print(f"Product details: {state['product_details']}")
        
        return state
        
    except Exception as e:
        print(f"Error extracting checkout details: {e}")
        state["error_message"] = f"Failed to understand checkout request: {str(e)}"
        state["ui_data_success"] = False
        return state
