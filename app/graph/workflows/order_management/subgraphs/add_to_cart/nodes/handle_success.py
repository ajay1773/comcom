"""Handle successful add to cart operations."""

from app.graph.workflows.order_management.types import AddToCartState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_success_node(state: AddToCartState) -> AddToCartState:
    """Handle successful add to cart operation with LLM-generated response."""
    
    cart_details = state.get("cart_details", [])
    product_details = state.get("product_details", {})
    quantity = state.get("quantity", 1)
    user_query = state.get("search_query", "")
    
    # Generate contextual success response using LLM
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant celebrating a successful add-to-cart operation.
        
        Generate a friendly, enthusiastic response confirming the item was added to their cart.
        
        Guidelines:
        - Be positive and congratulatory
        - Confirm the specific product that was added
        - Mention the quantity if more than 1
        - Keep the tone conversational and encouraging
        - Keep the response short and concise
        
        Context:
        - Product added: {product_name} by {brand}
        - Quantity: {quantity}
        - User's original request: {user_query}
        - Total items in cart: {cart_item_count}
        
        """),
        ("user", """Please generate a celebratory response confirming the successful addition to cart""")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({
            "product_name": product_details.get("name", "the item"),
            "brand": product_details.get("brand", ""),
            "quantity": quantity,
            "user_query": user_query,
            "cart_item_count": len(cart_details)
        }))
        
        success_message = str(response.content).strip()
        
    except Exception:
        # Fallback success message if LLM fails
        product_name = product_details.get("name", "the item")
        brand = product_details.get("brand", "")
        if brand:
            success_message = f"Great! I've added {quantity} {product_name} by {brand} to your cart. You now have {len(cart_details)} items in your cart."
        else:
            success_message = f"Great! I've added {quantity} {product_name} to your cart. You now have {len(cart_details)} items in your cart."
    
    # Set success response in workflow widget
    state["workflow_widget_json"] = {
        "template": "add_to_card_success",
        "payload": {
            "success_message": success_message,
            "cart_details": cart_details,
            "suggested_actions": [
                "View cart",
                "Continue shopping", 
                "Proceed to checkout"
            ]
        }
    }
    
    return state
