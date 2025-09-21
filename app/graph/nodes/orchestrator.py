from typing import cast
from app.models.chat import GlobalState
from pydantic import BaseModel

from app.core.enums import TypeWorkflowType, WorkflowStateKey

class OrchestrationDecision(BaseModel):
    """Orchestrator must return the workflow to call."""
    workflow: TypeWorkflowType
    reason: str


def map_intent_to_workflow(intent: str, confidence: float) -> str:
    if confidence < 0.5:
        return "fallback"
    
    mapping = {
        "product_search": "product_search",
        "place_order": "place_order",
        "initiate_payment": "initiate_payment",
        "payment_status": "payment_status",
        "support_query": "support_query",
        "faq": "fallback",
        "smalltalk": "fallback",
        "generate_signin_form": "generate_signin_form",
        "login_with_credentials": "login_with_credentials",
        "generate_signup_form": "generate_signup_form",
        "signup_with_details": "signup_with_details",
        "add_to_cart": "add_to_cart",
        "view_cart": "view_cart",
        "unknown": "fallback",
    }
    return mapping.get(intent, "fallback")


async def orchestrator_node(state: GlobalState) -> GlobalState:
    """
    Orchestrator node that decides which workflow should handle the request.
    Returns the workflow decision in the state.
    """
    intent = cast(str, state.get(WorkflowStateKey.INTENT.value, ""))
    confidence = cast(float, state.get(WorkflowStateKey.CONFIDENCE.value, 0))

    workflow = map_intent_to_workflow(intent, confidence)

    state[WorkflowStateKey.CURRENT_WORKFLOW.value] = workflow
    state.setdefault(WorkflowStateKey.WORKFLOW_HISTORY.value, []).append(workflow)

    return state
