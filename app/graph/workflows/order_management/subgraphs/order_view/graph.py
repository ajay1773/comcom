from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.order_management.types import OrderViewState

# Import nodes
from app.graph.workflows.order_management.subgraphs.order_view.nodes.extract_view_params import extract_view_params_node
from app.graph.workflows.order_management.subgraphs.order_view.nodes.fetch_orders import fetch_orders_node
from app.graph.workflows.order_management.subgraphs.order_view.nodes.format_order_response import format_order_response_node
from app.graph.workflows.order_management.subgraphs.order_view.nodes.order_view_failure_handler import order_view_failure_handler_node


def route_after_fetch(state: OrderViewState) -> str:
    """Route after fetching orders based on success/failure."""
    
    if state.get("error_message"):
        return "handle_failure"
    elif state.get("view_success"):
        return "format_response"
    else:
        return "handle_failure"


class OrderViewGraph:
    """Order view workflow graph."""

    @staticmethod
    def create() -> CompiledStateGraph[OrderViewState, None, OrderViewState, OrderViewState]:
        """Create the order view workflow graph."""
        
        # Create the state graph
        graph = StateGraph(OrderViewState)
        
        # Add nodes to the graph
        graph.add_node("extract_params", extract_view_params_node)
        graph.add_node("fetch_orders", fetch_orders_node)
        graph.add_node("format_response", format_order_response_node)
        graph.add_node("handle_failure", order_view_failure_handler_node)
        
        # Set entry point
        graph.set_entry_point("extract_params")
        
        # Add edges
        graph.add_edge("extract_params", "fetch_orders")
        
        # Conditional routing after fetch
        graph.add_conditional_edges(
            "fetch_orders",
            route_after_fetch,
            {
                "format_response": "format_response",
                "handle_failure": "handle_failure"
            }
        )
        
        # Both format_response and handle_failure end the workflow
        graph.add_edge("format_response", END)
        graph.add_edge("handle_failure", END)
        
        return graph.compile()
