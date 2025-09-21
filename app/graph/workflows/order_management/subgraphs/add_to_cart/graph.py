from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.order_management.subgraphs.add_to_cart.nodes.add_product_to_cart import add_product_to_cart_node
from app.graph.workflows.order_management.subgraphs.add_to_cart.nodes.extract_product_details_from_prompt import extract_product_details_from_prompt_node
from app.graph.workflows.order_management.subgraphs.add_to_cart.nodes.get_product_from_db import get_product_from_db_node
from app.graph.workflows.order_management.subgraphs.add_to_cart.nodes.handle_success import handle_success_node
from app.graph.workflows.order_management.subgraphs.add_to_cart.nodes.handle_failure import handle_failure_node
from app.graph.workflows.order_management.types import AddToCartState


def should_handle_operation_result(state: AddToCartState) -> str:
    """Check if the add to cart operation was successful or failed."""
    operation_success = state.get("operation_success", False)
    
    if operation_success:
        return NodeName.HANDLE_SUCCESS
    else:
        return NodeName.HANDLE_FAILURE


class AddToCartGraph:
    """Add to cart workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[AddToCartState, None, AddToCartState, AddToCartState]:
        """Create the add to cart subgraph."""

        # Use AddToCartState for the subgraph
        graph = StateGraph(AddToCartState)

        # Add workflow nodes
        graph.add_node(NodeName.EXTRACT_PRODUCT_DETAILS_FROM_PROMPT, extract_product_details_from_prompt_node)
        graph.add_node(NodeName.GET_PRODUCT_FROM_DB, get_product_from_db_node)
        graph.add_node(NodeName.ADD_PRODUCT_TO_CART, add_product_to_cart_node)
        graph.add_node(NodeName.HANDLE_SUCCESS, handle_success_node)
        graph.add_node(NodeName.HANDLE_FAILURE, handle_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_PRODUCT_DETAILS_FROM_PROMPT)

        # Add linear flow with conditional branching at the end
        graph.add_edge(NodeName.EXTRACT_PRODUCT_DETAILS_FROM_PROMPT, NodeName.GET_PRODUCT_FROM_DB)
        graph.add_edge(NodeName.GET_PRODUCT_FROM_DB, NodeName.ADD_PRODUCT_TO_CART)
        
        # Conditional edges based on operation success/failure
        graph.add_conditional_edges(
            NodeName.ADD_PRODUCT_TO_CART,
            should_handle_operation_result,
            {
                NodeName.HANDLE_SUCCESS: NodeName.HANDLE_SUCCESS,
                NodeName.HANDLE_FAILURE: NodeName.HANDLE_FAILURE
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_FAILURE, END)

        return graph.compile()
