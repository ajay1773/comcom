"""Runner for delete address subgraph."""

from typing import cast
from app.graph.workflows.user_management.subgraphs.delete_address.graph import DeleteAddressGraph
from app.graph.workflows.user_management.types import DeleteAddressState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_delete_address(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """
    Run delete address subgraph to remove an existing user address.
    
    Args:
        state: Global state containing user authentication and request data
        config: Optional runnable configuration
        
    Returns:
        Updated global state with address deletion results
    """
    
    # 1. Get or initialize delete address sub-state
    sub_state = cast(DeleteAddressState, {
        "search_query": state.get("user_message", ""),
        "suggestions": [],
        "workflow_widget_json": {},
        "user_id": state.get("user_id"),
        "session_token": state.get("session_token"),
        "is_authenticated": state.get("is_authenticated", False),
        "auth_required": True,
        "address_id": None,
        "user": state.get("user"),
        "existing_address": None,
        "address_delete_success": False,
        "workflow_output_text": None,
        "workflow_output_json": None,
        "error_message": None
    })

    # 2. Run the delete address subgraph
    subgraph = DeleteAddressGraph.create()
    updated_sub_state = cast(DeleteAddressState, await subgraph.ainvoke(sub_state, config))
    
    # 3. Merge results back into global state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", {})
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", "")
    
    # Set error if address deletion failed
    if updated_sub_state.get("error_message"):
        state["workflow_error"] = updated_sub_state.get("error_message", None)
    
    return state
