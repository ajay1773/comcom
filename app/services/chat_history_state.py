from langchain_core.runnables import RunnableConfig
from app.models.chat import GlobalState
from langgraph.graph.state import CompiledStateGraph
from typing import List, Dict, Any


class ConversationHistoryManager:
    """Manages conversation history for persistent chat sessions."""

    def __init__(self, max_history_items: int = 50):
        self.max_history_items = max_history_items

    def add_user_message(self, conversation_history: List[str], message: str) -> List[str]:
        """Add a user message to the conversation history."""
        conversation_history = conversation_history or []
        conversation_history.append(f"User: {message}")
        return self._trim_history(conversation_history)

    def add_assistant_message(self, conversation_history: List[str], message: str) -> List[str]:
        """Add an assistant message to the conversation history."""
        conversation_history = conversation_history or []
        conversation_history.append(f"Assistant: {message}")
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
            "user_profile": {},
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
        }

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
                    user_profile=existing_state.values.get("user_profile", {}),
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
                    user_profile=base_state["user_profile"],
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
                user_profile=base_state["user_profile"],
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
            )


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
