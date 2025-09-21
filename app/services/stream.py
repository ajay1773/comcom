from typing import AsyncIterator, cast
from uuid import uuid4, UUID
from datetime import datetime, date, time
from decimal import Decimal
from langchain_core.runnables import RunnableConfig
from app.services.chat_history_state import chat_history_state
from app.graph.workflows.base import create_base_graph
import json
import logging

logger = logging.getLogger(__name__)


class StreamService:
    """Service for managing stream operations."""

    def __init__(self):
        """Initialize stream service."""
        # Define which nodes should NOT stream (return structured data)
        self.non_streaming_nodes = {
            "orchestrator_node",
            "classifier_node", 
            "extract_search_parameters",
            "extract_product_details",
            "extract_login_credentials",
            "extract_params",
            "extract_signup_details"
        }

    async def stream_base_graph(
        self, message: str, thread_id: str, token: str
    ) -> AsyncIterator[str]:
        """Stream a message with Base Graph."""
        compiled_graph, _ = await create_base_graph()

        if thread_id == "" or thread_id is None:
            thread_id = f"chat_{uuid4()}"

        # Configuration for LangGraph checkpointing system
        config = RunnableConfig(configurable={"thread_id": thread_id})
        thread_data = json.dumps({"thread_id": thread_id, "event_name": "thread_info"})
        yield f"data: {thread_data}\n\n"

        initial_state = await chat_history_state.get_initial_state_from_config(
            message, config, compiled_graph, token
        )

        stream = compiled_graph.astream_events(
            initial_state, config=config, version="v1"
        )

        async for event in stream:
            event_type = event.get("event")
            event_name = event.get('name')

            # Handle disfluency_generated event from classifier
            if event_name == "classifier_node" and event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                if output and output.get('disfluent_message'):
                    yield f"data: {json.dumps({'event_name': 'disfluency_generated', 'text': output.get('disfluent_message')})}\n\n"

            # Handle streaming from user-facing nodes only
            elif event_type == "on_chat_model_stream":
                # Get the actual node name from metadata
                actual_node_name = event.get("metadata", {}).get("langgraph_node", "")
                
                # Only stream from nodes that should provide user-facing content
                if actual_node_name not in self.non_streaming_nodes:
                    event_data = event.get("data", {})
                    if "chunk" in event_data:
                        chunk = event_data["chunk"]
                        if hasattr(chunk, "content") and chunk.content:
                            content = chunk.content
                            if content and content.strip():
                                yield f"data: {json.dumps({'event_name': 'llm_stream', 'text': content})}\n\n"

            elif event_name == "LangGraph" and event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                
                # Extract workflow_widget_json from any completed workflow
                widget_json = self._extract_workflow_widget_json(output)
                if widget_json:
                    try:
                        # Ensure JSON serializability
                        serializable_json = self._make_json_serializable(widget_json)
                        yield f"data: {json.dumps({'event_name': 'workflow_widget_json', 'json': serializable_json})}\n\n"
                    except (TypeError, ValueError) as e:
                        logger.error(f"Failed to serialize workflow_widget_json: {e}")
                        logger.error(f"Widget JSON type: {type(widget_json)}")
                        logger.error(f"Widget JSON content: {str(widget_json)[:500]}...")
                        # Return a safe error message instead of crashing
                        error_json = {"error": "Failed to serialize workflow output", "message": str(e)}
                        yield f"data: {json.dumps({'event_name': 'workflow_widget_json', 'json': error_json})}\n\n"

            # Handle final output from output_handler
            elif event_name == "output_handler" and event_type == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                if output:
                    text_output = output.get("response") or output.get("workflow_output_text")
                    if text_output:
                        yield f"data: {json.dumps({'event_name': 'llm_stream', 'text': text_output})}\n\n"

    def _extract_workflow_widget_json(self, state_data):
        """
        Fully dynamic extraction of workflow widget JSON from any workflow state.
        No hardcoded workflow names - discovers them automatically.
        """
        if not isinstance(state_data, dict):
            return None
        
        # Strategy 1: Look for explicit workflow_widget_json field
        if "workflow_widget_json" in state_data:
            return state_data["workflow_widget_json"]
        
        # Strategy 2: Auto-discover workflow-specific nested states
        for key, value in state_data.items():
            if isinstance(value, dict) and self._is_workflow_state(key, value):
                # Extract widget data from discovered workflow state
                widget_data = self._extract_widget_data_dynamically(key, value)
                if widget_data:
                    return widget_data
        
        # Strategy 3: Direct workflow result detection (for subgraphs)
        if self._is_workflow_result(state_data):
            return self._format_workflow_result(state_data)
            
        return None
    
    def _is_workflow_state(self, key, value):
        """
        Determine if a key-value pair represents a workflow state using data structure analysis.
        Completely adaptive - no hardcoded patterns.
        """
        if not isinstance(value, dict):
            return False
        
        # Skip core system fields that are not workflows
        system_fields = {"user_message", "intent", "conversation_history", "user_profile", 
                        "response", "user_id", "session_token", "is_authenticated", 
                        "auth_required", "pending_workflow", "thread_id", "current_workflow", 
                        "workflow_history", "confidence", "workflow_output_text", 
                        "workflow_output_json", "workflow_error", "error_recovery_options"}
        
        if key in system_fields:
            return False
        
        # Analyze the data structure to determine if it's workflow-like
        return self._analyze_structure_for_workflow_patterns(value)
    
    def _extract_widget_data_dynamically(self, workflow_name, workflow_state):
        """
        Extract all non-null data from workflow state - completely adaptive.
        No hardcoded field filtering.
        """
        widget_data = {"type": workflow_name}
        
        # Include ALL fields that have meaningful values
        for field, value in workflow_state.items():
            if self._is_meaningful_value(value):
                widget_data[field] = value
        
        # Only return if we found meaningful data beyond the type
        return widget_data if len(widget_data) > 1 else None
    
    def _format_workflow_result(self, data):
        """
        Format direct workflow result data - completely adaptive.
        """
        # Use a generic type since we don't hardcode workflow detection
        return {
            "type": "workflow_result",
            **{k: v for k, v in data.items() if self._is_meaningful_value(v)}
        }
    
    def _is_workflow_result(self, data):
        """
        Detect if data represents a workflow result using structural analysis.
        No hardcoded patterns.
        """
        if not isinstance(data, dict):
            return False
        
        return self._analyze_structure_for_workflow_patterns(data)
    
    def _analyze_structure_for_workflow_patterns(self, data):
        """
        Analyze data structure to determine if it contains workflow-like patterns.
        Uses structural heuristics instead of hardcoded field names.
        """
        if not isinstance(data, dict) or len(data) < 2:
            return False
        
        # Analyze the data structure characteristics
        has_arrays = any(isinstance(v, list) for v in data.values())
        has_nested_objects = any(isinstance(v, dict) and len(v) > 0 for v in data.values())
        has_meaningful_data = sum(1 for v in data.values() if self._is_meaningful_value(v)) >= 2
        
        # Workflow data typically has:
        # 1. Arrays (results, items, etc.)
        # 2. Nested objects (parameters, details, etc.) 
        # 3. Multiple meaningful fields
        return has_arrays or (has_nested_objects and has_meaningful_data)
    
    def _is_meaningful_value(self, value):
        """
        Determine if a value contains meaningful data worth including in widget.
        """
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False  # Could be meaningful, but often default values
        
        return True

    def _make_json_serializable(self, obj):
        """
        Convert any object to JSON-serializable format.
        Handles AIMessage, BaseMessage, and other non-serializable objects.
        """
        if obj is None:
            return None
        
        # Handle different types
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        
        elif hasattr(obj, 'content'):  # AIMessage, HumanMessage, etc.
            return {
                "type": obj.__class__.__name__,
                "content": str(obj.content)
            }
        
        elif hasattr(obj, 'model_dump'):  # Pydantic models
            try:
                # Recursively process the dumped data to handle nested datetime objects
                dumped = obj.model_dump()
                return self._make_json_serializable(dumped)
            except Exception:
                return str(obj)
        
        elif hasattr(obj, 'dict'):  # Pydantic v1 models
            try:
                # Recursively process the dict data to handle nested datetime objects
                dict_data = obj.dict()
                return self._make_json_serializable(dict_data)
            except Exception:
                return str(obj)
        
        # Handle datetime objects (do this early to catch them before other checks)
        elif isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        
        # Handle UUID objects
        elif isinstance(obj, UUID):
            return str(obj)
        
        # Handle Decimal objects
        elif isinstance(obj, Decimal):
            return float(obj)
        
        # Handle any object that has an isoformat method (catches other datetime types)
        elif hasattr(obj, 'isoformat') and callable(obj.isoformat):
            try:
                return obj.isoformat()
            except Exception:
                return str(obj)
        
        # Handle basic types
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        
        # Convert everything else to string
        else:
            return str(obj)


stream_service = StreamService()