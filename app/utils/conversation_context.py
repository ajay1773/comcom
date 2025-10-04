"""
Utility functions for handling conversation context in workflow nodes.
Provides consistent formatting and error handling across all workflows.
"""

from typing import Any, Dict, Union, Mapping
from app.services.chat_history_state import get_conversation_context_for_workflow


def format_conversation_context(
    state: Union[Dict[str, Any], Mapping[str, Any]],
    context_template: str,
    limit: int = 5,
    fallback_message: str = ""
) -> str:
    """
    Format conversation context for use in LLM prompts with proper escaping and error handling.
    
    Args:
        state: The workflow state containing conversation_history
        context_template: Template string where {escaped_context} will be replaced with conversation history
        limit: Maximum number of conversation items to include (default: 5)
        fallback_message: Message to return if no conversation context is available
        
    Returns:
        Formatted conversation context string ready for use in prompts
        
    Example:
        template = '''
        CONVERSATION CONTEXT:
        The following is the recent conversation history:
        
        {escaped_context}
        
        Use this context to understand the user's request.
        '''
        
        context = format_conversation_context(state, template, limit=3)
    """
    # Input validation
    if not isinstance(state, (dict, Mapping)):
        return fallback_message
    
    if not isinstance(context_template, str):
        return fallback_message
    
    if not isinstance(limit, int) or limit <= 0:
        limit = 5
    
    # Get conversation history from state
    conversation_history = state.get("conversation_history", [])
    
    # Validate conversation history
    if not isinstance(conversation_history, list):
        return fallback_message
    
    if not conversation_history:
        return fallback_message
    
    try:
        # Get formatted conversation context using the existing utility
        conversation_context = get_conversation_context_for_workflow(state, limit=limit)
        
        # Additional safety check
        if not conversation_context or not isinstance(conversation_context, str):
            return fallback_message
        
        # Escape braces for prompt template safety
        escaped_context = conversation_context.replace("{", "{{").replace("}", "}}")
        
        # Validate that the template contains the placeholder
        if "{escaped_context}" not in context_template:
            # If template doesn't have placeholder, just return the escaped context
            return escaped_context
        
        # Format the template with escaped context
        formatted_context = context_template.format(escaped_context=escaped_context)
        
        return formatted_context.strip()
        
    except Exception as e:
        # Log the error if logging is available, otherwise fail silently
        print(f"Warning: Error formatting conversation context: {e}")
        return fallback_message


def get_conversation_context_simple(
    state: Union[Dict[str, Any], Mapping[str, Any]],
    limit: int = 5,
    join_separator: str = "\n"
) -> str:
    """
    Get simple conversation context without template formatting.
    
    Args:
        state: The workflow state containing conversation_history
        limit: Maximum number of conversation items to include
        join_separator: Separator to use when joining conversation items
        
    Returns:
        Simple conversation context string
    """
    # Input validation
    if not isinstance(state, (dict, Mapping)):
        return ""
    
    conversation_history = state.get("conversation_history", [])
    
    if not isinstance(conversation_history, list) or not conversation_history:
        return ""
    
    try:
        # Get the most recent conversation items
        recent_history = conversation_history[-limit:] if len(conversation_history) > limit else conversation_history
        
        # Filter out empty or invalid items
        valid_items = [item for item in recent_history if isinstance(item, str) and item.strip()]
        
        if not valid_items:
            return ""
        
        return join_separator.join(valid_items)
        
    except Exception as e:
        print(f"Warning: Error getting simple conversation context: {e}")
        return ""


def has_conversation_context(state: Union[Dict[str, Any], Mapping[str, Any]]) -> bool:
    """
    Check if the state has valid conversation context.
    
    Args:
        state: The workflow state to check
        
    Returns:
        True if conversation context is available, False otherwise
    """
    if not isinstance(state, (dict, Mapping)):
        return False
    
    conversation_history = state.get("conversation_history", [])
    
    if not isinstance(conversation_history, list):
        return False
    
    # Check if there are any non-empty string items
    return any(isinstance(item, str) and item.strip() for item in conversation_history)


# Pre-defined templates for common use cases
TEMPLATES = {
    "parameter_extraction": """
CONVERSATION CONTEXT:
The following is the recent conversation history to help you understand the user's preferences and previous interactions:

{escaped_context}

Use this context to better understand the user's current request and any preferences they've expressed.
""",
    
    "search_refinement": """
PREVIOUS CONVERSATION:
Here's what the user discussed earlier:

{escaped_context}

Consider this context when refining the search or understanding follow-up requests.
""",
    
    "order_processing": """
CONVERSATION HISTORY:
Previous interactions with the user:

{escaped_context}

Use this context to understand the user's order intent and preferences.
""",
    
    "general": """
CONTEXT:
Recent conversation:

{escaped_context}

Use this information to provide a more contextual response.
"""
}


def format_conversation_context_with_template(
    state: Union[Dict[str, Any], Mapping[str, Any]],
    template_name: str = "general",
    limit: int = 5,
    fallback_message: str = ""
) -> str:
    """
    Format conversation context using a pre-defined template.
    
    Args:
        state: The workflow state containing conversation_history
        template_name: Name of the pre-defined template to use
        limit: Maximum number of conversation items to include
        fallback_message: Message to return if no conversation context is available
        
    Returns:
        Formatted conversation context string
    """
    template = TEMPLATES.get(template_name, TEMPLATES["general"])
    return format_conversation_context(state, template, limit, fallback_message)
