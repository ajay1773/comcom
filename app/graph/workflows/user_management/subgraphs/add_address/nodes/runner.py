"""Runner for add address subgraph."""

from typing import cast
from app.graph.workflows.user_management.subgraphs.add_address.graph import AddAddressGraph
from app.graph.workflows.user_management.types import AddAddressState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_add_address(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """
    Run add address subgraph to extract and save user address.
    
    Args:
        state: Global state containing user authentication and request data
        config: Optional runnable configuration
        
    Returns:
        Updated global state with address save results
    """
    
    # 1. Get or initialize add address sub-state
    sub_state = cast(AddAddressState, {
        "search_query": state.get("user_message", ""),
        "suggestions": [],
        "workflow_widget_json": {},
        "user_id": state.get("user_id"),
        "session_token": state.get("session_token"),
        "is_authenticated": state.get("is_authenticated", False),
        "auth_required": True,
        "extracted_address": None,
        "address_save_success": False,
        "workflow_output_text": None,
        "workflow_output_json": None,
        "error_message": None
    })

    # 2. Run the add address subgraph
    subgraph = AddAddressGraph.create()
    updated_sub_state = cast(AddAddressState, await subgraph.ainvoke(sub_state, config))
    
    # 3. Merge results back into global state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", {})
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", "")
    
    return state
