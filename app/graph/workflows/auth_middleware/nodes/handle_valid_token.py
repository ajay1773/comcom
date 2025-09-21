from app.graph.workflows.auth_middleware.types import AuthMiddlewareState
from app.core.enums import WorkflowType


async def handle_valid_token_node(state: AuthMiddlewareState) -> AuthMiddlewareState:
    """
    Handle valid token case by setting authentication state and preparing 
    to route to the target workflow.
    """
    
    target_workflow = state.get("target_workflow")
    
    # Update state to indicate successful authentication
    state["workflow_widget_json"] = {}
    # Set suggestions for continuing the workflow
    state["suggestions"] = [f"Authentication successful. Continuing with {target_workflow}."]
    
    return state
