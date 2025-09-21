from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.signin.types import LoginWithCredentialsState
from app.graph.workflows.signin.subgraphs.login_with_credentials.nodes.extract_login_credentials import extract_login_credentials_node
from app.graph.workflows.signin.subgraphs.login_with_credentials.nodes.login_with_credentials import login_with_credentials_node
from app.graph.workflows.signin.subgraphs.login_with_credentials.nodes.should_handle_user_credentials import should_handle_user_credentials
from app.graph.workflows.signin.subgraphs.login_with_credentials.nodes.handle_no_user_exists import handle_no_user_exists
from app.core.enums import NodeName

class LoginWithCredentialsGraph:
    """Login with credentials workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[LoginWithCredentialsState, None, LoginWithCredentialsState, LoginWithCredentialsState]:
        """Create the login with credentials subgraph."""

        # Use LoginWithCredentialsState for proper typing
        graph = StateGraph(LoginWithCredentialsState)

        # Add nodes
        graph.add_node(NodeName.EXTRACT_LOGIN_CREDENTIALS, extract_login_credentials_node)
        graph.add_node(NodeName.LOGIN_WITH_CREDENTIALS, login_with_credentials_node)
        graph.add_node(NodeName.HANDLE_NO_USER_EXISTS, handle_no_user_exists)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_LOGIN_CREDENTIALS)

        # Add conditional routing after extracting credentials
        graph.add_conditional_edges(
            NodeName.EXTRACT_LOGIN_CREDENTIALS,
            should_handle_user_credentials,
            {
                "login_with_credentials": NodeName.LOGIN_WITH_CREDENTIALS,
                "fallback": NodeName.HANDLE_NO_USER_EXISTS
            }
        )

        # Both paths end the workflow
        graph.add_edge(NodeName.LOGIN_WITH_CREDENTIALS, END)
        graph.add_edge(NodeName.HANDLE_NO_USER_EXISTS, END)

        return graph.compile()
