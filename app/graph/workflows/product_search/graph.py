

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.product_search.nodes.extract_search_parameters import extract_search_parameters_node
from app.graph.workflows.product_search.nodes.execute_product_query import execute_product_query_node
from app.graph.workflows.product_search.nodes.format_results import format_results_node
from app.graph.workflows.product_search.nodes.should_extract_or_handle_no_filters import should_extract_or_handle_no_filters
from app.graph.workflows.product_search.nodes.display_search_results import display_search_results_node
from app.graph.workflows.product_search.nodes.handle_no_filters import handle_no_filters_node
from app.graph.workflows.product_search.types import ProductSearchState

class ProductSearchGraph:
    """
    Simplified Product Search Workflow (FTS5-based).
    
    Reduced from 8 nodes to 5 nodes by merging:
    - handle_fallback → merged into execute_product_query
    - filter_results → merged into format_results  
    - handle_no_results_found → merged into display_search_results
    - should_handle_product_search → removed (logic in display_search_results)
    """

    @staticmethod
    def create() -> CompiledStateGraph[ProductSearchState, None, ProductSearchState, ProductSearchState]:
        """Create the simplified product search subgraph."""

        # Use ProductSearchState since we want shared state with parent
        graph = StateGraph(ProductSearchState)

        # Add nodes (5 total - down from 8!)
        graph.add_node("extract_search_parameters", extract_search_parameters_node)
        graph.add_node("execute_product_query", execute_product_query_node)  # includes fallback logic
        graph.add_node("format_results", format_results_node)  # includes deduplication
        graph.add_node("display_search_results", display_search_results_node)  # handles no results too
        graph.add_node("handle_no_filters", handle_no_filters_node)

        # Set entry point
        graph.set_entry_point("extract_search_parameters")
        
        # Simplified pipeline flow:
        # 1. Extract parameters (ONE LLM call)
        # 2. Execute FTS5 search (with built-in fallback)
        # 3. Format results (with deduplication)
        # 4. Display results (handles both results and no results)
        
        # Route from extract_search_parameters based on whether keywords exist
        graph.add_conditional_edges("extract_search_parameters", should_extract_or_handle_no_filters, {
            "execute_product_query": "execute_product_query",
            "handle_no_filters": "handle_no_filters"
        })
        
        # Linear pipeline: execute → format → display
        graph.add_edge("execute_product_query", "format_results")
        graph.add_edge("format_results", "display_search_results")
        
        # End nodes
        graph.add_edge("display_search_results", END)
        graph.add_edge("handle_no_filters", END)

        return graph.compile()
