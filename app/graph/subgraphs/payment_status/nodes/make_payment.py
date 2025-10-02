from app.models.chat import GlobalState
from app.services.workflow_state import get_workflow_state, update_workflow_state
from app.services.db.order import order_service
from app.services.db.db import Order
import uuid
import datetime


async def make_payment_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for making a payment.
    """
    # Get workflow-specific state
    workflow_state = get_workflow_state(state, "place_order")
    selected_product = workflow_state.get("selected_product", {})
    user_id = state.get("user_id", 1)

    # Get authenticated user ID
    user_id = state.get("user_id", 1)  # Fallback to 1 for backward compatibility
    if not user_id:
        raise ValueError("User ID is required")

    await order_service.create_order(user_id, [selected_product], 0, "credit_card", "Payment for order")
    # await order_service.create_order(Order(
    #     order_number=selected_product.get("id", 0),
    #     status="paid",
    #     amount=selected_product.get("price", 100),
    #     total_items=selected_product.get("quantity", 1),
    #     payment_status="paid",
    #     payment_method="credit_card",
    #     shipping_address_id=0,
    #     notes="Payment for order",
    #     created_at=datetime.datetime.now().isoformat(),
    #     updated_at=datetime.datetime.now    ().isoformat()
    # ))

    # Prepare order details JSON
    payment_status_details = {
        "selected_product": selected_product,
        "price_breakdown": {
            "subtotal": selected_product.get("min_price", 0),
            "shipping": 10.00,  # Dummy shipping cost
            "tax": selected_product.get("min_price", 0) * 0.08,  # Dummy tax rate 8%
            "total": selected_product.get("min_price", 0) + 10.00 + (selected_product.get("min_price", 0) * 0.08)
        },
        "transaction_details": {
            "transaction_id": str(uuid.uuid4()),
            "transaction_date": datetime.datetime.now().isoformat(),
            "transaction_type": "credit_card",
            "transaction_status": "success",
            "transaction_amount": selected_product.get("min_price", 0) + 10.00 + (selected_product.get("min_price", 0) * 0.08)
        }
    }

    # Update workflow state
    workflow_state["payment_status_details"] = payment_status_details

    # Update global state
    state = update_workflow_state(state, "payment_status", workflow_state)

    # Set standardized workflow outputs
    state["workflow_output_text"] = "Your payment has been processed successfully."
    state["workflow_output_json"] = {
        "template": "payment_status_details",
        "payload": payment_status_details
    }

    return state
