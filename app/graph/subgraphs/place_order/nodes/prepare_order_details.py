from app.models.chat import GlobalState
from app.services.workflow_state import get_workflow_state, update_workflow_state

# Dummy addresses for demonstration
DUMMY_ADDRESSES = [
    {
        "id": "addr1",
        "name": "Home",
        "street": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94105",
        "country": "USA",
        "is_default": True
    },
    {
        "id": "addr2",
        "name": "Office",
        "street": "456 Market St",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94103",
        "country": "USA",
        "is_default": False
    }
]

async def prepare_order_details_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for preparing order details JSON for UI rendering.
    """
    # Get workflow-specific state
    workflow_state = get_workflow_state(state, "place_order")
    selected_product = workflow_state.get("selected_product", {})

    # Prepare order details JSON
    order_details = {
        "selected_product": selected_product,
        "addresses": DUMMY_ADDRESSES,
        "price_breakdown": {
            "subtotal": selected_product.get("min_price", 0),
            "shipping": 10.00,  # Dummy shipping cost
            "tax": selected_product.get("min_price", 0) * 0.08,  # Dummy tax rate 8%
            "total": selected_product.get("min_price", 0) + 10.00 + (selected_product.get("min_price", 0) * 0.08)
        }
    }

    # Update workflow state
    workflow_state["order_details"] = order_details

    # Update global state
    state = update_workflow_state(state, "place_order", workflow_state)

    # Set standardized workflow outputs
    state["workflow_output_text"] = "Here are your order details. Please review and confirm."
    state["workflow_output_json"] = {
        "template": "order_details",
        "payload": order_details
    }

    return state
