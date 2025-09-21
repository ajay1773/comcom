from typing import cast
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signup.types import SignupWithDetailsState, UserSignup


async def extract_signup_details_node(state: SignupWithDetailsState) -> SignupWithDetailsState:
    """Extract login credentials."""
    message = state.get("search_query", "")
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a signup details extractor. Extract the name, email, password, first name, last name and phone number from the user's message.",
        ),
        ("user", "{message}"),
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    response_dict  = cast(UserSignup, await llm.with_structured_output(UserSignup).ainvoke(prompt.invoke({"message": message})))
    
    state["details"] = {"email": response_dict.email, "password": response_dict.password, "first_name": response_dict.first_name, "last_name": response_dict.last_name, "phone": response_dict.phone}
    return state
