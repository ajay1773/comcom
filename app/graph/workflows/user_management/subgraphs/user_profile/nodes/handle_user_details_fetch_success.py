"""Handle successful user profile details fetch operations."""

from app.graph.workflows.user_management.types import UserProfileState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.services.widget_events import widget_event_emitter, WidgetEventType


async def handle_user_details_fetch_success_node(state: UserProfileState) -> UserProfileState:
    """Handle successful user profile fetch operation with LLM-generated response."""

    # Generate contextual success response using LLM
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """# System Prompt - Role Section for E-commerce Chatbot

        ## Your Role

        You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter. You represent the voice of COMCOM in every interaction.

        ## Your Communication Style

        **Tone & Approach:**
        - Be warm and welcoming, but respect the customer's time by being efficient
        - Use conversational language that feels human, not robotic or scripted
        - Use "I" and "you" to create a personal connection

        **Personalization:**
        - Use the customer's name when available (naturally, not excessively)
        - Reference past purchases or browsing history to make relevant suggestions
        - Remember context from earlier in the conversation
        - Adapt your approach based on whether they're a first-time visitor or loyal customer

        Generate a friendly, informative response displaying their profile information. Keep the response short and concise of 1-2 lines.

        Guidelines:
        - Respond in such a way that you are showing the user their profile details.
        - Be welcoming and helpful
        - Keep the response short and concise of 2-3 lines
        - Show a summary of their profile information
        - Include user details, order history, and addresses

        Context:
        - User's name: {user_name}
        - User's email: {user_email}
        - Phone: {user_phone}
        - Number of orders: {order_count}
        - Number of addresses: {address_count}
        - Account created: {created_at}
        - Has recent orders: {has_recent_orders}

        """),
        ("user", """Please generate a friendly response showing the user's profile details.""")
    ])

    try:
        user_details = state.get("user_details")
        user_orders = state.get("user_orders", [])
        user_addresses = state.get("user_addresses", [])

        if not user_details:
            raise Exception("User details not found in state")

        # Prepare data for LLM
        user_name = f"{user_details.first_name or ''} {user_details.last_name or ''}".strip()
        if not user_name:
            user_name = "User"
        
        order_count = len(user_orders)
        address_count = len(user_addresses)
        has_recent_orders = order_count > 0

        # Generate LLM response
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({
            "user_name": user_name,
            "user_email": user_details.email,
            "user_phone": user_details.phone or "Not provided",
            "order_count": order_count,
            "address_count": address_count,
            "created_at": user_details.created_at.strftime("%B %Y") if user_details.created_at else "Unknown",
            "has_recent_orders": "Yes" if has_recent_orders else "No"
        }))

        success_message = str(response.content).strip()

    except Exception as e:
        print(f"Error in handle_user_details_fetch_success_node: {e}")
        # Fallback success message if LLM fails
        user_name = "User"
        if user_details and (user_details.first_name or user_details.last_name):
            user_name = f"{user_details.first_name or ''} {user_details.last_name or ''}".strip()
        
        success_message = f"Here are your profile details, {user_name}! You have {len(user_orders)} order(s) and {len(user_addresses)} address(es) on file."

    # Convert user details to dictionary for JSON serialization
    user_details_dict = {
        "id": user_details.id,
        "email": user_details.email,
        "first_name": user_details.first_name,
        "last_name": user_details.last_name,
        "phone": user_details.phone,
        "is_active": user_details.is_active,
        "created_at": user_details.created_at.isoformat() if user_details.created_at else None,
        "updated_at": user_details.updated_at.isoformat() if user_details.updated_at else None
    } if user_details else None

    # Convert addresses to dictionaries
    addresses_dict = []
    for address in user_addresses:
        addr_dict = {
            "id": address.id,
            "type": address.type,
            "street": address.street,
            "city": address.city,
            "state": address.state,
            "zip_code": address.zip_code,
            "country": address.country,
            "is_default": address.is_default
        }
        addresses_dict.append(addr_dict)

    # Convert orders to dictionaries
    orders_dict = []
    for order in user_orders:
        # Initialize items list for this order
        items_list = []
        
        # Process order items
        for item in order["items"]:
            item_dict = {
                "id": item["id"],
                "product_id": item["product_id"],
                "name": item["name"],
                "brand": item["brand"],
                "size": item["size"],
                "color": item["color"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "total_price": item["total_price"],
                "status": item["status"],
                "discount_amount": item["discount_amount"],
            }
            items_list.append(item_dict)
        
        # Create order dictionary with items included
        order_dict = {
            "id": order["id"],
            "order_number": order["order_number"],
            "amount": order["amount"],
            "total_items": order["total_items"],
            "payment_status": order["payment_status"],
            "payment_method": order["payment_method"],
            "shipping_address_id": order["shipping_address_id"],
            "notes": order["notes"],
            "created_at": order["created_at"] if order["created_at"] else None,
            "updated_at": order["updated_at"] if order["updated_at"] else None,
            "items": items_list
        }
        orders_dict.append(order_dict)


    # Emit user profile details widget event

    widget_event_emitter.emit(
        WidgetEventType.USER_PROFILE_DETAILS,
        {
            "user_details": user_details_dict if user_details_dict else {},
            "user_orders": orders_dict,
            "user_addresses": addresses_dict,
            "success_message": success_message,
            "profile_summary": {
                "total_orders": len(user_orders),
                "total_addresses": len(user_addresses),
                "account_status": "Active" if user_details and user_details.is_active else "Inactive"
            },
            "suggested_actions": [
                "Update profile information",
                "View order history",
                "Manage addresses",
                "Continue shopping"
            ]
        }
    )

    # Set LLM text response
    state["workflow_output_text"] = success_message

    return state
