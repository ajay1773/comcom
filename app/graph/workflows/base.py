
from app.core.config import settings
from app.models.chat import GlobalState
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.graph.nodes.orchestrator import orchestrator_node
from app.graph.nodes.classifier import classifier_node
from app.graph.nodes.output_handler import output_handler_node
from app.graph.nodes.error_handler import error_handler_node
from app.graph.subgraphs.place_order.graph import PlaceOrderGraph
from app.graph.subgraphs.initiate_payment.graph import InitiatePaymentGraph
from app.graph.subgraphs.payment_status.graph import PaymentStatusGraph
from app.graph.subgraphs.fallback.graph import FallbackGraph
from app.graph.workflows.signin.subgraphs.generate_signin_form.nodes.runner import run_generate_signin_form
from app.core.enums import WorkflowType, NodeName, WorkflowStateKey
from app.graph.workflows.product_search.nodes.runner import run_product_search
import aiosqlite

from app.graph.workflows.signup.subgraphs.generate_signup_form.nodes.runner import run_generate_signup_form
from app.graph.workflows.signup.subgraphs.signup_with_details.nodes.runner import run_signup_with_details
from app.graph.workflows.signin.subgraphs.login_with_credentials.nodes.runner import run_login_with_credentials
from app.graph.workflows.auth_middleware.nodes.runner import run_auth_middleware
from app.graph.workflows.order_management.subgraphs.add_to_cart.nodes.runner import run_add_to_cart



def get_next_workflow(state: GlobalState) -> str:
    """
    Determine the next workflow based on orchestrator's decision.
    This function extracts the workflow type from the state.
    """
    return state[WorkflowStateKey.CURRENT_WORKFLOW.value]


def should_handle_error(state: GlobalState) -> str:
    """
    Check if there's a workflow error that needs to be handled.
    Routes to error_handler if an error exists, otherwise continues to output_handler.
    """
    if state.get(WorkflowStateKey.WORKFLOW_ERROR.value):
        return NodeName.ERROR_HANDLER
    return NodeName.OUTPUT_HANDLER


async def run_auth_protected_product_search(state: GlobalState, config=None) -> GlobalState:
    """Run product search with auth middleware protection."""
    # First run auth middleware
    auth_state = await run_auth_middleware(state, WorkflowType.PRODUCT_SEARCH, config)
    
    # If auth failed, return early with auth error
    if not auth_state.get("is_authenticated", False):
        return auth_state
    
    # If auth passed, run the actual product search workflow
    return await run_product_search(auth_state, config)

async def run_auth_protected_add_to_cart(state: GlobalState, config=None) -> GlobalState:
    """Run product search with auth middleware protection."""
    # First run auth middleware
    auth_state = await run_auth_middleware(state, WorkflowType.ADD_TO_CART, config)
    
    # If auth failed, return early with auth error
    if not auth_state.get("is_authenticated", False):
        return auth_state
    
    # If auth passed, run the actual product search workflow
    return await run_add_to_cart(auth_state, config)


async def run_auth_protected_place_order(state: GlobalState, config=None) -> GlobalState:
    """Run place order with auth middleware protection."""
    from typing import cast
    from app.graph.subgraphs.place_order.graph import PlaceOrderGraph
    
    # First run auth middleware
    auth_state = await run_auth_middleware(state, WorkflowType.PLACE_ORDER, config)
    
    # If auth failed, return early with auth error
    if not auth_state.get("is_authenticated", False):
        return auth_state
    
    # If auth passed, run the actual place order workflow
    place_order_graph = PlaceOrderGraph.create()
    result = await place_order_graph.ainvoke(auth_state, config)
    return cast(GlobalState, result)


async def create_base_graph():
    """Create and configure the LangGraph workflow."""

    conn = await aiosqlite.connect(settings.DATABASE_URL)
    memory = AsyncSqliteSaver(conn)
    # Create the graph
    graph = StateGraph(GlobalState)

    # Add core nodes
    graph.add_node(NodeName.ORCHESTRATOR_NODE, orchestrator_node)
    graph.add_node(NodeName.CLASSIFIER_NODE, classifier_node)
    graph.add_node(NodeName.OUTPUT_HANDLER, output_handler_node)
    graph.add_node(NodeName.ERROR_HANDLER, error_handler_node)
    graph.set_entry_point(NodeName.CLASSIFIER_NODE)
    graph.add_edge(NodeName.CLASSIFIER_NODE, NodeName.ORCHESTRATOR_NODE)

    # Create subgraphs (they're already compiled in their create() method)
    place_order_graph = PlaceOrderGraph.create()
    initiate_payment_graph = InitiatePaymentGraph.create()
    payment_status_graph = PaymentStatusGraph.create()
    fallback_graph = FallbackGraph.create()

    # Add compiled subgraphs as nodes
    # Regular workflows (no auth required)
    graph.add_node(NodeName.PRODUCT_SEARCH_WORKFLOW, run_product_search)
    graph.add_node(NodeName.GENERATE_SIGNUP_FORM_WORKFLOW, run_generate_signup_form)
    graph.add_node(NodeName.SIGNUP_WITH_DETAILS_WORKFLOW, run_signup_with_details)
    graph.add_node(NodeName.PLACE_ORDER_WORKFLOW, place_order_graph)
    graph.add_node(NodeName.INITIATE_PAYMENT_WORKFLOW, initiate_payment_graph)
    graph.add_node(NodeName.PAYMENT_STATUS_WORKFLOW, payment_status_graph)
    graph.add_node(NodeName.FALLBACK_WORKFLOW, fallback_graph)
    graph.add_node(NodeName.GENERATE_SIGNIN_FORM_WORKFLOW, run_generate_signin_form)
    graph.add_node(NodeName.LOGIN_WITH_CREDENTIALS_WORKFLOW, run_login_with_credentials)
    
    # Auth-protected workflows
    graph.add_node(NodeName.AUTH_PROTECTED_PLACE_ORDER_WORKFLOW, run_auth_protected_place_order)
    graph.add_node(NodeName.AUTH_PROTECTED_ADD_TO_CART_WORKFLOW, run_auth_protected_add_to_cart)
    # Route to different workflows based on orchestrator's decision
    graph.add_conditional_edges(
        NodeName.ORCHESTRATOR_NODE,
        get_next_workflow,
        {
            # Protected workflows (require authentication)
            WorkflowType.PRODUCT_SEARCH: NodeName.PRODUCT_SEARCH_WORKFLOW,
            WorkflowType.PLACE_ORDER: NodeName.AUTH_PROTECTED_PLACE_ORDER_WORKFLOW,
            WorkflowType.ADD_TO_CART: NodeName.AUTH_PROTECTED_ADD_TO_CART_WORKFLOW,
            # Auth-protected payment workflows
            WorkflowType.INITIATE_PAYMENT: NodeName.INITIATE_PAYMENT_WORKFLOW,
            WorkflowType.PAYMENT_STATUS: NodeName.PAYMENT_STATUS_WORKFLOW,
            # Public workflows (no auth required)
            WorkflowType.SUPPORT_QUERY: NodeName.FALLBACK_WORKFLOW,
            WorkflowType.FALLBACK: NodeName.FALLBACK_WORKFLOW,
            WorkflowType.GENERATE_SIGNIN_FORM: NodeName.GENERATE_SIGNIN_FORM_WORKFLOW,
            WorkflowType.LOGIN_WITH_CREDENTIALS: NodeName.LOGIN_WITH_CREDENTIALS_WORKFLOW,
            WorkflowType.GENERATE_SIGNUP_FORM: NodeName.GENERATE_SIGNUP_FORM_WORKFLOW,
            WorkflowType.SIGNUP_WITH_DETAILS: NodeName.SIGNUP_WITH_DETAILS_WORKFLOW,
        }
    )

    # Add conditional edges from workflows to check for errors
    # Auth-protected workflows error handling
    # graph.add_conditional_edges(
    #     NodeName.PRODUCT_SEARCH_WORKFLOW,
    #     should_handle_error,
    #     {
    #         NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
    #         NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
    #     }
    # )
    # graph.add_conditional_edges(
    #     NodeName.AUTH_PROTECTED_PLACE_ORDER_WORKFLOW,
    #     should_handle_error,
    #     {
    #         NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
    #         NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
    #     }
    # )
    # graph.add_conditional_edges(
    #     NodeName.ADD_TO_CART_WORKFLOW,
    #     should_handle_error,
    #     {
    #         NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
    #         NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
    #     }
    # )
    graph.add_conditional_edges(
        NodeName.PLACE_ORDER_WORKFLOW,
        should_handle_error,
        {
            NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
            NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
        }
    )
    graph.add_conditional_edges(
        NodeName.INITIATE_PAYMENT_WORKFLOW,
        should_handle_error,
        {
            NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
            NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
        }
    )
    graph.add_conditional_edges(
        NodeName.PAYMENT_STATUS_WORKFLOW,
        should_handle_error,
        {
            NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
            NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
        }
    )
    graph.add_conditional_edges(
        NodeName.FALLBACK_WORKFLOW,
        should_handle_error,
        {
            NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
            NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
        }
    )
    # graph.add_conditional_edges(
    #     NodeName.GENERATE_SIGNIN_FORM_WORKFLOW,
    #     should_handle_error,
    #     {
    #         NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
    #         NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
    #     }
    # )
    # graph.add_conditional_edges(
    #     NodeName.LOGIN_WITH_CREDENTIALS_WORKFLOW,
    #     should_handle_error,
    #     {
    #         NodeName.ERROR_HANDLER: NodeName.ERROR_HANDLER,
    #         NodeName.OUTPUT_HANDLER: NodeName.OUTPUT_HANDLER
    #     }
    # )
    # Error handler routes back to output handler after processing
    graph.add_edge(NodeName.ERROR_HANDLER, NodeName.OUTPUT_HANDLER)

    # Output handler is the final node
    graph.add_edge(NodeName.OUTPUT_HANDLER, END)
    compiled_graph = graph.compile(checkpointer=memory)

    # Graph is already compiled with memory for state persistence
    return compiled_graph, memory
