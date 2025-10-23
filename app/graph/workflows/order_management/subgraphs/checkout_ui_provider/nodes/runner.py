from typing import cast
from app.graph.workflows.order_management.types import CheckoutUIProviderState
from app.graph.workflows.order_management.subgraphs.checkout_ui_provider.graph import CheckoutUIProviderGraph
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig

async def run_checkout_ui_provider(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Run the checkout UI provider workflow."""
    
    # 1. Get or initialize sub-state
    sub_state = cast(CheckoutUIProviderState, state.get("checkout_ui_provider") or {
        "search_query": state.get('user_message', ''),
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
    
    # 3. Run the subgraph
    subgraph = CheckoutUIProviderGraph.create()
    updated_sub_state = cast(CheckoutUIProviderState, await subgraph.ainvoke(sub_state))
    
    # 4. Merge back into global state
    state["checkout_ui_provider"] = updated_sub_state  # type: ignore
    
    # 5. Set workflow outputs for output_handler
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", "")
    state["workflow_output_json"] = updated_sub_state.get("workflow_output_json", {})
    
    return state
