from langchain_core.runnables import RunnableConfig
from app.models.chat import GlobalState
from langgraph.graph.state import CompiledStateGraph
from typing import List, Dict, Any
from app.services.db.conversation import conversation_service
from app.services.auth import auth_service
from app.services.widget_events import widget_event_emitter, WidgetEventType
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID


class ConversationHistoryManager:
    """Manages conversation history for persistent chat sessions."""

    def __init__(self, max_history_items: int = 50):
        self.max_history_items = max_history_items

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

    def add_user_message(self, conversation_history: List[str], message: str) -> List[str]:
        """Add a user message to the conversation history."""
        conversation_history = conversation_history or []
        conversation_history.append(f"User: {message}")
        return self._trim_history(conversation_history)

    def add_assistant_message(self, conversation_history: List[str], message: str) -> List[str]:
        """Add an assistant message to the conversation history."""
        conversation_history = conversation_history or []
        latest_event = widget_event_emitter.get_latest_event()
        
        # Create the basic assistant message
        assistant_entry = f"Assistant: {message}"
        
        # If widget JSON is provided, append it as a JSON string
        if latest_event:
            import json
            # Use the serialization helper to handle non-serializable objects
            serializable_payload = self._make_json_serializable(latest_event.payload)
            # Handle both enum and string event types
            event_type_value = latest_event.event_type.value if isinstance(latest_event.event_type, WidgetEventType) else str(latest_event.event_type)
            widget_json_str = json.dumps({"widget_type": event_type_value, "payload": serializable_payload}, separators=(',', ':'))  # Compact JSON
            assistant_entry += f" | Widget: {widget_json_str}"
        
        conversation_history.append(assistant_entry)
        return self._trim_history(conversation_history)

    def add_workflow_message(self, conversation_history: List[str], workflow_type: str, data: Dict[str, Any]) -> List[str]:
        """Add a workflow interaction to the conversation history."""
        conversation_history = conversation_history or []
        # Create a summary of the workflow interaction
        summary = f"Workflow: {workflow_type}"
        if data:
            # Add key information from workflow data
            key_items = []
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (str, int, float, bool)) and key not in ['type']:
                        key_items.append(f"{key}: {value}")
            if key_items:
                summary += f" ({', '.join(key_items[:3])})"  # Limit to 3 items

        conversation_history.append(summary)
        return self._trim_history(conversation_history)


    def get_recent_context(self, conversation_history: List[str], limit: int = 10) -> List[str]:
        """Get the most recent conversation context."""
        if not conversation_history:
            return []

        return conversation_history[-limit:] if len(conversation_history) > limit else conversation_history

    def _trim_history(self, conversation_history: List[str]) -> List[str]:
        """Trim conversation history to prevent memory issues."""
        if len(conversation_history) > self.max_history_items:
            # Keep the most recent items
            return conversation_history[-self.max_history_items:]
        return conversation_history

    def format_for_prompt(self, conversation_history: List[str]) -> str:
        """Format conversation history for use in prompts."""
        if not conversation_history:
            return ""

        # Take the last 20 items for context
        recent_history = self.get_recent_context(conversation_history, 20)
        return "\n".join(recent_history)

    def search_conversation_history(self, conversation_history: List[str], query: str) -> List[str]:
        """Search conversation history for specific content."""
        if not conversation_history or not query:
            return []

        query_lower = query.lower()
        return [
            item for item in conversation_history
            if query_lower in item.lower()
        ]

    def get_conversation_summary(self, conversation_history: List[str], max_items: int = 5) -> str:
        """Get a summary of the most recent conversation items."""
        if not conversation_history:
            return ""

        recent = self.get_recent_context(conversation_history, max_items)
        return f"Recent conversation ({len(recent)} items): {' | '.join(recent)}"



class ChatHistoryState:
    def __init__(self):
        self.messages = []
        self.conversation_manager = ConversationHistoryManager()

    def _create_base_state(self, message: str, token: str, thread_id: str | None) -> dict:
        """Create a base state dictionary with common fields."""
        return {
            "user_message": message,
            "intent": None,
            "conversation_history": [],
            "user_profile": None,
            "response": None,
            "user_id": None,
            "session_token": token,
            "is_authenticated": False,
            "auth_required": False,
            "pending_workflow": None,
            "auth_middleware": None,
            "thread_id": thread_id,
            "current_workflow": "",
            "workflow_history": [],
            "confidence": None,
            "disfluent_message": None,
            "workflow_output_text": None,
            "workflow_output_json": None,
            "workflow_widget_json": None,
            "workflow_error": None,
            "error_recovery_options": None,
            "product_search": None,
            "generate_signin_form": None,
            "generate_signup_form": None,
            "signup_with_details": None,
            "login_with_credentials": None,
            "add_to_cart": None,
            "view_cart": None,
            "user_addresses": None,
            "add_address_form": None,
            "edit_address": None,
            "delete_address": None,
            "delete_from_cart": None,
            "user_profile": None,
        }

    async def _ensure_conversation_exists(self, thread_id: str, token: str) -> None:
        """Ensure conversation exists in database and link to user if authenticated."""
        if not thread_id:
            return
            
        try:
            # Get user from token if available
            user_id = None
            if token:
                try:
                    user = await auth_service.get_user_from_token(token)
                    if user:
                        user_id = user.id
                except Exception:
                    # Token might be invalid, continue without user
                    pass
            
            # Only create conversation for authenticated users
            # For logged-out users, skip conversation persistence
            if user_id:
                # Get or create conversation for authenticated users only
                await conversation_service.get_or_create_conversation(thread_id, user_id)
                print(f"✅ Conversation ensured for authenticated user {user_id}")
            else:
                print(f"⏭️ Skipping conversation persistence for unauthenticated user")
        except Exception as e:
            print(f"⚠️ Failed to ensure conversation exists: {e}")
            # Don't fail the entire flow if conversation management fails

    async def _update_conversation_activity(self, thread_id: str) -> None:
        """Update conversation activity after processing a message."""
        if not thread_id:
            return
            
        try:
            await conversation_service.update_conversation_activity(thread_id)
        except Exception as e:
            print(f"⚠️ Failed to update conversation activity: {e}")
            # Don't fail the entire flow if conversation management fails

    async def get_initial_state_from_config(
        self,
        message: str,
        config: RunnableConfig,
        compiled_graph: CompiledStateGraph[GlobalState, None, GlobalState, GlobalState],
        token: str
    ) -> GlobalState:
        """
        Get initial state from LangGraph checkpointer with conversation history support.
        Handles both existing and new conversations with proper error recovery.
        """
        thread_id = config.get("configurable", {}).get("thread_id")

        # Ensure conversation exists in database
        await self._ensure_conversation_exists(thread_id, token)

        try:
            # Query the checkpointer for existing conversation state
            existing_state = await compiled_graph.aget_state(config)

            if existing_state and existing_state.values:
                # === EXISTING CONVERSATION ===
                print(f"📖 Found existing conversation with {len(existing_state.values.get('conversation_history', []))} items")

                # Load existing conversation history and add the current user message
                existing_conversation_history = existing_state.values.get("conversation_history", [])
                updated_conversation_history = self.conversation_manager.add_user_message(
                    existing_conversation_history, message
                )

                # Create state with existing data and updated conversation history
                base_state = self._create_base_state(message, token, thread_id)
                return GlobalState(
                    user_message=base_state["user_message"],
                    intent=existing_state.values.get("intent"),
                    conversation_history=updated_conversation_history,
                    response=base_state["response"],
                    user_id=existing_state.values.get("user_id"),
                    session_token=base_state["session_token"],
                    is_authenticated=existing_state.values.get("is_authenticated", False),
                    auth_required=existing_state.values.get("auth_required", False),
                    pending_workflow=existing_state.values.get("pending_workflow"),
                    thread_id=existing_state.values.get("thread_id"),
                    current_workflow=existing_state.values.get("current_workflow", ""),
                    workflow_history=existing_state.values.get("workflow_history", []),
                    confidence=existing_state.values.get("confidence"),
                    disfluent_message=existing_state.values.get("disfluent_message"),
                    workflow_output_text=existing_state.values.get("workflow_output_text"),
                    workflow_output_json=existing_state.values.get("workflow_output_json"),
                    workflow_widget_json=existing_state.values.get("workflow_widget_json"),
                    workflow_error=existing_state.values.get("workflow_error"),
                    error_recovery_options=existing_state.values.get("error_recovery_options"),
                    product_search=existing_state.values.get("product_search"),
                    generate_signin_form=existing_state.values.get("generate_signin_form"),
                    generate_signup_form=existing_state.values.get("generate_signup_form"),
                    signup_with_details=existing_state.values.get("signup_with_details"),
                    login_with_credentials=existing_state.values.get("login_with_credentials"),
                    auth_middleware=existing_state.values.get("auth_middleware"),
                    add_to_cart=existing_state.values.get("add_to_cart"),
                    view_cart=existing_state.values.get("view_cart"),
                    user_addresses=existing_state.values.get("user_addresses"),
                    add_address_form=existing_state.values.get("add_address_form"),
                    edit_address=existing_state.values.get("edit_address"),
                    delete_address=existing_state.values.get("delete_address"),
                    delete_from_cart=existing_state.values.get("delete_from_cart"),
                    user_profile=existing_state.values.get("user_profile", {}),
                )

            else:
                # === NEW CONVERSATION ===
                print("🆕 Starting new conversation")
                initial_conversation_history = self.conversation_manager.add_user_message([], message)

                base_state = self._create_base_state(message, token, thread_id)
                return GlobalState(
                    user_message=base_state["user_message"],
                    intent=base_state["intent"],
                    conversation_history=initial_conversation_history,
                    response=base_state["response"],
                    user_id=base_state["user_id"],
                    session_token=base_state["session_token"],
                    is_authenticated=base_state["is_authenticated"],
                    auth_required=base_state["auth_required"],
                    pending_workflow=base_state["pending_workflow"],
                    thread_id=base_state["thread_id"],
                    current_workflow=base_state["current_workflow"],
                    workflow_history=base_state["workflow_history"],
                    confidence=base_state["confidence"],
                    disfluent_message=base_state["disfluent_message"],
                    workflow_output_text=base_state["workflow_output_text"],
                    workflow_output_json=base_state["workflow_output_json"],
                    workflow_widget_json=base_state["workflow_widget_json"],
                    workflow_error=base_state["workflow_error"],
                    error_recovery_options=base_state["error_recovery_options"],
                    product_search=base_state["product_search"],
                    generate_signin_form=base_state["generate_signin_form"],
                    generate_signup_form=base_state["generate_signup_form"],
                    signup_with_details=base_state["signup_with_details"],
                    login_with_credentials=base_state["login_with_credentials"],
                    auth_middleware=base_state["auth_middleware"],
                    add_to_cart=base_state["add_to_cart"],
                    view_cart=base_state["view_cart"],
                    user_addresses=base_state["user_addresses"],
                    add_address_form=base_state["add_address_form"],
                    edit_address=base_state["edit_address"],
                    delete_address=base_state["delete_address"],
                    delete_from_cart=base_state["delete_from_cart"],
                    user_profile=base_state["user_profile"],
                )

        except Exception as e:
            # === FALLBACK MEMORY RECOVERY ===
            print(f"⚠️ Memory lookup failed, using fallback method: {e}")

            # Create a minimal fallback state
            fallback_conversation_history = self.conversation_manager.add_user_message([], message)

            base_state = self._create_base_state(message, token, thread_id)
            return GlobalState(
                user_message=base_state["user_message"],
                intent=base_state["intent"],
                conversation_history=fallback_conversation_history,
                response=base_state["response"],
                user_id=base_state["user_id"],
                session_token=base_state["session_token"],
                is_authenticated=base_state["is_authenticated"],
                auth_required=base_state["auth_required"],
                pending_workflow=base_state["pending_workflow"],
                thread_id=base_state["thread_id"],
                current_workflow=base_state["current_workflow"],
                workflow_history=base_state["workflow_history"],
                confidence=base_state["confidence"],
                disfluent_message=base_state["disfluent_message"],
                workflow_output_text=base_state["workflow_output_text"],
                workflow_output_json=base_state["workflow_output_json"],
                workflow_widget_json=base_state["workflow_widget_json"],
                workflow_error=base_state["workflow_error"],
                error_recovery_options=base_state["error_recovery_options"],
                product_search=base_state["product_search"],
                generate_signin_form=base_state["generate_signin_form"],
                generate_signup_form=base_state["generate_signup_form"],
                signup_with_details=base_state["signup_with_details"],
                login_with_credentials=base_state["login_with_credentials"],
                auth_middleware=base_state["auth_middleware"],
                add_to_cart=base_state["add_to_cart"],
                view_cart=base_state["view_cart"],
                user_addresses=base_state["user_addresses"],
                add_address_form=base_state["add_address_form"],
                edit_address=base_state["edit_address"],
                delete_address=base_state["delete_address"],
                delete_from_cart=base_state["delete_from_cart"],
                user_profile=base_state["user_profile"],
            )

    async def update_conversation_after_processing(self, thread_id: str, token: str = "") -> None:
        """Update conversation metadata after processing a message."""
        # Only update conversation activity for authenticated users
        if token:
            try:
                user = await auth_service.get_user_from_token(token)
                if user:
                    await self._update_conversation_activity(thread_id)
                else:
                    print(f"⏭️ Skipping conversation activity update - no authenticated user")
            except Exception:
                print(f"⏭️ Skipping conversation activity update - invalid token")
        else:
            print(f"⏭️ Skipping conversation activity update - no token provided")


def get_conversation_context_for_workflow(state, limit: int = 10) -> str:
    """
    Utility function to get conversation context for workflow nodes.
    This is a convenient helper that can be used across different workflow nodes.

    Args:
        state: The current workflow state (should contain conversation_history)
        limit: Maximum number of conversation items to include

    Returns:
        Formatted conversation context as a string
    """
    conversation_history = state.get("conversation_history", [])
    return chat_history_state.conversation_manager.format_for_prompt(conversation_history)


# Create the singleton instance
chat_history_state = ChatHistoryState()
