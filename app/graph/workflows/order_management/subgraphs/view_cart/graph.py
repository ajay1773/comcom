from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.order_management.subgraphs.view_cart.nodes.get_cart_details_from_db import get_cart_details_from_db_node
from app.graph.workflows.order_management.subgraphs.view_cart.nodes.handle_view_cart_success import handle_view_cart_success_node
from app.graph.workflows.order_management.subgraphs.view_cart.nodes.handle_view_cart_fail import handle_view_cart_fail_node
from app.graph.workflows.order_management.types import ViewCartState


def should_handle_cart_result(state: ViewCartState) -> str:
    """Check if the view cart operation was successful or failed."""
    error_message = state.get("error_message", None)

    if error_message:
        return NodeName.HANDLE_VIEW_CART_FAIL
    else:
        return NodeName.HANDLE_VIEW_CART_SUCCESS


class ViewCartGraph:
    """View cart workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[ViewCartState, None, ViewCartState, ViewCartState]:
        """Create the view cart subgraph."""

        # Use ViewCartState for the subgraph
        graph = StateGraph(ViewCartState)

        # Add workflow nodes
        graph.add_node(NodeName.GET_CART_DETAILS, get_cart_details_from_db_node)
        graph.add_node(NodeName.HANDLE_VIEW_CART_SUCCESS, handle_view_cart_success_node)
        graph.add_node(NodeName.HANDLE_VIEW_CART_FAIL, handle_view_cart_fail_node)

        # Set entry point
        graph.set_entry_point(NodeName.GET_CART_DETAILS)

        # Add conditional edges based on operation success/failure
        graph.add_conditional_edges(
            NodeName.GET_CART_DETAILS,
            should_handle_cart_result,
            {
                NodeName.HANDLE_VIEW_CART_SUCCESS: NodeName.HANDLE_VIEW_CART_SUCCESS,
                NodeName.HANDLE_VIEW_CART_FAIL: NodeName.HANDLE_VIEW_CART_FAIL
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_VIEW_CART_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_VIEW_CART_FAIL, END)

        return graph.compile()
