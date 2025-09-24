"""Handle successful add to cart operations."""

from app.graph.workflows.order_management.types import AddToCartState
from app.services.db.cart import cart_service
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_success_node(state: AddToCartState) -> AddToCartState:
    """Handle successful add to cart operation with LLM-generated response."""
    
    cart_details = state.get("cart_details", [])
    product_details = state.get("product_details", {})
    quantity = state.get("quantity", 1)
    user_query = state.get("search_query", "")
    user_id = state.get("user_id", None)
    
    # Generate contextual success response using LLM
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant celebrating a successful add-to-cart operation.
        
        Generate a friendly, enthusiastic response confirming the item was deleted from their cart.
        
        Guidelines:
        - Be positive and congratulatory
        - Confirm the specific product that was deleted
        - Keep the tone conversational and encouraging
        - Keep the response short and concise
        
        Context:
        - Product deleted: {product_name} by {brand}
        - User's original request: {user_query}
        
        """),
        ("user", """Please generate a response confirming the successful deletion from cart""")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({
            "product_name": product_details.get("name", "the item"),
            "brand": product_details.get("brand", ""),
            "user_query": user_query,
        }))
        
        success_message = str(response.content).strip()
        cart_items = await cart_service.get_cart_items_with_product_details(user_id) if user_id else []
        cart_details = [
            {
                "id": item.id,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "size": item.size,
                "color": item.color,
                "unit": item.unit,
                "selected_options": item.selected_options,
                "added_at": item.added_at,
                "updated_at": item.updated_at,
                "product_details": item.product_details.model_dump() if item.product_details else None
            }
            for item in cart_items
        ]

        state["workflow_widget_json"] = {
        "template": "cart_details",
        "payload": {
            "message": {
                "type": "success",
                "message": "Deleted from cart"
            },
            "cart_details": cart_details,
        }
    } 
        
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
        "template": "delete_from_cart_success",
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
