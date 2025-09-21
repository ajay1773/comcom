from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.models.chat import GlobalState
from app.graph.subgraphs.place_order.nodes.extract_product_details import extract_product_details_node
from app.graph.subgraphs.place_order.nodes.get_selected_product import get_selected_product_node
from app.graph.subgraphs.place_order.nodes.prepare_order_details import prepare_order_details_node

class PlaceOrderGraph:
    """Place order workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[GlobalState, None, GlobalState, GlobalState]:
        """Create the place order subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(GlobalState)

        # Add nodes
        graph.add_node("extract_product_details", extract_product_details_node)
        graph.add_node("get_selected_product", get_selected_product_node)
        graph.add_node("prepare_order_details", prepare_order_details_node)

        # Set entry point
        graph.set_entry_point("extract_product_details")

        # Add edges
        graph.add_edge("extract_product_details", "get_selected_product")
        graph.add_edge("get_selected_product", "prepare_order_details")
        graph.add_edge("prepare_order_details", END)

        return graph.compile()
