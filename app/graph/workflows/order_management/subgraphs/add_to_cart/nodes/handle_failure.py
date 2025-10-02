"""Handle failed add to cart operations."""

from app.graph.workflows.order_management.types import AddToCartState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_failure_node(state: AddToCartState) -> AddToCartState:
    """Handle failed add to cart operation with LLM-generated response."""
    
    error_message = state.get("error_message", "Unknown error occurred")
    product_details = state.get("product_details", {})
    user_query = state.get("search_query", "")
    
    if len(product_details.keys()) == 0:
        error_message = "I couldn't find that product in our inventory. Please try searching for it first or check the spelling."
    
    # Generate contextual failure response using LLM
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """# System Prompt - Role Section for E-commerce Chatbot

        ## Your Role

        You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

        ## Your Communication Style

        **Empathy & Understanding:**
        - Acknowledge customer emotions and concerns ("I understand how frustrating that must be...")
        - Show genuine care when customers face issues ("Let me make this right for you")
        - Be patient with questions, no matter how many times they're asked

        **Language Guidelines:**
        - Keep responses clear, concise, and easy to understand
        - Avoid jargon unless the customer uses it first
        - Use positive framing ("Here's what I can do..." instead of "I can't do that, but...")

        ## Problem-Solving Approach

        When customers face issues:
        1. **Acknowledge** - Validate their concern immediately
        2. **Apologize** - When appropriate, offer a sincere apology on behalf of the company
        3. **Act** - Provide a clear solution or next step
        4. **Assure** - Confirm the issue is resolved or being handled

        Generate a friendly, empathetic response when adding an item to cart fails.
        
        Guidelines:
        - Be understanding and apologetic
        - Explain the issue in simple, non-technical terms
        - Avoid technical jargon
        - Keep the message short and concise
        
        Context:
        - Product they tried to add: {product_name} by {brand}
        - User's original request: {user_query}
        - Technical error: {error_message}
        
        Common issues and appropriate responses:
        - Authentication required: Guide them to sign in or create an account
        - Product not found: Suggest searching again or browsing
        - Missing information: Ask for more details
        - System errors: Apologize and suggest trying again
        - Other errors: Apologize and suggest trying again
        """),
        ("user", """Please generate a helpful response for this add-to-cart failure that will guide the user to resolve the issue.""")
    ])

    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({
            "product_name": product_details.get("name", "the item"),
            "brand": product_details.get("brand", ""),
            "user_query": user_query,
            "error_message": error_message
        }))
        
        failure_message = str(response.content).strip()

        state["suggestions"] = [failure_message]
        
    except Exception:
        # Fallback failure message if LLM fails
        if "authentication" in error_message.lower() or "user" in error_message.lower():
            failure_message = "I need you to be signed in to add items to your cart. Please sign in and try again."
        elif "missing" in error_message.lower() or "required" in error_message.lower():
            failure_message = "I couldn't find all the information needed to add this item. Please provide more details about the product you'd like to add."
        elif not product_details:
            failure_message = "I couldn't find that product in our inventory. Please try searching for it first or check the spelling."
        else:
            failure_message = "I encountered an issue adding the item to your cart. Please try again in a moment."
        
        state["suggestions"] = [failure_message]
    
    return state
