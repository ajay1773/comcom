from typing import cast
from app.graph.workflows.order_management.types import CheckoutProcessorState
from app.graph.workflows.order_management.subgraphs.checkout_processor.graph import CheckoutProcessorGraph
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig

async def run_checkout_processor(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Run the checkout processor workflow."""
    
    # 1. Get or initialize sub-state
    sub_state = cast(CheckoutProcessorState, state.get("checkout_processor") or {
        "user_message": state.get('user_message', ''),
        "suggestions": [],
        "workflow_output_json": None,
    })
    
    # 2. Always update with current context
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["suggestions"] = state.get("suggestions", [])
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)
    
    # 3. Get checkout data from UI provider if available
    checkout_ui_data = state.get("checkout_ui_provider", {})
    if checkout_ui_data:
        sub_state["checkout_type"] = checkout_ui_data.get("checkout_type")
        sub_state["product_details"] = checkout_ui_data.get("product_details")
        # Note: cart_items and total_amount will be validated again in the processor
    
    # 4. Run the subgraph
    subgraph = CheckoutProcessorGraph.create()
    updated_sub_state = cast(CheckoutProcessorState, await subgraph.ainvoke(sub_state))
    
    # 5. Merge back into global state
    state["checkout_processor"] = updated_sub_state
    
    # Text response will be automatically extracted by output_handler_node
    return state
