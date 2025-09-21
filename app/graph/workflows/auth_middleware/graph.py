from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.auth_middleware.types import AuthMiddlewareState
from app.graph.workflows.auth_middleware.nodes.parse_token import parse_token_node
from app.graph.workflows.auth_middleware.nodes.handle_valid_token import handle_valid_token_node
from app.graph.workflows.auth_middleware.nodes.handle_invalid_token import handle_invalid_token_node
from app.graph.workflows.auth_middleware.nodes.should_token_validate import should_token_validate


class AuthMiddlewareGraph:
    """Authentication middleware workflow as a subgraph."""

    @staticmethod
    def create() -> CompiledStateGraph[AuthMiddlewareState, None, AuthMiddlewareState, AuthMiddlewareState]:
        """Create the auth middleware subgraph."""

        # Use AuthMiddlewareState for proper typing
        graph = StateGraph(AuthMiddlewareState)

        # Add nodes
        graph.add_node("parse_token", parse_token_node)
        graph.add_node("handle_valid_token", handle_valid_token_node)
        graph.add_node("handle_invalid_token", handle_invalid_token_node)

        # Set entry point
        graph.set_entry_point("parse_token")

        # Add conditional routing after parsing token
        graph.add_conditional_edges(
            "parse_token",
            should_token_validate,
            {
                "handle_valid_token": "handle_valid_token",
                "handle_invalid_token": "handle_invalid_token"
            }
        )

        # Both paths end the workflow
        graph.add_edge("handle_valid_token", END)
        graph.add_edge("handle_invalid_token", END)

        return graph.compile()
