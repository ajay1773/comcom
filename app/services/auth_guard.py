"""Authentication guard for protecting workflows."""
from app.models.chat import GlobalState
from app.services.auth import auth_service


class AuthGuard:
    """Guard for checking authentication requirements."""

    # Workflows that require authentication
    PROTECTED_WORKFLOWS = {
        "place_order",
        "initiate_payment",
        "payment_status"
    }

    @staticmethod
    def requires_auth(workflow_name: str) -> bool:
        """Check if a workflow requires authentication."""
        return workflow_name in AuthGuard.PROTECTED_WORKFLOWS

    @staticmethod
    async def check_and_redirect(state: GlobalState) -> GlobalState:
        """
        Check if current workflow requires auth and redirect if needed.
        This should be called before executing protected workflows.
        """
        current_workflow = state.get("current_workflow")

        # Skip check if not a protected workflow
        if not AuthGuard.requires_auth(current_workflow):
            return state

        # Check if user is authenticated
        thread_id = state.get("thread_id", "")
        user = await auth_service.get_user_from_thread(thread_id)

        if user:
            # User is authenticated, update state and continue
            state["user_id"] = user.id
            state["is_authenticated"] = True
            state["user_profile"] = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone
            }
            state["auth_required"] = False
            return state
        else:
            # User not authenticated, redirect to auth workflow with interrupt
            state["pending_workflow"] = current_workflow
            state["current_workflow"] = "auth"
            state["auth_required"] = True
            state["is_authenticated"] = False
            state["user_id"] = None

            # Set auth message that will be shown by auth workflow
            auth_message = AuthGuard.get_auth_message(current_workflow)
            state["workflow_output_text"] = f"{auth_message} Please provide your email address to continue."
            state["workflow_output_json"] = {
                "template": "auth_required",
                "payload": {
                    "message": auth_message,
                    "pending_workflow": current_workflow,
                    "redirect_to_auth": True
                }
            }

            return state

    @staticmethod
    def get_auth_message(workflow_name: str) -> str:
        """Get appropriate authentication message for workflow."""
        messages = {
            "place_order": "To place an order, I need you to sign in first.",
            "initiate_payment": "To process payment, I need you to sign in first.",
            "payment_status": "To check payment status, I need you to sign in first."
        }
        return messages.get(workflow_name, "To continue, I need you to sign in first.")
