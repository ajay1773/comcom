from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.order_management.types import CheckoutUIProviderState
from app.core.enums import NodeName

# Import checkout UI provider nodes
from app.graph.workflows.order_management.subgraphs.checkout_ui_provider.nodes.extract_checkout_details import extract_checkout_details_node
from app.graph.workflows.order_management.subgraphs.checkout_ui_provider.nodes.prepare_ui_data import prepare_ui_data_node
from app.graph.workflows.order_management.subgraphs.checkout_ui_provider.nodes.ui_success_handler import ui_success_handler_node
from app.graph.workflows.order_management.subgraphs.checkout_ui_provider.nodes.ui_failure_handler import ui_failure_handler_node


def should_continue_ui_preparation(state: CheckoutUIProviderState) -> str:
    """Determine if UI preparation should continue or handle failure."""
    
    # Check if there's an error or UI data preparation failed
    if state.get("error_message") or state.get("ui_data_success") is False:
        return "failure"
    
    return "continue"


class CheckoutUIProviderGraph:
    """Checkout UI data provider workflow as a subgraph."""
    
    @staticmethod
    def create() -> CompiledStateGraph[CheckoutUIProviderState, None, CheckoutUIProviderState, CheckoutUIProviderState]:
        """Create the checkout UI provider workflow graph."""
        
        # Create the state graph
        graph = StateGraph(CheckoutUIProviderState)
        
        # Add nodes to the graph
        graph.add_node("extract_checkout_details", extract_checkout_details_node)
        graph.add_node("prepare_ui_data", prepare_ui_data_node)
        graph.add_node("ui_success_handler", ui_success_handler_node)
        graph.add_node("ui_failure_handler", ui_failure_handler_node)
        
        # Set entry point
        graph.set_entry_point("extract_checkout_details")
        
        # Add edges with conditional routing based on success/failure
        
        # From extract_checkout_details to prepare_ui_data or failure
        graph.add_conditional_edges(
            "extract_checkout_details",
            should_continue_ui_preparation,
            {
                "continue": "prepare_ui_data",
                "failure": "ui_failure_handler"
            }
        )
        
        # From prepare_ui_data to success or failure handler
        graph.add_conditional_edges(
            "prepare_ui_data",
            should_continue_ui_preparation,
            {
                "continue": "ui_success_handler",
                "failure": "ui_failure_handler"
            }
        )
        
        # Both success and failure handlers end the workflow
        graph.add_edge("ui_success_handler", END)
        graph.add_edge("ui_failure_handler", END)
        
        return graph.compile()
