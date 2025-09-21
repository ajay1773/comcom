

from typing import cast
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig
from app.graph.workflows.order_management.types import ViewCartState
from app.graph.workflows.order_management.subgraphs.view_cart.graph import ViewCartGraph


async def run_view_cart(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Run the view cart workflow subgraph."""
    # 1. get or init view_cart state
    sub_state = cast(ViewCartState, state.get("view_cart") or {
        "cart_details": [],
    })

    # 2. Update state with authentication info and other necessary fields
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)

    # 3. run the view cart subgraph
    subgraph = ViewCartGraph.create()
    updated_sub_state = cast(ViewCartState, await subgraph.ainvoke(sub_state))

    # 4. merge back into global state
    state["view_cart"] = updated_sub_state

    return state