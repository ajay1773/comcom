"""Runner function for product bundle search workflow."""

from typing import cast
from app.graph.workflows.product_bundle_search.graph import ProductBundleSearchGraph
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_product_bundle_search(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Runner function for product bundle search workflow."""
    
    # 1. Get or initialize sub-state
    sub_state = cast(ProductBundleSearchState, state.get("product_bundle_search") or {
        "bundle_query": state.get("user_message", ""),
        "identified_bundle_items": None,
        "bundle_results_payload": None,
    })

    # 2. Update sub-state with current context from global state
    sub_state["conversation_history"] = state.get("conversation_history", [])
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["bundle_query"] = state.get("user_message", "")

    # 3. Run the subgraph
    subgraph = ProductBundleSearchGraph.create()
    updated_sub_state = cast(ProductBundleSearchState, await subgraph.ainvoke(sub_state, config=config))

    # 4. Merge back into global state
    state["product_bundle_search"] = updated_sub_state
    # Workflow output will be automatically extracted by output_handler_node

    return state

