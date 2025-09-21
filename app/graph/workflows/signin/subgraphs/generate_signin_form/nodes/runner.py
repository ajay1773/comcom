from typing import cast
from app.graph.workflows.signin.subgraphs.generate_signin_form.graph import GenerateSigninFormGraph
from app.models.chat import GlobalState
from app.graph.workflows.signin.types import GenerateSigninFormState
from langchain_core.runnables import RunnableConfig



async def run_generate_signin_form(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    # 1. get or init
    sub_state = cast(GenerateSigninFormState, state.get("generate_signin_form") or {
        "search_query": state.get('user_message',''),
        "suggestions": [],
        "workflow_widget_json": None,
    })
    
    # 2. Always update search_query with current user_message
    sub_state["suggestions"] = state.get("suggestions", [])

    # 3. run the subgraph
    subgraph = GenerateSigninFormGraph.create()
    updated_sub_state = cast(GenerateSigninFormState, await subgraph.ainvoke(sub_state))
    # 4. merge back into global
    state["generate_signin_form"] = updated_sub_state
    state["workflow_widget_json"] = {
        "template": "send_login_form",
        "payload": updated_sub_state.get("suggestions", []),
    }
    return state