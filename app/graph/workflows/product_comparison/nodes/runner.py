"""Runner for product comparison workflow."""

from typing import cast
from app.graph.workflows.product_comparison.graph import ProductComparisonGraph
from app.graph.workflows.product_comparison.types import ProductComparisonState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_product_comparison(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Run the product comparison workflow."""
    
    # 1. Get or initialize sub-state
    sub_state = cast(ProductComparisonState, state.get("product_comparison") or {
        "search_query": "",
        "user_message": "",
        "conversation_history": [],
        "product_identifiers": [],
        "comparison_criteria": [],
        "user_context": "",
        "products": [],
        "comparison_analysis": {},
        "comparison_table": {},
        "recommendation": "",
        "workflow_output_text": "",
        "workflow_output_json": {},
        "result_count": 0,
        "error_message": ""
    })
    
    # 2. Always update with current context from GlobalState
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["conversation_history"] = state.get("conversation_history", [])
    sub_state["thread_id"] = state.get("thread_id", None)
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)
    
    # 3. Run the workflow
    subgraph = ProductComparisonGraph.create()
    updated_sub_state = cast(ProductComparisonState, await subgraph.ainvoke(sub_state, config))
    
    # 4. Merge back into global state
    state["product_comparison"] = updated_sub_state
    
    # 5. Set workflow outputs for output_handler
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", "")
    state["workflow_output_json"] = updated_sub_state.get("workflow_output_json", {})
    
    return state

