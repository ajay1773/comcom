

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.product_search.nodes.extract_search_parameters import extract_search_parameters_node
from app.graph.workflows.product_search.nodes.execute_product_query import execute_product_query_node
from app.graph.workflows.product_search.nodes.should_handle_product_search import should_handle_product_search
from app.graph.workflows.product_search.nodes.should_extract_or_handle_no_filters import should_extract_or_handle_no_filters
from app.graph.workflows.product_search.nodes.display_search_results import display_search_results_node
from app.graph.workflows.product_search.nodes.handle_no_results_found import handle_no_results_found_node
from app.graph.workflows.product_search.nodes.handle_no_filters import handle_no_filters_node
from app.graph.workflows.product_search.types import ProductSearchState

class ProductSearchGraph:
    """Product search workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[ProductSearchState, None, ProductSearchState, ProductSearchState]:
        """Create the product search subgraph."""

        # Use ProductSearchState since we want shared state with parent
        graph = StateGraph(ProductSearchState)

        # Add nodes
        graph.add_node("extract_search_parameters", extract_search_parameters_node)
        graph.add_node("execute_product_query", execute_product_query_node)
        graph.add_node("display_search_results", display_search_results_node)
        graph.add_node("handle_no_results_found", handle_no_results_found_node)
        graph.add_node("handle_no_filters", handle_no_filters_node)

        # Set entry point and routing
        graph.set_entry_point("extract_search_parameters")
        
        # Route from extract_search_parameters based on whether filters were provided
        graph.add_conditional_edges("extract_search_parameters", should_extract_or_handle_no_filters, {
            "execute_product_query": "execute_product_query",
            "handle_no_filters": "handle_no_filters"
        })
        
        # Route from execute_product_query based on results
        graph.add_conditional_edges("execute_product_query", should_handle_product_search, {
            "display_search_results": "display_search_results",
            "handle_no_results_found": "handle_no_results_found"
        })
        
        # End nodes
        graph.add_edge("display_search_results", END)
        graph.add_edge("handle_no_results_found", END)
        graph.add_edge("handle_no_filters", END)


        return graph.compile()
