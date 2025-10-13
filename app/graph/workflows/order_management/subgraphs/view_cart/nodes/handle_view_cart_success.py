"""Handle successful view cart operations."""

from app.graph.workflows.order_management.types import ViewCartState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.services.widget_events import widget_event_emitter, WidgetEventType
from app.types.common import BASE_PERSONA_PROMPT

async def handle_view_cart_success_node(state: ViewCartState) -> ViewCartState:
    """Handle successful view cart operation with LLM-generated response."""

    # Generate contextual success response using LLM
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", BASE_PERSONA_PROMPT + """

        ###Task:
        - Show a summary of what's in user's cart.

        ###Rules:
        - Do not include clickable links
        - Do not use technical words like "query", "results", or "response".
        - Include item count and total value
        - Keep the response concise but informative
        - Do not tell user that you can show their cart as this node is already showing it.

        ###Context:
        - User's original request: {user_query}
        - Number of different items: {cart_count}
        - Total quantity of all items: {total_items}
        - Total cart value: ${total_value:.2f}
        - Items are in cart: {has_items}

        """),
        ("user", """Please generate a friendly response showing the cart contents.""")
    ])

    try:
        cart_details = state.get("cart_details", []) or []
        user_query = state.get("search_query", "")

        # Calculate cart summary (works for both empty and populated carts)
        cart_count = len(cart_details)
        total_items = sum(item.quantity for item in cart_details)
        total_value = sum(item.total_price for item in cart_details)

        # Convert CartItemWithProductDetails objects to dictionaries for JSON serialization
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
                "updated_at": item.updated_at,
                "product_details": {
                    "id": item.product_details.id if item.product_details else None,
                    "title": item.product_details.title if item.product_details else None,
                    "category": item.product_details.category if item.product_details else None,
                    "price": item.product_details.price if item.product_details else None,
                    "gender": item.product_details.gender if item.product_details else None,
                    "material": item.product_details.material if item.product_details else None,
                    "style": item.product_details.style if item.product_details else None,
                    "pattern": item.product_details.pattern if item.product_details else None,
                    "color": item.product_details.color if item.product_details else None,
                    "images": item.product_details.images if item.product_details else None,
                    "available_sizes": item.product_details.available_sizes if item.product_details else None,
                    "unit": item.product_details.unit if item.product_details else None,
                    "brand": item.product_details.brand if item.product_details else None,
                    "sku": item.product_details.sku if item.product_details else None,
                    "weight": item.product_details.weight if item.product_details else None,
                    "dimensions": item.product_details.dimensions if item.product_details else None,
                    "warranty_information": item.product_details.warranty_information if item.product_details else None,
                    "shipping_information": item.product_details.shipping_information if item.product_details else None,
                    "availability_status": item.product_details.availability_status if item.product_details else None,
                    "return_policy": item.product_details.return_policy if item.product_details else None,
                    "minimum_order_quantity": item.product_details.minimum_order_quantity if item.product_details else None,
                    "thumbnail": item.product_details.thumbnail if item.product_details else None,
                    "images": item.product_details.images if item.product_details else None,
                    "barcode": item.product_details.barcode if item.product_details else None,
                    "qr_code": item.product_details.qr_code if item.product_details else None,
                    "available_sizes": item.product_details.available_sizes if item.product_details else None,
                    "unit": item.product_details.unit if item.product_details else None
                } if item.product_details else None
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

    # Emit cart details widget event
    widget_event_emitter.emit(
        WidgetEventType.VIEW_CART_SUCCESS,
        {
        "cart_items": cart_details_dict if cart_details else [],
        "cart_summary": {
            "item_count": cart_count,
            "total_items": total_items,
            "total_value": total_value
        },
        "success_message": success_message
        }
    )

    # Set text response for streaming
    state["workflow_output_text"] = success_message

    return state
