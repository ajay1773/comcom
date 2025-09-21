from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.signup.subgraphs.generate_signup_form.nodes.send_signup_form import send_signup_form_node
from app.core.enums import NodeName
from app.graph.workflows.signup.types import GenerateSignupFormState

class GenerateSignupFormGraph:
    """Generate signin form workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[GenerateSignupFormState, None, GenerateSignupFormState, GenerateSignupFormState]:
        """Create the generate signin form subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(GenerateSignupFormState)

        # Add nodes
        graph.add_node(NodeName.SEND_SIGNUP_FORM, send_signup_form_node)

        # Set entry point
        graph.set_entry_point(NodeName.SEND_SIGNUP_FORM)

        # Add edges
        graph.add_edge(NodeName.SEND_SIGNUP_FORM, END)

        return graph.compile()
