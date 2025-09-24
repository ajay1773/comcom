from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.order_management.subgraphs.delete_from_cart.nodes.delete_product import delete_product_from_cart_node
from app.graph.workflows.order_management.subgraphs.delete_from_cart.nodes.extract_product_details_from_prompt import extract_product_details_from_prompt_node
from app.graph.workflows.order_management.subgraphs.delete_from_cart.nodes.handle_success import handle_success_node
from app.graph.workflows.order_management.subgraphs.delete_from_cart.nodes.handle_failure import handle_failure_node
from app.graph.workflows.order_management.types import DeleteFromCartState


def should_handle_operation_result(state: DeleteFromCartState) -> str:
    """Check if the delete from cart operation was successful or failed."""
    operation_success = state.get("cart_delete_success", False)
    
    if operation_success:
        return NodeName.HANDLE_SUCCESS
    else:
        return NodeName.HANDLE_FAILURE


class DeleteFromCartGraph:
    """Delete from cart workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[DeleteFromCartState, None, DeleteFromCartState, DeleteFromCartState]:
        """Create the delete from cart subgraph."""

        # Use DeleteFromCartState for the subgraph
        graph = StateGraph(DeleteFromCartState)

        # Add workflow nodes
        graph.add_node(NodeName.EXTRACT_PRODUCT_DETAILS_FROM_PROMPT, extract_product_details_from_prompt_node)
        graph.add_node(NodeName.DELETE_PRODUCT_FROM_CART, delete_product_from_cart_node)
        graph.add_node(NodeName.HANDLE_SUCCESS, handle_success_node)
        graph.add_node(NodeName.HANDLE_FAILURE, handle_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_PRODUCT_DETAILS_FROM_PROMPT)

        # Add linear flow with conditional branching at the end
        graph.add_edge(NodeName.EXTRACT_PRODUCT_DETAILS_FROM_PROMPT, NodeName.DELETE_PRODUCT_FROM_CART)
        
        # Conditional edges based on operation success/failure
        graph.add_conditional_edges(
            NodeName.DELETE_PRODUCT_FROM_CART,
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
