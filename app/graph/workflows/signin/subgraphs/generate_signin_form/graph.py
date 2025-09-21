from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.signin.subgraphs.generate_signin_form.nodes.send_login_form import send_login_form_node
from app.core.enums import NodeName
from app.graph.workflows.signin.types import GenerateSigninFormState

class GenerateSigninFormGraph:
    """Generate signin form workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[GenerateSigninFormState, None, GenerateSigninFormState, GenerateSigninFormState]:
        """Create the generate signin form subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(GenerateSigninFormState)

        # Add nodes
        graph.add_node(NodeName.SEND_LOGIN_FORM, send_login_form_node)

        # Set entry point
        graph.set_entry_point(NodeName.SEND_LOGIN_FORM)

        # Add edges
        graph.add_edge(NodeName.SEND_LOGIN_FORM, END)

        return graph.compile()
