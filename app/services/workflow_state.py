"""Workflow state management utilities."""
from typing import Any
from app.models.chat import GlobalState
from app.core.enums import WorkflowStateKey


def get_workflow_state(state: GlobalState, workflow_name: str) -> dict[str, Any]:
    """Get workflow-specific state."""
    if workflow_name not in state[WorkflowStateKey.WORKFLOW_STATES.value]:
        state[WorkflowStateKey.WORKFLOW_STATES.value][workflow_name] = {}
    return state[WorkflowStateKey.WORKFLOW_STATES.value][workflow_name]


def update_workflow_state(
    state: GlobalState, workflow_name: str, updates: dict[str, Any]
) -> GlobalState:
    """Update workflow-specific state."""
    if workflow_name not in state[WorkflowStateKey.WORKFLOW_STATES.value]:
        state[WorkflowStateKey.WORKFLOW_STATES.value][workflow_name] = {}

    state[WorkflowStateKey.WORKFLOW_STATES.value][workflow_name].update(updates)

    # Update workflow tracking
    if state[WorkflowStateKey.CURRENT_WORKFLOW.value] != workflow_name:
        state[WorkflowStateKey.CURRENT_WORKFLOW.value] = workflow_name
        state[WorkflowStateKey.WORKFLOW_HISTORY.value].append(workflow_name)

    return state
