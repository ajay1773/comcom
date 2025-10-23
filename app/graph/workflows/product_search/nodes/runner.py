from typing import cast
from app.graph.workflows.product_search.graph import ProductSearchGraph
from app.graph.workflows.product_search.types import ProductSearchState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig

from app.services.widget_events import WidgetEventType, widget_event_emitter


async def run_product_search(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    # 1. get or init
    sub_state = cast(ProductSearchState, state.get("product_search") or {
        "search_query": "",
        "search_parameters": {},
        "search_results": [],
        "suggestions": [],
        "result_count": 0,
        "thread_id": None,
        "conversation_history": [],
        "user_id": None,
        "session_token": None,
        "is_authenticated": False,
        "auth_required": False,
    })
    
    # 2. Always update with current context from GlobalState
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["conversation_history"] = state.get("conversation_history", [])
    sub_state["thread_id"] = state.get("thread_id", None)
    sub_state["user_id"] = state.get("user_id", None)
    sub_state["session_token"] = state.get("session_token", None)
    sub_state["is_authenticated"] = state.get("is_authenticated", False)
    sub_state["auth_required"] = state.get("auth_required", False)

    # 3. run the subgraph
    subgraph = ProductSearchGraph.create()
    updated_sub_state = cast(ProductSearchState, await subgraph.ainvoke(sub_state))
    
    # 4. merge back into global
    state["product_search"] = updated_sub_state
    
    # 5. Set workflow outputs for output_handler
    state["workflow_output_text"] = updated_sub_state.get("workflow_output_text", "")
    state["workflow_output_json"] = updated_sub_state.get("workflow_output_json", {})
    
    # Emit product search results widget event
    widget_event_emitter.emit(
        WidgetEventType.PRODUCT_SEARCH_RESULTS,
        {
            "products": updated_sub_state.get("search_results", []),
            "search_parameters": updated_sub_state.get("search_parameters", {}),
            "result_count": updated_sub_state.get("result_count", 0),
            "success_message": updated_sub_state.get("suggestions", [''])[0]
        }
    )
    return state