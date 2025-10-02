from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.order_management.types import CheckoutState

# Import new subgraph runners
from app.graph.workflows.order_management.subgraphs.checkout_ui_provider.nodes.runner import run_checkout_ui_provider
from app.graph.workflows.order_management.subgraphs.checkout_processor.nodes.runner import run_checkout_processor
from app.graph.workflows.order_management.subgraphs.checkout.nodes.checkout_router import checkout_router_node


def route_checkout_request(state: CheckoutState) -> str:
    """Route checkout request to appropriate subgraph."""
    
    checkout_route = state.get("checkout_route", "ui_data")
    
    if checkout_route == "process_submission":
        return "process_submission"
    else:
        return "ui_data"

class CheckoutGraph:
    """Checkout workflow as a router to subgraphs."""

    @staticmethod
    def create() -> CompiledStateGraph[CheckoutState, None, CheckoutState, CheckoutState]:
        """Create the checkout workflow graph that routes to appropriate subgraphs."""
        
        # Create the state graph
        graph = StateGraph(CheckoutState)
        
        # Add nodes to the graph
        graph.add_node("checkout_router", checkout_router_node)
        graph.add_node("ui_data_provider", run_checkout_ui_provider)
        graph.add_node("submission_processor", run_checkout_processor)
        
        # Set entry point
        graph.set_entry_point("checkout_router")
        
        # Route from router to appropriate subgraph
        graph.add_conditional_edges(
            "checkout_router",
            route_checkout_request,
            {
                "ui_data": "ui_data_provider",
                "process_submission": "submission_processor"
            }
        )
        
        # Both subgraphs end the workflow
        graph.add_edge("ui_data_provider", END)
        graph.add_edge("submission_processor", END)
        
        return graph.compile()
        



