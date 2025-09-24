from typing import cast
from app.graph.workflows.auth_middleware.graph import AuthMiddlewareGraph
from app.graph.workflows.auth_middleware.types import AuthMiddlewareState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_auth_middleware(state: GlobalState, target_workflow: str, config: RunnableConfig | None = None) -> GlobalState:
    """
    Run auth middleware for a protected workflow.
    
    Args:
        state: Global state containing session_token and other data
        target_workflow: The workflow to run after successful authentication
        config: Optional runnable configuration
        
    Returns:
        Updated global state with auth results
    """
    
    # 1. Get or initialize auth middleware sub-state
    sub_state = cast(AuthMiddlewareState, {
        "search_query": state.get("user_message", ""),
        "suggestions": [],
        "workflow_widget_json": {},
        "token": state.get("session_token"),  # Get token from global state
        "is_token_valid": False,
        "user_id": None,
        "auth_error": None,
        "target_workflow": target_workflow,
    })

    # 2. Run the auth middleware subgraph with metadata
    subgraph = AuthMiddlewareGraph.create()
    
    # Create config with metadata to identify this as auth middleware
    auth_config = config.copy() if config else RunnableConfig()
    auth_config.setdefault("metadata", {})["workflow_type"] = "auth_middleware"
    auth_config.setdefault("metadata", {})["is_middleware"] = True
    auth_config.setdefault("metadata", {})["target_workflow"] = target_workflow
    
    updated_sub_state = cast(AuthMiddlewareState, await subgraph.ainvoke(sub_state, auth_config))
    
    # 3. Merge auth results back into global state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", {})
    
    # Update global auth state based on middleware results
    if updated_sub_state.get("is_token_valid", False):
        state["is_authenticated"] = True
        state["user_id"] = updated_sub_state.get("user_id")
        state["auth_required"] = False
        # Continue with the target workflow
        state["current_workflow"] = target_workflow
        state["pending_workflow"] = None
    else:
        state["is_authenticated"] = False
        state["user_id"] = None
        state["auth_required"] = True
        # Store the intended workflow for after login
        state["pending_workflow"] = target_workflow
    
    return state
