from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.models.chat import GlobalState
from app.graph.subgraphs.initiate_payment.nodes.generate_payment import generate_payment_node

class InitiatePaymentGraph:
    """Initiate payment workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[GlobalState, None, GlobalState, GlobalState]:
        """Create the initiate payment subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(GlobalState)

        # Add nodes
        graph.add_node("generate_payment", generate_payment_node)

        # Set entry point
        graph.set_entry_point("generate_payment")

        # Add edges
        graph.add_edge("generate_payment", END)

        return graph.compile()
