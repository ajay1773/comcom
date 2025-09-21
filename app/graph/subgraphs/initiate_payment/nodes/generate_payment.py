from app.models.chat import GlobalState
from app.services.workflow_state import get_workflow_state, update_workflow_state


async def generate_payment_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for generating a payment link.
    """
    # Get workflow-specific state
    workflow_state = get_workflow_state(state, "place_order")
    selected_product = workflow_state.get("selected_product", {})

    # Prepare order details JSON
    payment_details = {
        "selected_product": selected_product,
        "price_breakdown": {
            "subtotal": selected_product.get("min_price", 0),
            "shipping": 10.00,  # Dummy shipping cost
            "tax": selected_product.get("min_price", 0) * 0.08,  # Dummy tax rate 8%
            "total": selected_product.get("min_price", 0) + 10.00 + (selected_product.get("min_price", 0) * 0.08)
        }
    }

    # Update workflow state
    workflow_state["payment_details"] = payment_details

    # Update global state
    state = update_workflow_state(state, "initiate_payment", workflow_state)

    # Set standardized workflow outputs
    state["workflow_output_text"] = "Here is the payment form. Please enter your payment details."
    state["workflow_output_json"] = {
        "template": "initiate_payment",
        "payload": payment_details
    }

    return state
