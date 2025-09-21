from app.models.chat import GlobalState
from app.services.workflow_state import get_workflow_state, update_workflow_state

async def get_selected_product_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for finding the selected product from the product list in conversation history.
    """
    # Get workflow-specific state
    workflow_state = get_workflow_state(state, "place_order")
    extracted_details = workflow_state.get("extracted_product_details", {})

        # Get product search results from conversation history
    product_search_state = get_workflow_state(state, "product_search")

    # Debug logging
    print("🔍 Current workflow states:", state.get("workflow_states", {}))
    print("🛍️ Product search state:", product_search_state)

    if not product_search_state or "products" not in product_search_state:
        # Create standardized error instead of raising exception
        from app.graph.nodes.error_handler import create_workflow_error
        state["workflow_error"] = create_workflow_error(
            workflow_name="place_order",
            error_type="product_search_required",
            message="Please search for products first before placing an order",
            context={"missing": "product_search_results"}
        )
        return state

    # Get products list after validation
    products = product_search_state["products"]

    # Find the matching product
    selected_product = None
    for product in products:
        if (product["name"] == extracted_details["product_name"] and
            product["brand"] == extracted_details["brand"]):
            selected_product = product
            break

    if not selected_product:
        # If product not found in conversation history, create error instead of raising exception
        from app.graph.nodes.error_handler import create_workflow_error
        state["workflow_error"] = create_workflow_error(
            workflow_name="place_order",
            error_type="product_not_found",
            message="The selected product was not found in the current search results",
            context={
                "searched_product": extracted_details,
                "available_products": [f"{p['name']} by {p['brand']}" for p in products]
            }
        )
        return state

    # Update workflow state with selected product
    workflow_state["selected_product"] = selected_product

    # Update the global state with workflow-specific state
    return update_workflow_state(state, "place_order", workflow_state)
