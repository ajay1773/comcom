from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.models.chat import GlobalState
from app.graph.subgraphs.payment_status.nodes.make_payment import make_payment_node

class PaymentStatusGraph:
    """Payment status workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[GlobalState, None, GlobalState, GlobalState]:
        """Create the payment status subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(GlobalState)

        # Add nodes
        graph.add_node("make_payment", make_payment_node)

        # Set entry point
        graph.set_entry_point("make_payment")

        # Add edges
        graph.add_edge("make_payment", END)

        return graph.compile()
