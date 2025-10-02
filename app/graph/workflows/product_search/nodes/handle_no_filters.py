from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service
from app.services.widget_events import WidgetEventType, widget_event_emitter


async def handle_no_filters_node(state: ProductSearchState) -> ProductSearchState:
    """Handle cases when no filters are provided by the user."""
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

        The client has expressed interest in exploring styles but needs guidance to refine their vision.
        Help them discover their style direction with your fashion expertise.
        Format your response in markdown for better readability.
        
        Keep in mind these guidelines:
        1. Warmly acknowledge their style exploration with consultant enthusiasm
        2. Guide them to be more specific about their style vision
        3. Suggest style categories like apparel, footwear, accessories, handbags, or jewelry with fashion expertise
        4. Ask about style preferences like aesthetic, occasion, color palette, or designer preferences
        5. Keep the response conversational, knowledgeable, and inspiring
        6. Use fashion terminology that shows your expertise
        7. Keep the response concise but engaging and style-focused
        """),
        ("user", "{search_query}"),
    ])

    messages = template_prompt.invoke({"search_query": search_query})
    llm = llm_service.get_llm_without_tools()
    response = await llm.ainvoke(messages)
    response_content = str(response.content) if hasattr(response, "content") else str(response)
    
    state["suggestions"] = [response_content]
    
    # Emit widget event to show helpful suggestions
    widget_event_emitter.emit(
        WidgetEventType.PRODUCT_SEARCH_RESULTS,
        {
            "suggested_actions": [
                "Browse clothing",
                "Browse shoes", 
                "Browse accessories",
                "Browse bags",
                "Browse jewelry"
            ],
            "search_query": search_query
        }
    )

    return state
