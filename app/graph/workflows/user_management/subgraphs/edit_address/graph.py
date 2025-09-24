"""Edit address subgraph for updating user addresses in database."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.user_management.subgraphs.edit_address.nodes.extract_edit_details import extract_edit_details_node
from app.graph.workflows.user_management.subgraphs.edit_address.nodes.validate_address_ownership import validate_address_ownership_node
from app.graph.workflows.user_management.subgraphs.edit_address.nodes.update_address_details import update_address_details_node
from app.graph.workflows.user_management.subgraphs.edit_address.nodes.handle_address_edit_success import handle_address_edit_success_node
from app.graph.workflows.user_management.subgraphs.edit_address.nodes.handle_address_edit_failure import handle_address_edit_failure_node
from app.graph.workflows.user_management.types import EditAddressState


def should_proceed_to_validation(state: EditAddressState) -> str:
    """Determine if we should proceed to validation or handle failure."""
    if state.get("address_id") and state.get("extracted_address"):
        return NodeName.VALIDATE_ADDRESS_OWNERSHIP
    else:
        return NodeName.HANDLE_ADDRESS_EDIT_FAILURE


def should_proceed_to_update(state: EditAddressState) -> str:
    """Determine if we should proceed to update or handle failure."""
    if state.get("existing_address") and not state.get("error_message"):
        return NodeName.UPDATE_ADDRESS_DETAILS
    else:
        return NodeName.HANDLE_ADDRESS_EDIT_FAILURE


def should_handle_update_result(state: EditAddressState) -> str:
    """Determine if address update was successful or failed."""
    if state.get("address_edit_success", False):
        return NodeName.HANDLE_ADDRESS_EDIT_SUCCESS
    else:
        return NodeName.HANDLE_ADDRESS_EDIT_FAILURE


class EditAddressGraph:
    """Edit address workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[EditAddressState, None, EditAddressState, EditAddressState]:
        """Create the edit address subgraph."""

        # Use EditAddressState for the subgraph
        graph = StateGraph(EditAddressState)

        # Add all workflow nodes
        graph.add_node(NodeName.EXTRACT_EDIT_DETAILS, extract_edit_details_node)
        graph.add_node(NodeName.VALIDATE_ADDRESS_OWNERSHIP, validate_address_ownership_node)
        graph.add_node(NodeName.UPDATE_ADDRESS_DETAILS, update_address_details_node)
        graph.add_node(NodeName.HANDLE_ADDRESS_EDIT_SUCCESS, handle_address_edit_success_node)
        graph.add_node(NodeName.HANDLE_ADDRESS_EDIT_FAILURE, handle_address_edit_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_EDIT_DETAILS)

        # Conditional edge from extract to validation or failure
        graph.add_conditional_edges(
            NodeName.EXTRACT_EDIT_DETAILS,
            should_proceed_to_validation,
            {
                NodeName.VALIDATE_ADDRESS_OWNERSHIP: NodeName.VALIDATE_ADDRESS_OWNERSHIP,
                NodeName.HANDLE_ADDRESS_EDIT_FAILURE: NodeName.HANDLE_ADDRESS_EDIT_FAILURE
            }
        )

        # Conditional edge from validation to update or failure
        graph.add_conditional_edges(
            NodeName.VALIDATE_ADDRESS_OWNERSHIP,
            should_proceed_to_update,
            {
                NodeName.UPDATE_ADDRESS_DETAILS: NodeName.UPDATE_ADDRESS_DETAILS,
                NodeName.HANDLE_ADDRESS_EDIT_FAILURE: NodeName.HANDLE_ADDRESS_EDIT_FAILURE
            }
        )

        # Conditional edges from update node based on success/failure
        graph.add_conditional_edges(
            NodeName.UPDATE_ADDRESS_DETAILS,
            should_handle_update_result,
            {
                NodeName.HANDLE_ADDRESS_EDIT_SUCCESS: NodeName.HANDLE_ADDRESS_EDIT_SUCCESS,
                NodeName.HANDLE_ADDRESS_EDIT_FAILURE: NodeName.HANDLE_ADDRESS_EDIT_FAILURE
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_ADDRESS_EDIT_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_ADDRESS_EDIT_FAILURE, END)

        return graph.compile()
