from typing import cast
from app.models.chat import GlobalState
from pydantic import BaseModel

from app.core.enums import TypeWorkflowType, WorkflowStateKey

class OrchestrationDecision(BaseModel):
    """Orchestrator must return the workflow to call."""
    workflow: TypeWorkflowType
    reason: str


def map_intent_to_workflow(intent: str, confidence: float) -> str:
    """
    Map classified intent to appropriate workflow.
    Enhanced to handle all conversation types and fallback scenarios.
    """
    # Low confidence always goes to fallback for safety
    if confidence < 0.5:
        return "fallback"
    
    # Core ecommerce workflows
    ecommerce_workflows = {
        "product_search": "product_search",
        "place_order": "place_order",
        "initiate_payment": "initiate_payment",
        "payment_status": "payment_status",
        "add_to_cart": "add_to_cart",
        "view_cart": "view_cart",
        "delete_from_cart": "delete_from_cart",
        "user_profile": "user_profile",
        "user_addresses": "user_addresses",
        "add_address_form": "add_address_form",
        "edit_address": "edit_address",
        "delete_address": "delete_address",
        "checkout": "checkout",
        "checkout_ui_provider": "checkout_ui_provider", 
        "checkout_processor": "checkout_processor",
        "order_view": "order_view",
    }
    
    # Authentication workflows
    auth_workflows = {
        "generate_signin_form": "generate_signin_form",
        "login_with_credentials": "login_with_credentials",
        "generate_signup_form": "generate_signup_form",
        "signup_with_details": "signup_with_details",
    }
    
    # Fallback workflows - all conversation types that need enhanced handling
    fallback_intents = {
        "support_query": "support_query",  # Keep support_query as separate workflow
        "faq": "fallback",
        "smalltalk": "fallback",
        "unknown": "fallback",
        "greeting": "fallback",
        "capabilities": "fallback", 
        "farewell": "fallback",
        "out_of_scope": "fallback",
    }
    
    # Combine all mappings
    all_mappings = {**ecommerce_workflows, **auth_workflows, **fallback_intents}
    
    # Return mapped workflow or fallback as default
    return all_mappings.get(intent, "fallback")


async def orchestrator_node(state: GlobalState) -> GlobalState:
    """
    Enhanced orchestrator node that decides which workflow should handle the request.
    Provides better routing for fallback scenarios and conversation management.
    """
    intent = cast(str, state.get(WorkflowStateKey.INTENT.value, ""))
    confidence = cast(float, state.get(WorkflowStateKey.CONFIDENCE.value, 0))
    user_message = state.get(WorkflowStateKey.USER_MESSAGE.value, "")

    # Map intent to workflow using enhanced logic
    workflow = map_intent_to_workflow(intent, confidence)
    
    # Store orchestration metadata for debugging and analytics
    orchestration_metadata = {
        "original_intent": intent,
        "confidence_score": confidence,
        "selected_workflow": workflow,
        "message_length": len(user_message) if user_message else 0,
        "is_fallback": workflow == "fallback",
        "routing_reason": _get_routing_reason(intent, confidence, workflow)
    }
    
    # Update state with workflow decision and metadata
    state[WorkflowStateKey.CURRENT_WORKFLOW.value] = workflow
    state.setdefault(WorkflowStateKey.WORKFLOW_HISTORY.value, []).append(workflow)
    
    # Store orchestration metadata for potential use by workflows
    state.setdefault("orchestration_metadata", orchestration_metadata)

    return state


def _get_routing_reason(intent: str, confidence: float, workflow: str) -> str:
    """
    Provide human-readable reason for workflow routing decision.
    Useful for debugging and analytics.
    """
    if confidence < 0.5:
        return f"Low confidence ({confidence:.2f}) - routed to fallback"
    elif workflow == "fallback":
        return f"Intent '{intent}' mapped to fallback workflow"
    elif intent == workflow:
        return f"Direct mapping: {intent} -> {workflow}"
    else:
        return f"Intent '{intent}' mapped to workflow '{workflow}'"
