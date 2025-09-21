from typing import cast
from app.graph.workflows.product_search.graph import ProductSearchGraph
from app.graph.workflows.product_search.types import ProductSearchState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig


async def run_product_search(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    # 1. get or init
    sub_state = cast(ProductSearchState, state.get("product_search") or {
        "search_query": "",
        "search_parameters": {},
        "search_results": [],
        "suggestions": [],
        "result_count": 0,
        "workflow_widget_json": None,
    })
    
    # 2. Always update search_query with current user_message
    sub_state["search_query"] = state.get("user_message", "")

    # 3. run the subgraph
    subgraph = ProductSearchGraph.create()
    updated_sub_state = cast(ProductSearchState, await subgraph.ainvoke(sub_state))
    # 4. merge back into global
    state["product_search"] = updated_sub_state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", None)
    return state