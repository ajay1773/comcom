from app.graph.workflows.product_search.types import ProductSearchState


async def should_extract_or_handle_no_filters(state: ProductSearchState) -> str:
    """Route from extract_search_parameters based on whether filters were provided."""
    
    # Check if no filters were provided
    search_parameters = state.get("search_parameters", {})
    no_filter_values = all(value is None for value in search_parameters.values())
    
    if no_filter_values:
        return "handle_no_filters"
    else:
        return "execute_product_query"
