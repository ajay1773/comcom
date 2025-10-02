from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.order_management.types import CheckoutProcessorState

# Import checkout processor nodes
from app.graph.workflows.order_management.subgraphs.checkout_processor.nodes.extract_submission_details import extract_submission_details_node
from app.graph.workflows.order_management.subgraphs.checkout_processor.nodes.validate_submission import validate_submission_node
from app.graph.workflows.order_management.subgraphs.checkout_processor.nodes.process_payment import process_payment_node
from app.graph.workflows.order_management.subgraphs.checkout_processor.nodes.create_order import create_order_node
from app.graph.workflows.order_management.subgraphs.checkout_processor.nodes.processor_success_handler import processor_success_handler_node
from app.graph.workflows.order_management.subgraphs.checkout_processor.nodes.processor_failure_handler import processor_failure_handler_node


def should_continue_processing(state: CheckoutProcessorState) -> str:
    """Determine if processing should continue or handle failure."""
    
    # Check if there's an error or checkout processing failed
    if state.get("error_message") or state.get("checkout_success") is False:
        return "failure"
    
    return "continue"


class CheckoutProcessorGraph:
    """Checkout processor workflow as a subgraph."""
    
    @staticmethod
    def create() -> CompiledStateGraph[CheckoutProcessorState, None, CheckoutProcessorState, CheckoutProcessorState]:
        """Create the checkout processor workflow graph."""
        
        # Create the state graph
        graph = StateGraph(CheckoutProcessorState)
        
        # Add nodes to the graph
        graph.add_node("extract_submission_details", extract_submission_details_node)
        graph.add_node("validate_submission", validate_submission_node)
        graph.add_node("process_payment", process_payment_node)
        graph.add_node("create_order", create_order_node)
        graph.add_node("processor_success_handler", processor_success_handler_node)
        graph.add_node("processor_failure_handler", processor_failure_handler_node)
        
        # Set entry point
        graph.set_entry_point("extract_submission_details")
        
        # Add edges with conditional routing based on success/failure
        
        # From extract_submission_details to validate_submission or failure
        graph.add_conditional_edges(
            "extract_submission_details",
            should_continue_processing,
            {
                "continue": "validate_submission",
                "failure": "processor_failure_handler"
            }
        )
        
        # From validate_submission to process_payment or failure
        graph.add_conditional_edges(
            "validate_submission",
            should_continue_processing,
            {
                "continue": "process_payment",
                "failure": "processor_failure_handler"
            }
        )
        
        # From process_payment to create_order or failure
        graph.add_conditional_edges(
            "process_payment",
            should_continue_processing,
            {
                "continue": "create_order",
                "failure": "processor_failure_handler"
            }
        )
        
        # From create_order to success or failure handler
        graph.add_conditional_edges(
            "create_order",
            should_continue_processing,
            {
                "continue": "processor_success_handler",
                "failure": "processor_failure_handler"
            }
        )
        
        # Both success and failure handlers end the workflow
        graph.add_edge("processor_success_handler", END)
        graph.add_edge("processor_failure_handler", END)
        
        return graph.compile()
