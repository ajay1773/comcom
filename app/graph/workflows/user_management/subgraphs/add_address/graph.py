"""Add address subgraph for saving user addresses to database."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.user_management.subgraphs.add_address.nodes.extract_address_details import extract_address_details_node
from app.graph.workflows.user_management.subgraphs.add_address.nodes.save_address_details import save_address_details_node
from app.graph.workflows.user_management.subgraphs.add_address.nodes.handle_address_save_success import handle_address_save_success_node
from app.graph.workflows.user_management.subgraphs.add_address.nodes.handle_address_save_failure import handle_address_save_failure_node
from app.graph.workflows.user_management.types import AddAddressState


def should_handle_save_success(state: AddAddressState) -> str:
    """Determine if address save was successful or failed."""
    if state.get("address_save_success", False):
        return NodeName.HANDLE_ADDRESS_SAVE_SUCCESS
    else:
        return NodeName.HANDLE_ADDRESS_SAVE_FAILURE


class AddAddressGraph:
    """Add address workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[AddAddressState, None, AddAddressState, AddAddressState]:
        """Create the add address subgraph."""

        # Use AddAddressState for the subgraph
        graph = StateGraph(AddAddressState)

        # Add all workflow nodes
        graph.add_node(NodeName.EXTRACT_ADDRESS_DETAILS, extract_address_details_node)
        graph.add_node(NodeName.SAVE_ADDRESS_DETAILS, save_address_details_node)
        graph.add_node(NodeName.HANDLE_ADDRESS_SAVE_SUCCESS, handle_address_save_success_node)
        graph.add_node(NodeName.HANDLE_ADDRESS_SAVE_FAILURE, handle_address_save_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_ADDRESS_DETAILS)

        # Linear flow: extract -> save
        graph.add_edge(NodeName.EXTRACT_ADDRESS_DETAILS, NodeName.SAVE_ADDRESS_DETAILS)

        # Conditional edges from save node based on success/failure
        graph.add_conditional_edges(
            NodeName.SAVE_ADDRESS_DETAILS,
            should_handle_save_success,
            {
                NodeName.HANDLE_ADDRESS_SAVE_SUCCESS: NodeName.HANDLE_ADDRESS_SAVE_SUCCESS,
                NodeName.HANDLE_ADDRESS_SAVE_FAILURE: NodeName.HANDLE_ADDRESS_SAVE_FAILURE
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_ADDRESS_SAVE_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_ADDRESS_SAVE_FAILURE, END)

        return graph.compile()
