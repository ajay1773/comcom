"""Delete address subgraph for removing user addresses from database."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.user_management.subgraphs.delete_address.nodes.extract_address_id import extract_address_id_node
from app.graph.workflows.user_management.subgraphs.delete_address.nodes.validate_delete_permissions import validate_delete_permissions_node
from app.graph.workflows.user_management.subgraphs.delete_address.nodes.delete_address import delete_address_node
from app.graph.workflows.user_management.subgraphs.delete_address.nodes.handle_address_delete_success import handle_address_delete_success_node
from app.graph.workflows.user_management.subgraphs.delete_address.nodes.handle_address_delete_failure import handle_address_delete_failure_node
from app.graph.workflows.user_management.types import DeleteAddressState


def should_proceed_to_validation(state: DeleteAddressState) -> str:
    """Determine if we should proceed to validation or handle failure."""
    if state.get("address_id"):
        return NodeName.VALIDATE_DELETE_PERMISSIONS
    else:
        return NodeName.HANDLE_ADDRESS_DELETE_FAILURE


def should_proceed_to_delete(state: DeleteAddressState) -> str:
    """Determine if we should proceed to delete or handle failure."""
    if state.get("existing_address") and not state.get("error_message"):
        return NodeName.DELETE_ADDRESS
    else:
        return NodeName.HANDLE_ADDRESS_DELETE_FAILURE


def should_handle_delete_result(state: DeleteAddressState) -> str:
    """Determine if address deletion was successful or failed."""
    if state.get("address_delete_success", False):
        return NodeName.HANDLE_ADDRESS_DELETE_SUCCESS
    else:
        return NodeName.HANDLE_ADDRESS_DELETE_FAILURE


class DeleteAddressGraph:
    """Delete address workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[DeleteAddressState, None, DeleteAddressState, DeleteAddressState]:
        """Create the delete address subgraph."""

        # Use DeleteAddressState for the subgraph
        graph = StateGraph(DeleteAddressState)

        # Add all workflow nodes
        graph.add_node(NodeName.EXTRACT_ADDRESS_ID, extract_address_id_node)
        graph.add_node(NodeName.VALIDATE_DELETE_PERMISSIONS, validate_delete_permissions_node)
        graph.add_node(NodeName.DELETE_ADDRESS, delete_address_node)
        graph.add_node(NodeName.HANDLE_ADDRESS_DELETE_SUCCESS, handle_address_delete_success_node)
        graph.add_node(NodeName.HANDLE_ADDRESS_DELETE_FAILURE, handle_address_delete_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_ADDRESS_ID)

        # Conditional edge from extract to validation or failure
        graph.add_conditional_edges(
            NodeName.EXTRACT_ADDRESS_ID,
            should_proceed_to_validation,
            {
                NodeName.VALIDATE_DELETE_PERMISSIONS: NodeName.VALIDATE_DELETE_PERMISSIONS,
                NodeName.HANDLE_ADDRESS_DELETE_FAILURE: NodeName.HANDLE_ADDRESS_DELETE_FAILURE
            }
        )

        # Conditional edge from validation to delete or failure
        graph.add_conditional_edges(
            NodeName.VALIDATE_DELETE_PERMISSIONS,
            should_proceed_to_delete,
            {
                NodeName.DELETE_ADDRESS: NodeName.DELETE_ADDRESS,
                NodeName.HANDLE_ADDRESS_DELETE_FAILURE: NodeName.HANDLE_ADDRESS_DELETE_FAILURE
            }
        )

        # Conditional edges from delete node based on success/failure
        graph.add_conditional_edges(
            NodeName.DELETE_ADDRESS,
            should_handle_delete_result,
            {
                NodeName.HANDLE_ADDRESS_DELETE_SUCCESS: NodeName.HANDLE_ADDRESS_DELETE_SUCCESS,
                NodeName.HANDLE_ADDRESS_DELETE_FAILURE: NodeName.HANDLE_ADDRESS_DELETE_FAILURE
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_ADDRESS_DELETE_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_ADDRESS_DELETE_FAILURE, END)

        return graph.compile()
