from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.signup.types import SignupWithDetailsState
from app.graph.workflows.signup.subgraphs.signup_with_details.nodes.extract_signup_details import extract_signup_details_node
from app.graph.workflows.signup.subgraphs.signup_with_details.nodes.save_user_details import save_user_details_node
from app.core.enums import NodeName

class SignupWithDetailsGraph:
    """Signup with details workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[SignupWithDetailsState, None, SignupWithDetailsState, SignupWithDetailsState]:
        """Create the signup with details subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(SignupWithDetailsState)

        # Add nodes
        graph.add_node(NodeName.EXTRACT_SIGNUP_DETAILS, extract_signup_details_node)
        graph.add_node(NodeName.SAVE_USER_DETAILS, save_user_details_node)

        # Set entry point
        graph.set_entry_point(NodeName.EXTRACT_SIGNUP_DETAILS)

        # Add edges
        graph.add_edge(NodeName.EXTRACT_SIGNUP_DETAILS, NodeName.SAVE_USER_DETAILS)
        graph.add_edge(NodeName.SAVE_USER_DETAILS, END)

        return graph.compile()
