
from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signup.types import GenerateSignupFormState
from app.services.llm import llm_service
from app.types.common import BASE_PERSONA_PROMPT

async def send_signup_form_node(state: GenerateSignupFormState) -> GenerateSignupFormState:
    """Send the login form to the user."""

    user_message = state.get('search_query')
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", BASE_PERSONA_PROMPT + """
        ###TASK:
        - Generate a short, helpful message that tells user to sign up using the signup form that you have provided.

        ###RULES:
        - Do not include clickable links
        - Simply guide them to use the signup form for their signup.
        - Do not tell user to use the forget password feature as that is not a feature of the system.
        """),
        ("user","{user_message}")
    ])

    
    messages = template_prompt.invoke({"user_message": user_message})
    response = await llm_service.get_llm_without_tools().ainvoke(messages)
    response = cast(str, response)
    state["suggestions"] = [response]
    return state
