"""
Legacy utility for extracting subgraph suggestions.
Now uses the centralized response extractor for consistency.
"""
from app.services.response_extractor import response_extractor

def extract_subgraph_suggestions(subgraph_state: dict) -> str:
    """
    Extract suggestions from a subgraph state.
    
    This function maintains backward compatibility while using
    the centralized response extraction logic.
    """
    return response_extractor.extract_subgraph_suggestions(subgraph_state)