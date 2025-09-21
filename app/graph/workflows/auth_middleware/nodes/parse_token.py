from typing import cast
from app.graph.workflows.auth_middleware.types import AuthMiddlewareState
from app.services.jwt import JWTService


async def parse_token_node(state: AuthMiddlewareState) -> AuthMiddlewareState:
    """Parse and validate JWT token from the session_token field."""
    
    token = state.get("token")
    
    if not token:
        # No token provided
        state["is_token_valid"] = False
        state["auth_error"] = "No authentication token provided"
        state["user_id"] = None
        return state
    
    try:
        # Verify JWT token and extract user ID
        user_id = await JWTService.verify_jwt(token)
        
        # Token is valid
        state["is_token_valid"] = True
        state["user_id"] = user_id
        state["auth_error"] = None
        
    except Exception as e:
        # Token is invalid or expired
        state["is_token_valid"] = False
        state["auth_error"] = f"Invalid or expired token: {str(e)}"
        state["user_id"] = None
    
    return state
