"""Node for handling standardized workflow outputs."""
from langchain_core.runnables import RunnableConfig
from app.models.chat import GlobalState
from app.services.chat_history_state import chat_history_state
from app.services.response_extractor import response_extractor
from app.services.widget_events import widget_event_emitter

async def output_handler_node(
    state: GlobalState,
    config: RunnableConfig | None = None,
) -> GlobalState:
    """
    A generic node that processes workflow text outputs and adds them to conversation history.
    
    This node automatically extracts text responses from various workflow output patterns:
    - Explicit response field
    - workflow_output_text (standardized)
    - suggestions[0] (legacy pattern)
    - Subgraph-specific output patterns
    
    Widget events are handled separately by individual workflows.
    """
    # Use the centralized response extractor to get text output
    text_output = response_extractor.extract_text_response(state)

    # Add the response to conversation history
    current_conversation_history = state.get("conversation_history", [])
    
    # Add the assistant's text response with widget JSON if available
    updated_conversation_history = chat_history_state.conversation_manager.add_assistant_message(
        current_conversation_history, text_output
    )
    
    state["conversation_history"] = updated_conversation_history
    
    # Ensure the response field is set for streaming
    state["response"] = text_output

    return state
