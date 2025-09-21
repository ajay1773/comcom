
from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signin.types import GenerateSigninFormState
from app.services.llm import llm_service

async def send_login_form_node(state: GenerateSigninFormState) -> GenerateSigninFormState:
    """Send the login form to the user."""

    user_message = state.get('search_query')
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a helpful assistant in an e-commerce system.
        You need to tell the user that they can login using their email address and password on the login form that you are sending.
        Generate a short, friendly message that:
        1. Politely informs the user that they can login using their email address and password on the login form that you are sending.
        2. Do not use technical words like "query", "results", or "response".
        3. Keeps the tone conversational and natural, as if chatting with a human.
        4. Do not send the email or password in the message back to the user.
        5. Do not send any link or anything else to the user on which they can click to login.
        6. Simply tell the user that they can login using their email address and password on the login form that you are sending.
        7. Do not tell user about the direction of the form.
        """),
        ("user","{user_message}")
    ])

    
    messages = template_prompt.invoke({"user_message": user_message})
    response = await llm_service.get_llm_without_tools().ainvoke(messages)
    response = cast(str, response)
    state["suggestions"] = [response]
    return state
