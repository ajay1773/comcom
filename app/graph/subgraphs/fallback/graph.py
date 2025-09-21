from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.models.chat import GlobalState
from app.graph.subgraphs.fallback.nodes.handle_fallback import handle_fallback_node

class FallbackGraph:
    """Fallback workflow for handling smalltalk, FAQ, and unknown intents."""

    @staticmethod
    def create() -> CompiledStateGraph[GlobalState, None, GlobalState, GlobalState]:
        """Create the fallback subgraph."""

        # Use GlobalState since we want shared state with parent
        graph = StateGraph(GlobalState)

        # Add nodes
        graph.add_node("handle_fallback", handle_fallback_node)

        # Set entry point
        graph.set_entry_point("handle_fallback")

        # Add edges
        graph.add_edge("handle_fallback", END)

        return graph.compile()
