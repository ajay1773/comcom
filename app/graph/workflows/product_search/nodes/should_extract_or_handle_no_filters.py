from app.graph.workflows.product_search.types import ProductSearchState


async def should_extract_or_handle_no_filters(state: ProductSearchState) -> str:
    """
    Route from extract_search_parameters based on whether meaningful search keywords were provided.
    In the FTS5 pipeline, keywords are required for search.
    """
    
    search_parameters = state.get("search_parameters", {})
    keywords = search_parameters.get("keywords", "").strip()
    
    # If no meaningful keywords were extracted, handle as no filters
    if not keywords or keywords == "":
        return "handle_no_filters"
    else:
        return "execute_product_query"
