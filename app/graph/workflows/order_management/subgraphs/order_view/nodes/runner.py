from typing import cast
from app.graph.workflows.order_management.types import OrderViewState
from app.graph.workflows.order_management.subgraphs.order_view.graph import OrderViewGraph
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig

async def run_order_view(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Run the order view workflow."""
    
    # 1. Get or initialize sub-state
    sub_state = cast(OrderViewState, state.get("order_view") or {
        "search_query": state.get('user_message', ''),
        "suggestions": [],
    })
    
    # 2. Always update with current context
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["suggestions"] = state.get("suggestions", [])
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)
    
    # 3. Run the subgraph
    subgraph = OrderViewGraph.create()
    updated_sub_state = cast(OrderViewState, await subgraph.ainvoke(sub_state))
    
    # 4. Merge back into global state
    state["order_view"] = updated_sub_state  # type: ignore
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", None)
    
    # Text response will be automatically extracted by output_handler_node
    return state
