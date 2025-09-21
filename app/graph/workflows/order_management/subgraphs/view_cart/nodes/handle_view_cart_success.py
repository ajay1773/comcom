"""Handle successful view cart operations."""

from app.graph.workflows.order_management.types import ViewCartState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_view_cart_success_node(state: ViewCartState) -> ViewCartState:
    """Handle successful view cart operation with LLM-generated response."""

    # Generate contextual success response using LLM
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant showing a user's cart contents.

        Generate a friendly, informative response displaying their cart contents.

        Guidelines:
        - Be welcoming and helpful
        - Show a summary of what's in their cart
        - Include item count and total value
        - Keep the tone conversational and encouraging
        - Keep the response concise but informative

        Context:
        - User's original request: {user_query}
        - Number of different items: {cart_count}
        - Total quantity of all items: {total_items}
        - Total cart value: ${total_value:.2f}
        - Items are in cart: {has_items}

        """),
        ("user", """Please generate a friendly response showing the cart contents.""")
    ])

    try:
        cart_details = state.get("cart_details", [])
        user_query = state.get("search_query", "")

        # Calculate cart summary (works for both empty and populated carts)
        cart_count = len(cart_details)
        total_items = sum(item.quantity for item in cart_details)
        total_value = sum(item.total_price for item in cart_details)

        # Convert CartItem objects to dictionaries for JSON serialization
        cart_details_dict = [
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
                "updated_at": item.updated_at
            }
            for item in cart_details
        ]

        # Generate LLM response for both empty and populated carts
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({
            "user_query": user_query,
            "cart_count": cart_count,
            "total_items": total_items,
            "total_value": total_value,
            "has_items": "Yes" if cart_details else "No"
        }))

        success_message = str(response.content).strip()

    except Exception as e:
        print(f"Error in handle_view_cart_success_node: {e}")
        # Fallback success message if LLM fails
        if cart_details:
            success_message = f"Your cart contains {cart_count} item(s) with a total of {total_items} unit(s) worth ${total_value:.2f}."
        else:
            success_message = "Your cart is currently empty. Start shopping to add items!"

    # Set success response in workflow widget
    state["workflow_widget_json"] = {
        "template": "cart_details",
        "payload": {
            "success_message": success_message,
            "cart_details": cart_details_dict if cart_details else [],
            "cart_summary": {
                "item_count": cart_count,
                "total_items": total_items,
                "total_value": total_value
            },
            "suggested_actions": [
                "Continue shopping",
                "Proceed to checkout",
                "Remove items" if cart_details else None,
                "Add more items" if cart_details else "Browse products"
            ]
        }
    }

    return state
