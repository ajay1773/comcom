from typing import cast
from app.models.user import UserLogin
from app.services.llm import llm_service
from app.services.db.user import user_service
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signin.types import LoginWithCredentialsState


async def extract_login_credentials_node(state: LoginWithCredentialsState) -> LoginWithCredentialsState:
    """Extract login credentials and lookup user."""
    message = state.get("search_query", "")
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a login credentials extractor. Extract the email and password from the user's message.",
        ),
        ("user", "{message}"),
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    response_dict  = cast(UserLogin, await llm.with_structured_output(UserLogin).ainvoke(prompt.invoke({"message": message})))
    
    state["credentials"] = {"email": response_dict.email, "password": response_dict.password}
    
    # Look up user by email and store in state
    if response_dict.email:
        user = await user_service.get_user_by_email(response_dict.email)
        state["user"] = user
    else:
        state["user"] = None
    
    return state
