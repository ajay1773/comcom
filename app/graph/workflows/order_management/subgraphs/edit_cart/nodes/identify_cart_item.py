from typing import cast
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from app.graph.workflows.order_management.types import EditCartState
from app.services.db.cart import cart_service


class CartItemMatch(BaseModel):
    """Result of matching user reference to a cart item."""
    matched_item_id: int | None  # The ID of the matched cart item
    confidence: str  # "high", "medium", "low"
    reasoning: str  # Explanation of the match


async def identify_cart_item_node(state: EditCartState) -> EditCartState:
    """
    LangGraph node for identifying which cart item the user is referring to.
    
    Uses LLM to match the user's reference against current cart items.
    """
    try:
        user_id = state.get("user_id", None)
        target_reference = state.get("target_product_reference", "")
        
        if user_id is None:
            state["error_message"] = "User not authenticated"
            return state
        
        # Get current cart items with product details
        cart_items = await cart_service.get_cart_items_with_product_details(user_id)
        
        if not cart_items:
            state["error_message"] = "Your cart is empty. There are no items to edit."
            return state
        
        # Format cart items for LLM
        cart_items_text = []
        for idx, item in enumerate(cart_items, 1):
            product = item.product_details
            item_desc = f"""
Item {idx}:
- Cart Item ID: {item.id}
- Product: {product.title if product else 'Unknown'}
- Brand: {product.brand if product else 'Unknown'}
- Size: {item.size or 'N/A'}
- Color: {item.color or (product.color if product else 'N/A')}
- Quantity: {item.quantity}
- Price: ${item.unit_price}
"""
            cart_items_text.append(item_desc)
        
        cart_items_formatted = "\n".join(cart_items_text)
        
        # Use LLM to match the reference to a cart item
        matcher_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a cart item matcher for an e-commerce system.
            Your task is to identify which cart item the user is referring to based on their reference.

            TASK:
            Given the user's reference and the current cart items, identify which item they mean.

            MATCHING RULES:
            1. Look for exact matches first (product name, brand)
            2. Consider partial matches (e.g., "shirt" matches "Blue Shirt")
            3. Consider attributes (size, color, brand)
            4. Consider temporal context (e.g., "last item" = most recently added)
            5. If multiple items match, choose the most recently added one
            6. If no good match, return null with explanation

            CONFIDENCE LEVELS:
            - "high": Exact match or very clear reference
            - "medium": Good match but some ambiguity
            - "low": Uncertain match, multiple possibilities

            Return the matched cart item ID, confidence level, and reasoning.
            """ ),
            ("user", """User's reference: "{target_reference}"

Current cart items:
{cart_items}

Which cart item is the user referring to?
""")
        ])

        llm = llm_service.get_llm_without_tools(disable_streaming=True)

        response = await llm.with_structured_output(CartItemMatch).ainvoke(
            matcher_prompt.invoke({
                "target_reference": target_reference,
                "cart_items": cart_items_formatted
            })
        )

        response = cast(CartItemMatch, response)
        
        if response.matched_item_id is None:
            state["error_message"] = f"Could not identify which item you're referring to. {response.reasoning}"
            return state
        
        # Find the matched item in our cart_items list
        matched_item = None
        for item in cart_items:
            if item.id == response.matched_item_id:
                matched_item = item
                break
        
        if matched_item is None:
            state["error_message"] = "Could not find the matched item in your cart."
            return state
        
        # Store matched item details in state
        state["cart_item_id"] = matched_item.id
        state["matched_cart_item"] = {
            "id": matched_item.id,
            "product_id": matched_item.product_id,
            "product_name": matched_item.product_details.title if matched_item.product_details else "Unknown",
            "brand": matched_item.product_details.brand if matched_item.product_details else "Unknown",
            "quantity": matched_item.quantity,
            "size": matched_item.size,
            "color": matched_item.color,
            "unit_price": matched_item.unit_price,
            "total_price": matched_item.total_price
        }
        
        # Store full cart details for potential use
        state["cart_details"] = [item for item in cart_items]
        
        return state
        
    except Exception as e:
        state["error_message"] = f"Error identifying cart item: {str(e)}"
        return state

