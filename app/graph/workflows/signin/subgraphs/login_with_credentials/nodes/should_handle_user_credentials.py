from app.graph.workflows.signin.types import LoginWithCredentialsState


def should_handle_user_credentials(state: LoginWithCredentialsState) -> str:
    """Should handle user credentials."""
    credentials = state.get("credentials")
    user = state.get("user")
    
    # Check if we have valid credentials and user exists
    if credentials and credentials.get("email") and credentials.get("password") and user:
        return "login_with_credentials"
    else:
        return "fallback"