"""State validation and cleanup service for LangGraph workflows."""
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from app.models.chat import GlobalState

logger = logging.getLogger(__name__)

class StateValidator:
    """Service for validating and cleaning up workflow states."""

    def __init__(self):
        self.max_workflow_age_hours = 24  # Clean up workflows older than this
        self.max_error_age_hours = 1      # Clean up old errors
        self.max_history_length = 50      # Maximum workflow history entries

    def validate_state(self, state: GlobalState) -> List[str]:
        """Validate the state and return list of issues found."""
        issues = []

        # Check required fields
        required_fields = ["user_message", "workflow_states", "workflow_history"]
        for field in required_fields:
            if field not in state:
                issues.append(f"Missing required field: {field}")

        # Validate workflow states
        if "workflow_states" in state:
            workflow_issues = self._validate_workflow_states(state["workflow_states"])
            issues.extend(workflow_issues)

        # Validate current workflow
        if "current_workflow" in state and state["current_workflow"]:
            if state["current_workflow"] not in ["product_search", "place_order", "initiate_payment", "payment_status", "support_query", "fallback"]:
                issues.append(f"Invalid current_workflow: {state['current_workflow']}")

        # Check for stale data
        stale_issues = self._check_for_stale_data(state)
        issues.extend(stale_issues)

        return issues

    def cleanup_state(self, state: GlobalState) -> GlobalState:
        """Clean up the state by removing old data and fixing issues."""
        original_state = state.copy()

        try:
            # Clean up old workflow states
            if "workflow_states" in state:
                state["workflow_states"] = self._cleanup_workflow_states(state["workflow_states"])

            # Clean up workflow history
            if "workflow_history" in state:
                state["workflow_history"] = self._cleanup_workflow_history(state["workflow_history"])

            # Clean up old errors
            if "workflow_error" in state:
                state["workflow_error"] = self._cleanup_error(state["workflow_error"])

            # Fix common issues
            state = self._fix_common_issues(state)

            # Log cleanup if state was modified
            if state != original_state:
                logger.info("State cleaned up", extra={
                    "thread_id": getattr(state, 'configurable', {}).get('thread_id', 'unknown'),
                    "cleanup_performed": True
                })

        except Exception as e:
            logger.error(f"Error during state cleanup: {str(e)}")
            # Return original state if cleanup fails
            return original_state

        return state

    def _validate_workflow_states(self, workflow_states: Dict[str, Any]) -> List[str]:
        """Validate workflow states structure."""
        issues = []

        for workflow_name, workflow_state in workflow_states.items():
            if not isinstance(workflow_state, dict):
                issues.append(f"Invalid workflow state type for {workflow_name}: {type(workflow_state)}")
                continue

            # Check for excessively large states
            state_size = len(str(workflow_state))
            if state_size > 10000:  # 10KB limit per workflow state
                issues.append(f"Workflow state too large for {workflow_name}: {state_size} chars")

        return issues

    def _check_for_stale_data(self, state: GlobalState) -> List[str]:
        """Check for stale or outdated data in state."""
        issues = []

        # Check for old timestamps in errors
        if "workflow_error" in state and state["workflow_error"]:
            error_timestamp = state["workflow_error"].get("timestamp")
            if error_timestamp:
                try:
                    error_time = datetime.fromisoformat(error_timestamp)
                    if datetime.now() - error_time > timedelta(hours=self.max_error_age_hours):
                        issues.append("Stale workflow error detected")
                except (ValueError, TypeError):
                    issues.append("Invalid error timestamp format")

        return issues

    def _cleanup_workflow_states(self, workflow_states: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old or invalid workflow states."""
        cleaned_states = {}

        for workflow_name, workflow_state in workflow_states.items():
            # Skip if state is too old or invalid
            if not isinstance(workflow_state, dict):
                continue

            # Remove excessively large states
            if len(str(workflow_state)) > 10000:
                logger.warning(f"Removing oversized workflow state for {workflow_name}")
                continue

            cleaned_states[workflow_name] = workflow_state

        return cleaned_states

    def _cleanup_workflow_history(self, workflow_history: List[str]) -> List[str]:
        """Clean up workflow history by limiting length."""
        if len(workflow_history) > self.max_history_length:
            # Keep most recent entries
            return workflow_history[-self.max_history_length:]
        return workflow_history

    def _cleanup_error(self, workflow_error: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean up old workflow errors."""
        if not workflow_error:
            return None

        error_timestamp = workflow_error.get("timestamp")
        if error_timestamp:
            try:
                error_time = datetime.fromisoformat(error_timestamp)
                if datetime.now() - error_time > timedelta(hours=self.max_error_age_hours):
                    logger.info("Cleaning up stale workflow error")
                    return None
            except (ValueError, TypeError):
                logger.warning("Invalid error timestamp, cleaning up error")
                return None

        return workflow_error

    def _fix_common_issues(self, state: GlobalState) -> GlobalState:
        """Fix common state issues."""
        # Ensure workflow_states exists
        if "workflow_states" not in state:
            state["workflow_states"] = {}

        # Ensure workflow_history exists and is a list
        if "workflow_history" not in state:
            state["workflow_history"] = []
        elif not isinstance(state["workflow_history"], list):
            state["workflow_history"] = []

        # Remove invalid current_workflow
        if "current_workflow" in state:
            valid_workflows = ["product_search", "place_order", "initiate_payment", "payment_status", "support_query", "fallback", None]
            if state["current_workflow"] not in valid_workflows:
                logger.warning(f"Removing invalid current_workflow: {state['current_workflow']}")
                state["current_workflow"] = None

        return state

    def get_state_summary(self, state: GlobalState) -> Dict[str, Any]:
        """Get a summary of the current state for monitoring."""
        return {
            "has_user_message": "user_message" in state,
            "current_workflow": state.get("current_workflow"),
            "workflow_count": len(state.get("workflow_states", {})),
            "history_length": len(state.get("workflow_history", [])),
            "has_error": "workflow_error" in state and state["workflow_error"] is not None,
            "has_output_text": "workflow_output_text" in state,
            "has_output_json": "workflow_output_json" in state
        }


# Global instance
state_validator = StateValidator()

# Convenience functions
def validate_and_cleanup_state(state: GlobalState) -> tuple[GlobalState, List[str]]:
    """Validate state and return cleaned state with any issues found."""
    issues = state_validator.validate_state(state)
    cleaned_state = state_validator.cleanup_state(state)
    return cleaned_state, issues

def get_state_summary(state: GlobalState) -> Dict[str, Any]:
    """Get state summary for monitoring."""
    return state_validator.get_state_summary(state)
