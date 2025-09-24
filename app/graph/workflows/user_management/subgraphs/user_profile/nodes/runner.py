"""Runner for user profile subgraph."""

from typing import cast
from app.graph.workflows.user_management.subgraphs.user_profile.graph import UserProfileGraph
from app.graph.workflows.user_management.types import UserProfileState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_user_profile(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """
    Run user profile subgraph to fetch and display user profile details.
    
    Args:
        state: Global state containing user authentication and request data
        config: Optional runnable configuration
        
    Returns:
        Updated global state with user profile results
    """
    
    # 1. Get or initialize user profile sub-state
    sub_state = cast(UserProfileState, {
        "search_query": state.get("user_message", ""),
        "suggestions": [],
        "workflow_widget_json": {},
        "user_id": state.get("user_id"),
        "session_token": state.get("session_token"),
        "is_authenticated": state.get("is_authenticated", False),
        "auth_required": True,
        "user_details": None,
        "user_orders": [],
        "user_addresses": [],
        "workflow_output_text": None,
        "workflow_output_json": None,
        "error_message": None,
        "profile_fetch_success": False
    })

    # 2. Run the user profile subgraph
    subgraph = UserProfileGraph.create()
    updated_sub_state = cast(UserProfileState, await subgraph.ainvoke(sub_state, config))
    
    # 3. Merge results back into global state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", {})
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", "")
    
    # Set error if profile fetch failed
    if updated_sub_state.get("error_message"):
        state["workflow_error"] = updated_sub_state.get("error_message")
    
    return state
