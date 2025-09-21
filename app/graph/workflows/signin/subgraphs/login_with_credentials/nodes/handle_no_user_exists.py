from typing import cast
from app.graph.workflows.signin.types import LoginWithCredentialsState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service

async def handle_no_user_exists(state: LoginWithCredentialsState) -> LoginWithCredentialsState:
    """Handle no user exists."""
    user_message = state.get("user_message", "")
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are part of a helpful chatbot assistant in an e-commerce system.
        You are supposed to handle the case where there is not any user when the given credentials are used to login.
        1. Politely informs the user that no user exists with the given credentials.
        2. Do not use technical words like "query", "results", or "response".
        3. Keeps the tone conversational and natural, as if chatting with a human.
        4. Suggest them to sign up for an account.
        5. Do not send the email or password in the message back to the user.
        6. Simply tell the user that no user exists with the given credentials and suggest them to sign up for an account.
        7. Do not say "Here's a friendly message: "
        """),
        ("user", "{user_message}"),
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    response = await llm.ainvoke(template_prompt.invoke({"user_message": user_message}))
    response = cast(str, response)
    state["suggestions"] = [response]
    return state