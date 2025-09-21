from typing import Dict, Any
from app.types.common import CommonState


class AuthMiddlewareState(CommonState):
    """State for authentication middleware workflow."""
    token: str | None
    is_token_valid: bool
    user_id: int | None
    auth_error: str | None
    target_workflow: str
    workflow_widget_json: Dict[str, Any]
