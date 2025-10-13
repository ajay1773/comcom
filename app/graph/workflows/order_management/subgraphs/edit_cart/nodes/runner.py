from typing import cast
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig
from app.graph.workflows.order_management.types import EditCartState
from app.graph.workflows.order_management.subgraphs.edit_cart.graph import EditCartGraph


async def run_edit_cart(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """
    Runner function for the edit cart workflow.
    Prepares state and executes the edit cart subgraph.
    """
    # 1. Get or initialize edit_cart state
    sub_state = cast(EditCartState, state.get("edit_cart") or {
        "search_query": state.get('user_message',''),
        "suggestions": [],
        "workflow_widget_json": None,
    })

    # 2. Update sub_state with current context
    sub_state["conversation_history"] = state.get("conversation_history", [])
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["suggestions"] = state.get("suggestions", [])
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)

    # 3. Run the subgraph
    subgraph = EditCartGraph.create()
    updated_sub_state = cast(EditCartState, await subgraph.ainvoke(sub_state, config))
    
    # 4. Merge back into global state
    state["edit_cart"] = updated_sub_state
    # Text response will be automatically extracted by output_handler_node

    return state

