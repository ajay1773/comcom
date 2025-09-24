"""User addresses subgraph for fetching and displaying user saved addresses."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.user_management.subgraphs.user_addresses.nodes.get_user_addresses import get_user_addresses_node
from app.graph.workflows.user_management.subgraphs.user_addresses.nodes.handle_addresses_fetch_success import handle_addresses_fetch_success_node
from app.graph.workflows.user_management.subgraphs.user_addresses.nodes.handle_addresses_fetch_failure import handle_addresses_fetch_failure_node
from app.graph.workflows.user_management.types import UserAddressesState


def should_handle_addresses_result(state: UserAddressesState) -> str:
    """Check if the user addresses fetch operation was successful or failed."""
    addresses_fetch_success = state.get("addresses_fetch_success", False)
    error_message = state.get("error_message", None)

    if addresses_fetch_success and not error_message:
        return NodeName.HANDLE_ADDRESSES_FETCH_SUCCESS
    else:
        return NodeName.HANDLE_ADDRESSES_FETCH_FAILURE


class UserAddressesGraph:
    """User addresses workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[UserAddressesState, None, UserAddressesState, UserAddressesState]:
        """Create the user addresses subgraph."""

        # Use UserAddressesState for the subgraph
        graph = StateGraph(UserAddressesState)

        # Add workflow nodes
        graph.add_node(NodeName.GET_USER_ADDRESSES, get_user_addresses_node)
        graph.add_node(NodeName.HANDLE_ADDRESSES_FETCH_SUCCESS, handle_addresses_fetch_success_node)
        graph.add_node(NodeName.HANDLE_ADDRESSES_FETCH_FAILURE, handle_addresses_fetch_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.GET_USER_ADDRESSES)

        # Add conditional edges based on operation success/failure
        graph.add_conditional_edges(
            NodeName.GET_USER_ADDRESSES,
            should_handle_addresses_result,
            {
                NodeName.HANDLE_ADDRESSES_FETCH_SUCCESS: NodeName.HANDLE_ADDRESSES_FETCH_SUCCESS,
                NodeName.HANDLE_ADDRESSES_FETCH_FAILURE: NodeName.HANDLE_ADDRESSES_FETCH_FAILURE
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_ADDRESSES_FETCH_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_ADDRESSES_FETCH_FAILURE, END)

        return graph.compile()
