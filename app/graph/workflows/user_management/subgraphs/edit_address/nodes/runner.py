"""Runner for edit address subgraph."""

from typing import cast
from app.graph.workflows.user_management.subgraphs.edit_address.graph import EditAddressGraph
from app.graph.workflows.user_management.types import EditAddressState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_edit_address(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """
    Run edit address subgraph to update an existing user address.
    
    Args:
        state: Global state containing user authentication and request data
        config: Optional runnable configuration
        
    Returns:
        Updated global state with address edit results
    """
    
    # 1. Get or initialize edit address sub-state
    sub_state = cast(EditAddressState, {
        "search_query": state.get("user_message", ""),
        "suggestions": [],
        "workflow_widget_json": {},
        "user_id": state.get("user_id"),
        "session_token": state.get("session_token"),
        "is_authenticated": state.get("is_authenticated", False),
        "auth_required": True,
        "address_id": None,
        "extracted_address": None,
        "existing_address": None,
        "address_edit_success": False,
        "workflow_output_text": None,
        "workflow_output_json": None,
        "error_message": None
    })

    # 2. Run the edit address subgraph
    subgraph = EditAddressGraph.create()
    updated_sub_state = cast(EditAddressState, await subgraph.ainvoke(sub_state, config))
    
    # 3. Merge results back into global state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", {})
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", "")
    
    return state
