"""User profile subgraph for fetching and displaying user profile details."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.core.enums import NodeName
from app.graph.workflows.user_management.subgraphs.user_profile.nodes.get_user_details import get_user_details_node
from app.graph.workflows.user_management.subgraphs.user_profile.nodes.handle_user_details_fetch_success import handle_user_details_fetch_success_node
from app.graph.workflows.user_management.subgraphs.user_profile.nodes.handle_user_details_fetch_failure import handle_user_details_fetch_failure_node
from app.graph.workflows.user_management.types import UserProfileState


def should_handle_profile_result(state: UserProfileState) -> str:
    """Check if the user profile fetch operation was successful or failed."""
    profile_fetch_success = state.get("profile_fetch_success", False)
    error_message = state.get("error_message", None)

    if profile_fetch_success and not error_message:
        return NodeName.HANDLE_USER_DETAILS_FETCH_SUCCESS
    else:
        return NodeName.HANDLE_USER_DETAILS_FETCH_FAILURE


class UserProfileGraph:
    """User profile workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[UserProfileState, None, UserProfileState, UserProfileState]:
        """Create the user profile subgraph."""

        # Use UserProfileState for the subgraph
        graph = StateGraph(UserProfileState)

        # Add workflow nodes
        graph.add_node(NodeName.GET_USER_DETAILS, get_user_details_node)
        graph.add_node(NodeName.HANDLE_USER_DETAILS_FETCH_SUCCESS, handle_user_details_fetch_success_node)
        graph.add_node(NodeName.HANDLE_USER_DETAILS_FETCH_FAILURE, handle_user_details_fetch_failure_node)

        # Set entry point
        graph.set_entry_point(NodeName.GET_USER_DETAILS)

        # Add conditional edges based on operation success/failure
        graph.add_conditional_edges(
            NodeName.GET_USER_DETAILS,
            should_handle_profile_result,
            {
                NodeName.HANDLE_USER_DETAILS_FETCH_SUCCESS: NodeName.HANDLE_USER_DETAILS_FETCH_SUCCESS,
                NodeName.HANDLE_USER_DETAILS_FETCH_FAILURE: NodeName.HANDLE_USER_DETAILS_FETCH_FAILURE
            }
        )

        # Both success and failure handlers end the workflow
        graph.add_edge(NodeName.HANDLE_USER_DETAILS_FETCH_SUCCESS, END)
        graph.add_edge(NodeName.HANDLE_USER_DETAILS_FETCH_FAILURE, END)

        return graph.compile()
