from typing import cast
from app.graph.workflows.signup.types import SignupWithDetailsState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig
from app.graph.workflows.signup.subgraphs.signup_with_details.graph import SignupWithDetailsGraph
from app.services.widget_events import widget_event_emitter, WidgetEventType

async def run_signup_with_details(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    # 1. get or init
    sub_state = cast(SignupWithDetailsState, state.get("signup_with_details") or {
        "search_query": state.get('user_message',''),
        "suggestions": [],
    })
    
    # 2. Always update search_query with current user_message
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["suggestions"] = state.get("suggestions", [])

    # 3. run the subgraph
    subgraph = SignupWithDetailsGraph.create()
    updated_sub_state = cast(SignupWithDetailsState, await subgraph.ainvoke(sub_state))
    # 4. merge back into global
    state["signup_with_details"] = updated_sub_state    
    # Text response will be automatically extracted by output_handler_node
    return state