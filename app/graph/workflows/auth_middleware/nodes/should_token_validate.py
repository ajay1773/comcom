from app.graph.workflows.auth_middleware.types import AuthMiddlewareState


def should_token_validate(state: AuthMiddlewareState) -> str:
    """
    Conditional edge function that determines next node based on token validity.
    
    Returns:
        "handle_valid_token" if token is valid
        "handle_invalid_token" if token is invalid
    """
    is_token_valid = state.get("is_token_valid", False)
    
    if is_token_valid:
        return "handle_valid_token"
    else:
        return "handle_invalid_token"
