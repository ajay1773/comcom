from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.order_management.subgraphs.edit_cart.nodes.extract_edit_details import extract_edit_details_node
from app.graph.workflows.order_management.subgraphs.edit_cart.nodes.identify_cart_item import identify_cart_item_node
from app.graph.workflows.order_management.subgraphs.edit_cart.nodes.apply_cart_edit import apply_cart_edit_node
from app.graph.workflows.order_management.subgraphs.edit_cart.nodes.handle_edit_success import handle_edit_success_node
from app.graph.workflows.order_management.subgraphs.edit_cart.nodes.handle_edit_failure import handle_edit_failure_node
from app.graph.workflows.order_management.types import EditCartState


def should_continue_to_apply_edit(state: EditCartState) -> str:
    """Check if we successfully identified the cart item to edit."""
    error_message = state.get("error_message", None)
    matched_cart_item = state.get("matched_cart_item", None)
    
    if error_message or not matched_cart_item:
        return NodeName.HANDLE_EDIT_FAILURE
    else:
        return NodeName.APPLY_CART_EDIT


def should_handle_edit_result(state: EditCartState) -> str:
    """Check if the edit operation was successful or failed."""
    edit_success = state.get("edit_success", False)
    
    if edit_success:
        return NodeName.HANDLE_EDIT_SUCCESS
    else:
        return NodeName.HANDLE_EDIT_FAILURE


class EditCartGraph:
    """Edit cart workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[EditCartState, None, EditCartState, EditCartState]:
        """Create the edit cart subgraph."""

        # Use EditCartState for the subgraph
        graph = StateGraph(EditCartState)

        # Add workflow nodes
        graph.add_node(NodeName.EXTRACT_EDIT_CART_DETAILS, extract_edit_details_node)
        graph.add_node(NodeName.IDENTIFY_CART_ITEM, identify_cart_item_node)
        graph.add_node(NodeName.APPLY_CART_EDIT, apply_cart_edit_node)
        graph.add_node(NodeName.HANDLE_EDIT_SUCCESS, handle_edit_success_node)
        graph.add_node(NodeName.HANDLE_EDIT_FAILURE, handle_edit_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_EDIT_CART_DETAILS)

        # Add linear flow with conditional branching
        graph.add_edge(NodeName.EXTRACT_EDIT_CART_DETAILS, NodeName.IDENTIFY_CART_ITEM)
        
        # Conditional edge after identifying item
        graph.add_conditional_edges(
            NodeName.IDENTIFY_CART_ITEM,
            should_continue_to_apply_edit,
            {
                NodeName.APPLY_CART_EDIT: NodeName.APPLY_CART_EDIT,
                NodeName.HANDLE_EDIT_FAILURE: NodeName.HANDLE_EDIT_FAILURE
            }
        )
        
        # Conditional edges based on operation success/failure
        graph.add_conditional_edges(
            NodeName.APPLY_CART_EDIT,
            should_handle_edit_result,
            {
                NodeName.HANDLE_EDIT_SUCCESS: NodeName.HANDLE_EDIT_SUCCESS,
                NodeName.HANDLE_EDIT_FAILURE: NodeName.HANDLE_EDIT_FAILURE
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_EDIT_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_EDIT_FAILURE, END)

        return graph.compile()

