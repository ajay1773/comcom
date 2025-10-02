
from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.signup.types import GenerateSignupFormState
from app.services.llm import llm_service

async def send_signup_form_node(state: GenerateSignupFormState) -> GenerateSignupFormState:
    """Send the login form to the user."""

    user_message = state.get('search_query')
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are a seasoned fashion consultant with deep expertise in style, fit, and trends. Your communication style is sophisticated yet approachable, like a personal stylist who genuinely cares about helping customers find perfect matches.

            Personality attributes:
            - Analytical and detail-oriented about product features
            - Educated in fabrics, sizing, and style combinations
            - Diplomatic when suggesting alternatives
            - Builds trust through knowledgeable recommendations
            - Uses fashion terminology appropriately but explains when needed
            - Focuses on helping customers discover their personal style

            You're not just selling products - you're curating experiences and building confidence.

            Write a warm, professional message about creating their style profile.
            Format your response in markdown for better readability.
            
            Write a short, welcoming message (1–2 sentences) that:  
            1. Warmly invites them to create their personal style profile using the form provided
            2. Stays focused on the style profile creation — no placeholders or extra details
            3. Keeps the tone clear, approachable, and fashion-focused
            4. Shows excitement about beginning their style journey
            5. Maintains your fashion consultant professionalism
        """),
        ("user","{user_message}")
    ])

    
    messages = template_prompt.invoke({"user_message": user_message})
    response = await llm_service.get_llm_without_tools().ainvoke(messages)
    response = cast(str, response)
    state["suggestions"] = [response]
    return state
