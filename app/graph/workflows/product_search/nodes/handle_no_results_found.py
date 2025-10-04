from typing import  cast
from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service
from app.services.widget_events import WidgetEventType, widget_event_emitter

async def handle_no_results_found_node(state: ProductSearchState) -> ProductSearchState:
    """Handle no results found."""
    search_query = state.get("search_query", "")
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are a part of the e-commerce chatbot assistant for comocom and your responsibility is to handle the case when user has searched for some product and that product could not be found in the system.
            Your tone should be professional and polite.

            1. Politely informs the user that you could not find the product.
            2. Do not use technical words like "query", "results", or "response".
            3. Keeps the tone conversational and natural, as if chatting with a human.
            4. Do not send the search query in the message back to the user.
            5. Simply tell the user that no product was found with the given search query and suggest them to try again with different search query.
            6. Do not say "Here's a friendly message:"
            7. Make sure to add the product name in the response
        """),
        ("user", "{search_query}"),
    ])

    messages = template_prompt.invoke({"search_query": search_query})
    response = await llm_service.get_llm_without_tools().ainvoke(messages)
    response = cast(str, response)

    state["suggestions"] = [response]
    widget_event_emitter.emit(
        WidgetEventType.PRODUCT_SEARCH_RESULTS,
        {
            "suggested_actions": ["Try again"],
            "search_query": search_query
        }
    )

    return state