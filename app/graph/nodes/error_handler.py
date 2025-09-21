"""Error handling node for LangGraph workflows."""
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from app.models.chat import GlobalState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def error_handler_node(
    state: GlobalState,
    config: RunnableConfig | None = None,
) -> GlobalState:
    """
    Global error handler that processes workflow errors and generates user-friendly responses.
    This node should be called when a workflow encounters an error.
    """
    try:
        workflow_error = state.get("workflow_error")
        if not workflow_error:
            # No error to handle, continue normally
            return state

        error_type = workflow_error.get("type", "unknown_error")
        error_message = workflow_error.get("message", "An unexpected error occurred")
        workflow_name = workflow_error.get("workflow_name", "unknown")
        original_exception = workflow_error.get("exception")

        # Log the error for monitoring
        logger.error(
            f"Workflow error in {workflow_name}: {error_type} - {error_message}",
            extra={
                "workflow_name": workflow_name,
                "error_type": error_type,
                "thread_id": config.configurable.get("thread_id") if config else None,
                "user_message": state.get("user_message", ""),
                "timestamp": datetime.now().isoformat()
            }
        )

        # Generate recovery options based on error type
        recovery_options = _generate_recovery_options(error_type, workflow_name)

        # Generate user-friendly error message
        error_response = await _generate_error_message(
            error_type, error_message, workflow_name, recovery_options
        )

        # Update state with error information
        state["workflow_output_text"] = error_response
        state["workflow_output_json"] = {
            "template": "error",
            "payload": {
                "error_type": error_type,
                "error_message": error_message,
                "workflow_name": workflow_name,
                "recovery_options": recovery_options,
                "timestamp": datetime.now().isoformat()
            }
        }
        state["error_recovery_options"] = recovery_options

        # Clear the error from state to prevent re-processing
        state["workflow_error"] = None

        return state

    except Exception as e:
        # Handle errors in error handling itself
        logger.critical(f"Error in error handler: {str(e)}", exc_info=True)
        state["workflow_output_text"] = "I'm experiencing technical difficulties. Please try again in a moment."
        state["workflow_output_json"] = {
            "template": "error",
            "payload": {
                "error_type": "system_error",
                "error_message": "Error handling system failure",
                "recovery_options": ["Try again", "Contact support"]
            }
        }
        return state


def _generate_recovery_options(error_type: str, workflow_name: str) -> list[str]:
    """Generate context-appropriate recovery options based on error type."""
    base_options = ["Try again", "Start over", "Contact support"]

    # Workflow-specific recovery options
    if workflow_name == "place_order":
        if error_type == "product_not_found":
            return ["Search for products first", "Check product name spelling"] + base_options
        elif error_type == "validation_error":
            return ["Check your input format", "Provide complete product information"] + base_options
        else:
            return ["Check order details", "Verify product availability"] + base_options

    elif workflow_name == "product_search":
        if error_type == "no_results":
            return ["Try different keywords", "Check spelling", "Use broader search terms"] + base_options
        else:
            return ["Refine your search", "Try different categories"] + base_options

    elif workflow_name in ["initiate_payment", "payment_status"]:
        if error_type == "payment_error":
            return ["Check payment details", "Verify card information", "Try different payment method"] + base_options
        else:
            return ["Check payment status", "Verify transaction details"] + base_options

    return base_options


async def _generate_error_message(
    error_type: str, error_message: str, workflow_name: str, recovery_options: list[str]
) -> str:
    """Generate a user-friendly error message using LLM."""
    try:
        error_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are an error message generator for an e-commerce chatbot.
                Generate a clear, helpful, and user-friendly error message based on the error details provided.

                Guidelines:
                - Be empathetic and apologetic
                - Explain what went wrong in simple terms
                - Suggest specific next steps from the recovery options
                - Keep the tone professional but friendly
                - Don't mention technical details unless absolutely necessary
                - Focus on what the user can do to resolve the issue

                Error context:
                - Workflow: {workflow_name}
                - Error Type: {error_type}
                - Technical Message: {error_message}
                - Recovery Options: {recovery_options}
            """),
            ("user", """
                Please generate a user-friendly error message for this situation.
                Make it helpful and actionable.
            """)
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(
            error_prompt.invoke({
                "workflow_name": workflow_name,
                "error_type": error_type,
                "error_message": error_message,
                "recovery_options": ", ".join(recovery_options)
            })
        )

        return response.content.strip()

    except Exception as e:
        # Fallback error message if LLM fails
        logger.warning(f"Failed to generate error message with LLM: {str(e)}")
        return f"I'm sorry, but I encountered an issue with {workflow_name}. {error_message}. You can try: {', '.join(recovery_options[:2])}."


def create_workflow_error(
    workflow_name: str,
    error_type: str,
    message: str,
    exception: Exception = None,
    context: dict = None
) -> dict:
    """Helper function to create standardized workflow error objects."""
    return {
        "workflow_name": workflow_name,
        "type": error_type,
        "message": message,
        "exception": str(exception) if exception else None,
        "context": context or {},
        "timestamp": datetime.now().isoformat()
    }
