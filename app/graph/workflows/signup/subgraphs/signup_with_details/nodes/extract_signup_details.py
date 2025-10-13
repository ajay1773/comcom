from typing import cast
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signup.types import SignupWithDetailsState, UserSignup
from app.utils.conversation_context import format_conversation_context_with_template


async def extract_signup_details_node(state: SignupWithDetailsState) -> SignupWithDetailsState:
    """Extract login credentials."""
    message = state.get("search_query", "")
    
    # Get conversation context for better signup detail extraction
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="general",
        limit=5,
        fallback_message=""
    )
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a signup details extractor. Extract the name, email, password, first name, last name and phone number from the user's message.",
        ),
        ("user", "{message}"),
        ("user", "{conversation_context}"),
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    response_dict  = cast(UserSignup, await llm.with_structured_output(UserSignup).ainvoke(prompt.invoke({"message": message, "conversation_context": conversation_context})))
    
    state["details"] = {"email": response_dict.email, "password": response_dict.password, "first_name": response_dict.first_name, "last_name": response_dict.last_name, "phone": response_dict.phone}
    return state
