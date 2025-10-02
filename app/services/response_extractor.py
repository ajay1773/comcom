"""
Response extraction service for standardizing workflow outputs.

This service provides a centralized way to extract text responses from various
workflow output patterns, eliminating the need for manual response assignment
in individual workflow runners.
"""

from typing import Dict, Any, Optional
from app.models.chat import GlobalState


class ResponseExtractor:
    """
    Centralized service for extracting text responses from workflow states.
    
    This class handles the various patterns used across workflows to provide
    text responses, including suggestions arrays, workflow_output_text fields,
    and other response patterns.
    """
    
    @staticmethod
    def extract_text_response(state: GlobalState) -> str:
        """
        Extract the primary text response from a workflow state.
        
        This method checks multiple sources in order of priority:
        1. Explicit response field (highest priority)
        2. workflow_output_text (standardized output)
        3. suggestions[0] (legacy pattern)
        4. Subgraph-specific suggestions patterns
        5. Empty string (fallback)
        
        Args:
            state: The global state containing workflow outputs
            
        Returns:
            The extracted text response, or empty string if none found
        """
        # 1. Check if response is already explicitly set
        if state.get("response"):
            return str(state["response"])
        
        # 2. Check for standardized workflow_output_text
        if state.get("workflow_output_text"):
            return str(state["workflow_output_text"])
        
        # 3. Check for suggestions pattern (legacy)
        suggestions = state.get("suggestions", [])
        if suggestions and len(suggestions) > 0:
            return str(suggestions[0])
        
        # 4. Check subgraph-specific suggestions patterns
        response = ResponseExtractor._extract_from_subgraphs(state)
        if response:
            return response
        
        # 5. Fallback to empty string
        return ""
    
    @staticmethod
    def _extract_from_subgraphs(state: GlobalState) -> Optional[str]:
        """
        Extract responses from subgraph states.
        
        This method checks various subgraph states for their suggestions
        or output patterns.
        
        Args:
            state: The global state containing subgraph states
            
        Returns:
            The extracted response or None if not found
        """
        # Define subgraph keys to check
        subgraph_keys = [
            "product_search",
            "add_to_cart", 
            "view_cart",
            "delete_from_cart",
            "checkout",
            "checkout_ui_provider",
            "checkout_processor",
            "order_view",
            "generate_signin_form",
            "login_with_credentials", 
            "generate_signup_form",
            "signup_with_details",
            "user_profile",
            "user_addresses",
            "add_address",
            "edit_address",
            "delete_address"
            "order_confirmation"
            "payment_status"
            "error_message"
            "success_message"
            "order_view_failure"
            "order_view_success"
            "order_view_failure_handler"
            "format_order_response"
            "order_view_failure_handler"
            "order_view_failure_handler"
        ]
        
        for key in subgraph_keys:
            subgraph_state = state.get(key)
            if not subgraph_state:
                continue
                
            # Check for workflow_output_text in subgraph
            if subgraph_state.get("workflow_output_text"):
                return str(subgraph_state["workflow_output_text"])
                
            # Check for suggestions in subgraph
            suggestions = subgraph_state.get("suggestions", [])
            if suggestions and len(suggestions) > 0:
                return str(suggestions[0])
        
        return None
    
    @staticmethod
    def extract_subgraph_suggestions(subgraph_state: Dict[str, Any]) -> str:
        """
        Legacy compatibility method for extract_subgraph_suggestions utility.
        
        This method maintains backward compatibility with the existing
        extract_subgraph_suggestions function while providing the same
        centralized logic.
        
        Args:
            subgraph_state: The subgraph state dictionary
            
        Returns:
            The extracted suggestion or empty string
        """
        if not subgraph_state:
            return ""
            
        # Check for workflow_output_text first (preferred)
        if subgraph_state.get("workflow_output_text"):
            return str(subgraph_state["workflow_output_text"])
            
        # Fall back to suggestions pattern
        suggestions = subgraph_state.get("suggestions", [])
        if suggestions and len(suggestions) > 0:
            return str(suggestions[0])
            
        return ""


# Create a singleton instance for easy importing
response_extractor = ResponseExtractor()
