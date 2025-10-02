from app.graph.workflows.product_search.types import ProductSearchState
from app.services.db.product import product_service
from typing import Dict, Any


async def execute_product_query_node(state: ProductSearchState) -> Dict[str, Any]:
    """
    LangGraph node for looking up products in the database based on extracted parameters.
    Returns only updates to the state (LangGraph merges them automatically).
    """
    filters = state.get("search_parameters", {})
    
    # Execute the product search with the provided filters
    results = await product_service.get_products(filters)
    
    return {
        "search_results": results,
        "result_count": len(results),
        "suggestions": [],  # can be populated later
    }

