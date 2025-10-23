from typing import AsyncIterator, cast, Optional
from uuid import uuid4, UUID
from datetime import datetime, date, time
from decimal import Decimal
from langchain_core.runnables import RunnableConfig
from app.services.chat_history_state import chat_history_state
from app.graph.workflows.base import create_base_graph
from app.services.widget_events import widget_event_emitter
from app.services.token_counter import token_counter_service
from app.services.rate_limiter import rate_limiter_service
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
            "extract_signup_details",
            "output_handler"
        }
        
        # Set up widget event listener
        widget_event_emitter.add_listener("*", self._handle_widget_event)
        self._current_stream_generator = None

    def _handle_widget_event(self, event):
        """Handle widget events by storing them for streaming."""
        # Store the event to be streamed
        self._latest_widget_event = event

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

        # Clear any previous widget events
        widget_event_emitter.clear_events()
        self._latest_widget_event = None

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
                        if hasattr(chunk, "content") and chunk.content is not None:
                            content = chunk.content
                            # Allow all content including whitespace, but filter out empty strings
                            if content != "":
                                yield f"data: {json.dumps({'event_name': 'llm_stream', 'text': content})}\n\n"

            # Handle workflow completion - check for widget events
            elif event_name == "LangGraph" and event_type == "on_chain_end":
                # Check if any widget events were emitted during this workflow
                latest_event = widget_event_emitter.get_latest_event()
                if latest_event and latest_event != getattr(self, '_last_streamed_event', None):
                    try:
                        # Stream the widget event
                        event_data = {
                            'event_name': 'widget_event',
                            'widget_type': latest_event.event_type.value,
                            'payload': self._make_json_serializable(latest_event.payload)
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"
                        self._last_streamed_event = latest_event
                    except (TypeError, ValueError) as e:
                        logger.error(f"Failed to serialize widget event: {e}")
                        error_json = {"error": "Failed to serialize widget event", "message": str(e)}
                        yield f"data: {json.dumps({'event_name': 'widget_event', 'widget_type': 'error', 'payload': error_json})}\n\n"

            # Handle final output from output_handler
            elif event_name == "output_handler" and event_type == "on_chain_end":
                # Output handler only manages conversation history now
                # Text streaming is handled by individual workflow nodes
                # No need to stream the complete text again
                pass
        
        # Update conversation activity after processing is complete (only for authenticated users)
        await chat_history_state.update_conversation_after_processing(thread_id, token)

    async def stream_base_graph_with_token_tracking(
        self, message: str, thread_id: str, token: str, user_id: Optional[int] = None
    ) -> AsyncIterator[str]:
        """
        Stream a message with Base Graph and track token usage for logged-in users.
        
        Args:
            message: User's input message
            thread_id: Thread identifier for conversation
            token: Authentication token (if any)
            user_id: User ID for token tracking (if authenticated)
        """
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

        # Clear any previous widget events
        widget_event_emitter.clear_events()
        self._latest_widget_event = None

        # Track tokens for this conversation
        prompt_tokens = token_counter_service.count_tokens(message)
        completion_tokens = 0
        accumulated_response = ""

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
                    disfluent_text = output.get('disfluent_message')
                    accumulated_response += disfluent_text
                    yield f"data: {json.dumps({'event_name': 'disfluency_generated', 'text': disfluent_text})}\n\n"

            # Handle streaming from user-facing nodes only
            elif event_type == "on_chat_model_stream":
                # Get the actual node name from metadata
                actual_node_name = event.get("metadata", {}).get("langgraph_node", "")
                
                # Only stream from nodes that should provide user-facing content
                if actual_node_name not in self.non_streaming_nodes:
                    event_data = event.get("data", {})
                    if "chunk" in event_data:
                        chunk = event_data["chunk"]
                        if hasattr(chunk, "content") and chunk.content is not None:
                            content = chunk.content
                            # Allow all content including whitespace, but filter out empty strings
                            if content != "":
                                accumulated_response += content
                                yield f"data: {json.dumps({'event_name': 'llm_stream', 'text': content})}\n\n"

            # Handle workflow completion - check for widget events
            elif event_name == "LangGraph" and event_type == "on_chain_end":
                # Check if any widget events were emitted during this workflow
                latest_event = widget_event_emitter.get_latest_event()
                if latest_event and latest_event != getattr(self, '_last_streamed_event', None):
                    try:
                        # Stream the widget event
                        event_data = {
                            'event_name': 'widget_event',
                            'widget_type': latest_event.event_type.value,
                            'payload': self._make_json_serializable(latest_event.payload)
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"
                        self._last_streamed_event = latest_event
                    except (TypeError, ValueError) as e:
                        logger.error(f"Failed to serialize widget event: {e}")
                        error_json = {"error": "Failed to serialize widget event", "message": str(e)}
                        yield f"data: {json.dumps({'event_name': 'widget_event', 'widget_type': 'error', 'payload': error_json})}\n\n"

            # Handle final output from output_handler
            elif event_name == "output_handler" and event_type == "on_chain_end":
                # Output handler only manages conversation history now
                # Text streaming is handled by individual workflow nodes
                # No need to stream the complete text again
                pass
        
        # Calculate completion tokens from accumulated response
        completion_tokens = token_counter_service.count_tokens(accumulated_response)
        total_tokens = prompt_tokens + completion_tokens
        
        # Record token usage for authenticated users
        if user_id:
            try:
                token_usage = await rate_limiter_service.record_token_usage(user_id, total_tokens)
                logger.info(
                    f"Token usage recorded for user {user_id}: "
                    f"{total_tokens} tokens (prompt: {prompt_tokens}, completion: {completion_tokens}). "
                    f"Total today: {token_usage['tokens_used']}/{token_usage['daily_limit']}"
                )
                
                # Send token usage info to client
                usage_event = {
                    'event_name': 'token_usage',
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'tokens_used_today': token_usage['tokens_used'],
                    'remaining_tokens': token_usage['remaining_tokens'],
                    'daily_limit': token_usage['daily_limit']
                }
                yield f"data: {json.dumps(usage_event)}\n\n"
                
            except Exception as e:
                logger.error(f"Failed to record token usage for user {user_id}: {e}")
        else:
            # For logged-out users, just log the token count
            logger.info(f"Logged-out user conversation used {total_tokens} tokens (prompt: {prompt_tokens}, completion: {completion_tokens})")
        
        # Update conversation activity after processing is complete (only for authenticated users)
        await chat_history_state.update_conversation_after_processing(thread_id, token)

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