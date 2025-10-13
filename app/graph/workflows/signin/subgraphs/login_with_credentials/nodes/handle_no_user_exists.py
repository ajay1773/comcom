from typing import cast
from app.graph.workflows.signin.types import LoginWithCredentialsState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service
from app.types.common import BASE_PERSONA_PROMPT
from app.utils.conversation_context import format_conversation_context_with_template

async def handle_no_user_exists(state: LoginWithCredentialsState) -> LoginWithCredentialsState:
    """Handle no user exists."""
    user_message = state.get("user_message", "")
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="general",
        limit=5,
        fallback_message=""
    )
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", BASE_PERSONA_PROMPT + """
        ###TASK:
        - Politely informs the user that no user exists with the given credentials.

        ###RULES:
        - Do not use technical words like "query", "results", or "response".
        - Suggest them to sign up for an account.
        - Do not send the email or password in the message back to the user.
        - Do not tell user to use the forget password feature as that is not a feature of the system.
        """),
        ("assistant", "{conversation_context}"),
        ("user", "{user_message}"),
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    response = await llm.ainvoke(template_prompt.invoke({"user_message": user_message, "conversation_context": conversation_context}))
    response = cast(str, response)
    state["suggestions"] = [response]
    return state