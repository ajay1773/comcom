from typing import Any, Dict, List, TypedDict


class CommonState(TypedDict):
    """State for common workflows."""
    search_query: str
    suggestions: List[str]
    workflow_widget_json: Dict[str, Any]

class AuthState(TypedDict):
    """State for authentication workflows."""
    user_id: int | None
    session_token: str | None
    is_authenticated: bool
    auth_required: bool

