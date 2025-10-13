"""Type definitions for product comparison workflow."""

from typing import List, Dict, Any, NotRequired
from app.types.common import CommonState, AuthState


class ProductComparisonState(CommonState, AuthState):
    """State for product comparison workflow."""
    
    # Input
    search_query: str
    
    # Extracted data
    product_identifiers: NotRequired[List[Dict[str, Any]]]  # Product names/IDs to compare
    comparison_criteria: NotRequired[List[str]]  # What to compare (price, features, etc.)
    user_context: NotRequired[str]  # User preferences/specific question
    
    # Fetched data
    products: NotRequired[List[Dict[str, Any]]]  # Full product details from DB
    
    # Generated analysis
    comparison_analysis: NotRequired[Dict[str, Any]]  # LLM-generated insights
    comparison_table: NotRequired[Dict[str, Any]]  # Structured comparison data
    recommendation: NotRequired[str]  # AI recommendation
    
    # Output
    workflow_output_text: NotRequired[str]
    workflow_output_json: NotRequired[Dict[str, Any]]
    
    # Metadata
    result_count: NotRequired[int]
    error_message: NotRequired[str]
    category_mismatch_handled: NotRequired[bool]  # Flag for category mismatch handling
    edge_case_handled: NotRequired[bool]  # Flag for any edge case handling

