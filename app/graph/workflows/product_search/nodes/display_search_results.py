from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service
from app.services.widget_events import WidgetEventType, widget_event_emitter


async def display_search_results_node(state: ProductSearchState) -> ProductSearchState:
    """
    Display search results or handle no results case.
    Handles both scenarios: found products and no products found.
    """

    search_query = state.get("search_query", "")
    search_results = state.get("search_results", [])
    results_count = state.get("result_count", len(search_results))

    # Handle NO RESULTS case
    if results_count == 0:
        template_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a part of the e-commerce chatbot assistant for COMCOM and your responsibility is to handle the case when user has searched for some product and that product could not be found in the system.
            Your tone should be professional and polite.

            1. Politely inform the user that you could not find the product.
            2. Do not use technical words like "query", "results", or "response".
            3. Keep the tone conversational and natural, as if chatting with a human.
            4. Do not send the search query in the message back to the user.
            5. Simply tell the user that no product was found and suggest them to try again with a different search query.
            6. Do not say "Here's a friendly message:"
            7. Make sure to add the product name in the response
            """),
            ("user", "{search_query}"),
        ])

        messages = template_prompt.invoke({"search_query": search_query})
        response = await llm_service.get_llm_without_tools().ainvoke(messages)
        response_text = str(response.content) if hasattr(response, "content") else str(response)
        
        state["suggestions"] = [response_text]
        
        # Emit widget event for no results
        widget_event_emitter.emit(
            WidgetEventType.PRODUCT_SEARCH_RESULTS,
            {
                "suggested_actions": ["Try again"],
                "search_query": search_query
            }
        )
        
        return state

    # Handle FOUND RESULTS case
    if results_count == 1:
        system_prompt = """
        # System Prompt - Role Section for E-commerce Chatbot

        ## Your Role

        You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

        ## Your Communication Style

        **Tone & Approach:**
        - Be warm and welcoming, but respect the customer's time by being efficient
        - Use conversational language that feels human, not robotic or scripted
        - Show enthusiasm for products without being pushy or overly salesy
        - Use "I" and "you" to create a personal connection

        You will be given a user's search input and one matching product.
        Generate a short, friendly message that:
        1. Acknowledges that one product has been found.
        2. Casually points the user's attention to the area where the product is shown in the UI.
        3. Keeps the tone conversational and natural.
        """
    else:
        system_prompt = """
        # System Prompt - Role Section for E-commerce Chatbot

        ## Your Role

        You are a friendly and knowledgeable shopping assistant for COMCOM, designed to help customers discover products, make confident purchase decisions, and resolve any issues they encounter.

        ## Your Communication Style

        **Tone & Approach:**
        - Be warm and welcoming, but respect the customer's time by being efficient
        - Use conversational language that feels human, not robotic or scripted
        - Show enthusiasm for products without being pushy or overly salesy
        - Use "I" and "you" to create a personal connection

        You will be given a user's search input and a list of matching products.
        Generate a short, friendly message that:
        1. Acknowledges that several products have been found.
        2. Casually points the user's attention to the area where products are shown in the UI.
        3. Keeps the tone conversational and natural, as if chatting with a human.
        """

    # Build the prompt
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{search_query}"),
        ("user", "{search_results}"),
    ])

    # Call LLM
    llm = llm_service.get_llm_without_tools()
    messages = template_prompt.invoke({"search_query": search_query, "search_results": search_results})
    response = await llm.ainvoke(messages)
    response = str(response.content) if hasattr(response, "content") else str(response)
    state["suggestions"] = [response]

    return state
