from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.models.chat import GlobalState
from app.graph.subgraphs.product_search.nodes.extract_params import extract_params_node
from app.graph.subgraphs.product_search.nodes.product_db_lookup import product_db_lookup_node

class ProductSearchGraph:
    """Product search workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[GlobalState, None, GlobalState, GlobalState]:
        """Create the product search subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(GlobalState)

        # Add nodes
        graph.add_node("extract_params", extract_params_node)
        graph.add_node("product_lookup", product_db_lookup_node)

        # Set entry point
        graph.set_entry_point("extract_params")

        # Add edges
        graph.add_edge("extract_params", "product_lookup")
        graph.add_edge("product_lookup", END)

        return graph.compile()
