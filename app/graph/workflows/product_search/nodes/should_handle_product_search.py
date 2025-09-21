

from app.graph.workflows.product_search.types import ProductSearchState


async def should_handle_product_search(state: ProductSearchState) -> str:
    """Should handle product search results."""

    return "display_search_results" if state.get("result_count") > 0 else "handle_no_results_found"