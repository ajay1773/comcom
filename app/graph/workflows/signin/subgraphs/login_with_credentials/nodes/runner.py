from typing import cast
from app.graph.workflows.signin.types import LoginWithCredentialsState
from app.models.chat import GlobalState
from langchain_core.runnables import RunnableConfig
from app.graph.workflows.signin.subgraphs.login_with_credentials.graph import LoginWithCredentialsGraph

async def run_login_with_credentials(state: GlobalState, config: RunnableConfig | None = None) -> GlobalState:
    """Run the login with credentials subgraph."""
    
    # 1. Get or initialize the login sub-state
    sub_state = cast(LoginWithCredentialsState, state.get("login_with_credentials") or {
        "search_query": state.get('user_message', ''),
        "suggestions": [],
        "workflow_widget_json": {},
        "credentials": {},
        "user": None
    })
    
    # 2. Always update search_query with current user_message
    sub_state["search_query"] = state.get("user_message", "")
    sub_state["suggestions"] = state.get("suggestions", [])

    # 3. Run the subgraph
    subgraph = LoginWithCredentialsGraph.create()
    updated_sub_state = cast(LoginWithCredentialsState, await subgraph.ainvoke(sub_state))
    
    # 4. Merge back into global state
    state["login_with_credentials"] = updated_sub_state
    state["workflow_widget_json"] = updated_sub_state.get("workflow_widget_json", {})
    
    # 5. Update authentication state if login was successful
    if updated_sub_state.get("is_authenticated"):
        state["is_authenticated"] = True
        state["user_id"] = updated_sub_state.get("user_id")
    
    return state
