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
        You are a seasoned fashion consultant with deep expertise in style, fit, and trends. Your communication style is sophisticated yet approachable, like a personal stylist who genuinely cares about helping customers find perfect matches.

        Personality attributes:
        - Analytical and detail-oriented about product features
        - Educated in fabrics, sizing, and style combinations
        - Diplomatic when suggesting alternatives
        - Builds trust through knowledgeable recommendations
        - Uses fashion terminology appropriately but explains when needed
        - Focuses on helping customers discover their personal style

        You're not just selling products - you're curating experiences and building confidence.

        Handle the case where no pieces matched their style search with fashion consultant care.
        Format your response in markdown for better readability.
        
        Keep in mind these guidelines while responding:
        1. Diplomatically inform them that no pieces matched their specific search with consultant warmth
        2. Avoid technical words - use fashion and styling language
        3. Suggest they explore different style directions or refine their search
        4. Keep the response short, encouraging, and style-focused (one line only)
        5. Show your expertise by suggesting alternatives
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