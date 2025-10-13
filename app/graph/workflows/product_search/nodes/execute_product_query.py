from app.graph.workflows.product_search.types import ProductSearchState
from app.services.db.product import product_service
from typing import Dict, Any, List, cast


async def execute_product_query_node(state: ProductSearchState) -> Dict[str, Any]:
    """
    LangGraph node for executing FTS5-based product search with built-in fallback.
    Uses the simplified search parameters extracted by LLM.
    Returns only updates to the state (LangGraph merges them automatically).
    """
    search_params = state.get("search_parameters", {})
    
    # Execute FTS5 search with extracted parameters
    # FTS5 automatically handles:
    # - Typos and case insensitivity
    # - Relevance ranking using BM25 algorithm
    # - Partial matches
    results = await product_service.search_products_fts(search_params, limit=20)
    result_count = len(results)
    suggestions = []
    
    # # Built-in fallback handling for poor results
    # if result_count == 0:
    #     # Try relaxing constraints progressively
    #     results, suggestions = await _handle_zero_results(search_params)
    #     result_count = len(results)
    # elif result_count < 3:
    #     # Try to expand results slightly
    #     results, suggestions = await _handle_few_results(search_params, results)
    #     result_count = len(results)
    
    return {
        "search_results": results,
        "result_count": result_count,
        "suggestions": suggestions
    }


async def _handle_zero_results(search_params: Dict[str, Any]) -> tuple[List[Any], List[Dict[str, str]]]:
    """Handle zero results by relaxing constraints."""
    keywords = search_params.get("keywords", "")
    suggestions = []
    
    # Try 1: Remove price constraints
    if search_params.get("price_min") or search_params.get("price_max"):
        relaxed_params = search_params.copy()
        relaxed_params.pop("price_min", None)
        relaxed_params.pop("price_max", None)
        
        products = await product_service.search_products_fts(relaxed_params, limit=10)
        if products:
            suggestions.append({
                "type": "relaxed_price",
                "message": "No products found in your price range. Showing all available options."
            })
            return products, suggestions
    
    # Try 2: Remove rating filter
    if search_params.get("rating_min"):
        relaxed_params = search_params.copy()
        relaxed_params.pop("rating_min", None)
        relaxed_params.pop("price_min", None)
        relaxed_params.pop("price_max", None)
        
        products = await product_service.search_products_fts(relaxed_params, limit=10)
        if products:
            suggestions.append({
                "type": "relaxed_rating",
                "message": "No highly-rated products found. Showing products with all ratings."
            })
            return products, suggestions
    
    # Try 3: Remove gender filter
    if search_params.get("gender"):
        relaxed_params = search_params.copy()
        relaxed_params.pop("gender", None)
        relaxed_params.pop("price_min", None)
        relaxed_params.pop("price_max", None)
        relaxed_params.pop("rating_min", None)
        
        products = await product_service.search_products_fts(relaxed_params, limit=10)
        if products:
            suggestions.append({
                "type": "broadened_search",
                "message": "Limited results found. Showing products for all genders."
            })
            return products, suggestions
    
    # Try 4: Very broad search with first keyword only
    popular_products = await product_service.search_products_fts(
        {"keywords": keywords.split()[0] if keywords else "product", "in_stock_only": False}, 
        limit=10
    )
    
    if not popular_products:
        # Ultimate fallback
        popular_products = await product_service.search_products("", limit=10)
    
    suggestions.append({
        "type": "popular",
        "message": "No matches found. Here are some products you might like."
    })
    
    return popular_products, suggestions


async def _handle_few_results(
    search_params: Dict[str, Any],
    current_products: List[Any]
) -> tuple[List[Any], List[Dict[str, str]]]:
    """Expand search slightly to include more results."""
    keywords = search_params.get("keywords", "")
    suggestions = []
    
    # Broaden the search by removing some constraints
    relaxed_params = {
        "keywords": keywords,
        "in_stock_only": search_params.get("in_stock_only", True)
    }
    
    # Keep only gender filter if present
    if gender := search_params.get("gender"):
        relaxed_params["gender"] = gender
    
    # Search with relaxed parameters
    related_products = await product_service.search_products_fts(relaxed_params, limit=15)
    
    # Add products not already in results
    # Products from service are dicts - cast for type checker
    current_ids = {cast(Dict[str, Any], p)["id"] for p in current_products}
    new_products = [p for p in related_products if cast(Dict[str, Any], p)["id"] not in current_ids]
    
    if new_products:
        all_products = current_products + new_products[:5]
        suggestions.append({
            "type": "related",
            "message": "We also found these related products you might like."
        })
        return all_products, suggestions
    
    return current_products, suggestions

