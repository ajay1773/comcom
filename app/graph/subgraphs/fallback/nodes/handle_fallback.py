from app.models.chat import GlobalState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any

async def handle_fallback_node(state: GlobalState) -> GlobalState:
    """
    Handle fallback scenarios including smalltalk, FAQ, and unknown intents.
    """
    user_message = state.get("user_message", "")
    intent = state.get("intent", "unknown")

    # Different responses based on intent type
    if intent == "smalltalk":
        response_text = await _handle_smalltalk(user_message)
    elif intent == "faq":
        response_text = await _handle_faq(user_message)
    elif intent == "support_query":
        response_text = await _handle_support_query(user_message)
    else:  # unknown or other
        response_text = await _handle_unknown(user_message)

    # Update state with response
    state["workflow_output_text"] = response_text
    state["workflow_output_json"] = {
        "template": "fallback_response",
        "payload": {
            "intent": intent,
            "response_type": "conversational",
            "user_query": user_message
        }
    }

    return state

async def _handle_smalltalk(user_message: str) -> str:
    """Handle casual conversation."""
    try:
        smalltalk_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a friendly e-commerce assistant. Respond naturally to casual conversation.
                Keep responses helpful, engaging, and related to shopping/e-commerce when possible.
                Be concise but friendly. Suggest shopping-related topics when appropriate.
                """),
            ("user", "{message}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(smalltalk_prompt.invoke({"message": user_message}))
        return response.content.strip()
    except Exception as e:
        # Fallback response
        return "I'm here to help you with shopping and product questions! What would you like to know about our products?"

async def _handle_faq(user_message: str) -> str:
    """Handle frequently asked questions."""
    try:
        faq_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are an e-commerce assistant answering FAQs.
                Provide helpful, accurate information about common e-commerce topics:
                - Shipping and delivery
                - Returns and refunds
                - Payment methods
                - Product information
                - Account management
                - General policies

                If the question doesn't match common FAQs, provide a general helpful response.
                """),
            ("user", "{message}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(faq_prompt.invoke({"message": user_message}))
        return response.content.strip()
    except Exception as e:
        # Fallback response
        return "I'd be happy to help answer your questions about our products and services. What would you like to know?"

async def _handle_support_query(user_message: str) -> str:
    """Handle support-related queries."""
    try:
        support_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a customer support assistant for an e-commerce platform.
                Provide helpful guidance for support issues:
                - Order problems
                - Account issues
                - Technical problems
                - Product issues

                Be empathetic, offer solutions, and escalate when necessary.
                """),
            ("user", "{message}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(support_prompt.invoke({"message": user_message}))
        return response.content.strip()
    except Exception as e:
        # Fallback response
        return "I'm here to help with any support issues you might have. Could you please provide more details about what you need assistance with?"

async def _handle_unknown(user_message: str) -> str:
    """Handle unknown or unclear intents."""
    try:
        unknown_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                The user's message wasn't clearly understood. Respond helpfully by:
                1. Acknowledging the message
                2. Asking for clarification
                3. Suggesting common things users might want to do
                4. Keeping the tone friendly and helpful

                Common suggestions: product search, order help, account questions, etc.
                """),
            ("user", "{message}")
        ])

        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(unknown_prompt.invoke({"message": user_message}))
        return response.content.strip()
    except Exception as e:
        # Fallback response
        return "I'm not sure I understood that correctly. Could you please rephrase your question? I'm here to help with product searches, orders, and general questions about our store!"
