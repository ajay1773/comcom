from typing import List, TypedDict


class CommonState(TypedDict):
    """State for common workflows."""
    search_query: str
    suggestions: List[str]
    thread_id: str | None
    conversation_history: List[str]

class AuthState(TypedDict):
    """State for authentication workflows."""
    user_id: int | None
    session_token: str | None
    is_authenticated: bool
    auth_required: bool

