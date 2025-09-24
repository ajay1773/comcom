from typing import Any, Optional
from app.graph.workflows.product_search.types import ProductSearchState
from app.graph.workflows.signin.types import GenerateSigninFormState, LoginWithCredentialsState
# Removed unused import - ChatState is not used in the codebase
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from app.graph.workflows.signup.types import GenerateSignupFormState, SignupWithDetailsState
from app.graph.workflows.auth_middleware.types import AuthMiddlewareState
from app.graph.workflows.order_management.types import AddToCartState, DeleteFromCartState, ViewCartState




class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    query: str = Field(..., description="The user's message")
    thread_id: Optional[str] = Field(..., description="Unique thread identifier")
    

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="The assistant's response")
    done: bool = Field(
        ..., description="Whether this is the final chunk of the response"
    )

class GlobalState(TypedDict):
    # Core state
    user_message: str
    intent: str | None
    conversation_history: list[str]
    user_profile: dict
    response: str | None

    # Auth
    user_id: int | None
    session_token: str | None
    is_authenticated: bool
    auth_required: bool
    pending_workflow: str | None
    thread_id: str | None

    # Workflow management
    current_workflow: str
    workflow_history: list[str]
    confidence: float | None
    disfluent_message: str | None

    # Outputs
    workflow_output_text: str | None
    workflow_output_json: dict | None
    workflow_widget_json: dict | None

    # Errors
    workflow_error: dict[str, Any] | None
    error_recovery_options: list[str] | None

    # Namespaced workflow sub-states
    product_search: ProductSearchState | None
    generate_signin_form: GenerateSigninFormState | None
    generate_signup_form: GenerateSignupFormState | None
    signup_with_details: SignupWithDetailsState | None
    login_with_credentials: LoginWithCredentialsState | None
    auth_middleware: AuthMiddlewareState | None
    add_to_cart: AddToCartState | None
    view_cart: ViewCartState | None
    delete_from_cart: DeleteFromCartState | None
# ChatState removed - not used in the codebase


