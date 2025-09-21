
from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signup.types import GenerateSignupFormState
from app.services.llm import llm_service

async def send_signup_form_node(state: GenerateSignupFormState) -> GenerateSignupFormState:
    """Send the login form to the user."""

    user_message = state.get('search_query')
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are a friendly assistant for an e-commerce platform.  
            Write a very short, warm message (1–2 sentences) that:  
            1. Politely tells the user they can sign up by filling out the signup form provided.  
            2. Stays focused on the form — do not add placeholders like [insert form] or extra details.  
            3. Keeps the tone clear, approachable, and conversational, without sounding like a sales pitch or invitation to a "community".  
        """),
        ("user","{user_message}")
    ])

    
    messages = template_prompt.invoke({"user_message": user_message})
    response = await llm_service.get_llm_without_tools().ainvoke(messages)
    response = cast(str, response)
    state["suggestions"] = [response]
    return state
