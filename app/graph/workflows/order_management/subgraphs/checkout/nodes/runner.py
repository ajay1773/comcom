from typing import cast
from app.graph.workflows.order_management.types import CheckoutState
from app.graph.workflows.order_management.subgraphs.checkout.graph import CheckoutGraph
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig

async def run_checkout(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Run the checkout workflow."""

        # 1. get or init
    sub_state = cast(CheckoutState, state.get("checkout") or {
        "search_query": state.get('user_message',''),
        "suggestions": [],
        "workflow_widget_json": None,
    })

    # 2. Always update search_query with current user_message
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["suggestions"] = state.get("suggestions", [])
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)

    # 3. run the subgraph
    subgraph = CheckoutGraph.create()
    updated_sub_state = cast(CheckoutState, await subgraph.ainvoke(sub_state))
    # 4. merge back into global
    state["checkout"] = updated_sub_state
    # Text response will be automatically extracted by output_handler_node

    return state