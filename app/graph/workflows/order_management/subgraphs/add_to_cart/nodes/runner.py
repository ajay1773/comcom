

from typing import cast
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig
from app.graph.workflows.order_management.types import AddToCartState
from app.graph.workflows.order_management.subgraphs.add_to_cart.graph import AddToCartGraph



async def run_add_to_cart(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    # 1. get or init
    sub_state = cast(AddToCartState, state.get("add_to_cart") or {
        "search_query": state.get('user_message',''),
        "suggestions": [],
        "workflow_widget_json": None,
    })

    # 2. Always update search_query with current user_message
    sub_state["suggestions"] = state.get("suggestions", [])
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)

    # 3. run the subgraph
    subgraph = AddToCartGraph.create()
    updated_sub_state = cast(AddToCartState, await subgraph.ainvoke(sub_state))
    # 4. merge back into global
    state["add_to_cart"] = updated_sub_state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", None)

    return state