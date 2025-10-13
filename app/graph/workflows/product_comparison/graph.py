"""Product comparison workflow graph definition."""

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.product_comparison.types import ProductComparisonState
from app.graph.workflows.product_comparison.nodes.extract_comparison_request import extract_comparison_request_node
from app.graph.workflows.product_comparison.nodes.fetch_product_details import fetch_product_details_node
from app.graph.workflows.product_comparison.nodes.handle_edge_cases import handle_edge_cases_node
from app.graph.workflows.product_comparison.nodes.generate_comparison_analysis import generate_comparison_analysis_node
from app.graph.workflows.product_comparison.nodes.format_comparison_output import format_comparison_output_node


class ProductComparisonGraph:
    """Product comparison workflow graph."""

    @staticmethod
    def create() -> CompiledStateGraph[ProductComparisonState, None, ProductComparisonState, ProductComparisonState]:
        """Create the product comparison workflow graph."""
        workflow = StateGraph(ProductComparisonState)

        # Add nodes
        workflow.add_node("extract_request", extract_comparison_request_node)
        workflow.add_node("fetch_products", fetch_product_details_node)
        workflow.add_node("handle_edge_cases", handle_edge_cases_node)
        workflow.add_node("generate_analysis", generate_comparison_analysis_node)
        workflow.add_node("format_output", format_comparison_output_node)

        # Define edges
        workflow.set_entry_point("extract_request")
        workflow.add_edge("extract_request", "fetch_products")
        workflow.add_edge("fetch_products", "handle_edge_cases")

        # Conditional routing based on whether we have valid products for comparison
        workflow.add_conditional_edges(
            "handle_edge_cases",
            ProductComparisonGraph.should_proceed_to_analysis,
            {
                "generate_analysis": "generate_analysis",
                "end": END
            }
        )

        workflow.add_edge("generate_analysis", "format_output")
        workflow.add_edge("format_output", END)

        return workflow.compile()
    
    @staticmethod
    def should_proceed_to_analysis(state: ProductComparisonState) -> str:
        """Route based on whether we have valid products to compare."""
        edge_case_handled = state.get("edge_case_handled", False)
        category_mismatch_handled = state.get("category_mismatch_handled", False)
        products = state.get("products", [])
    
        # If edge case was handled (no products, single product, etc.), end workflow
        if edge_case_handled:
            return "end"
        
        # If category mismatch was handled, still proceed with comparison
        # (user can decide whether to continue or not based on the warning)
        if category_mismatch_handled and len(products) >= 2:
            return "generate_analysis"
        
        # If we have 2+ products and no edge cases, proceed to analysis
        if len(products) >= 2:
            return "generate_analysis"
        
        # Fallback to end
        return "end"


