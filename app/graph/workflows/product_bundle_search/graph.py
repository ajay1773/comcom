"""Product Bundle Search workflow graph."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.product_bundle_search.nodes.identify_bundle_items import identify_bundle_items_node
from app.graph.workflows.product_bundle_search.nodes.execute_bundle_search import execute_bundle_search_node
from app.graph.workflows.product_bundle_search.nodes.format_bundle_results import format_bundle_results_node
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState


class ProductBundleSearchGraph:
    """
    Product Bundle Search Workflow.

    Flow:
    1. Identify bundle items (LLM analyzes use case)
    2. Execute searches for each item
    3. Format and group results
    """

    @staticmethod
    def create() -> CompiledStateGraph[ProductBundleSearchState, None, ProductBundleSearchState, ProductBundleSearchState]:
        """Create the product bundle search subgraph."""

        graph = StateGraph(ProductBundleSearchState)

        # Add nodes
        graph.add_node("identify_bundle_items", identify_bundle_items_node)
        graph.add_node("execute_bundle_search", execute_bundle_search_node)
        graph.add_node("format_bundle_results", format_bundle_results_node)

        # Set entry point
        graph.set_entry_point("identify_bundle_items")

        # Linear flow: identify → search → format
        graph.add_edge("identify_bundle_items", "execute_bundle_search")
        graph.add_edge("execute_bundle_search", "format_bundle_results")
        graph.add_edge("format_bundle_results", END)

        return graph.compile()

