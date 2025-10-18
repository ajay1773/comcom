"""Node for formatting bundle results for display."""

from typing import Dict, Any
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service
from app.services.widget_events import widget_event_emitter, WidgetEventType


async def format_bundle_results_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Format bundle results for display.
    Uses LLM to generate natural language response and creates widget JSON for frontend rendering.
    """

    bundle_results = state.get("bundle_results", {})
    bundle_title = state.get("bundle_title", "Recommended Bundle")
    bundle_description = state.get("bundle_description", "")
    result_count = state.get("result_count", 0)
    search_query = state.get("search_query", "")
    use_case = state.get("use_case", search_query)

    # Handle NO RESULTS case with LLM
    if result_count == 0:
        no_results_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a friendly and helpful shopping assistant for COMCOM.
            
            The user requested a product bundle for a specific activity or use case, but we couldn't find any matching products in our inventory.
            
            Your task:
            1. Politely acknowledge their request
            2. Apologize that we don't currently have those products
            3. Suggest they try a different activity or check back later
            4. Keep the tone warm, conversational, and encouraging
            5. Do not use technical terms like "query", "results", or "database"
            6. Keep the response concise (2-3 sentences)
            
            Example: "I'd love to help you with cricket equipment! Unfortunately, we don't have those items available right now. Feel free to ask about other activities or check back soon!"
            """),
            ("user", "User's request: {use_case}")
        ])
        
        messages = no_results_prompt.invoke({"use_case": use_case})
        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(messages)
        response_text = str(response.content) if hasattr(response, "content") else str(response)
        
        return {
            "workflow_output_text": response_text,
            "workflow_output_json": None
        }

    # Group by priority
    essential_items = {}
    recommended_items = {}
    optional_items = {}

    for category, products in bundle_results.items():
        if not products:
            continue

        priority = products[0]["priority"]

        if priority == 1:
            essential_items[category] = products
        elif priority == 2:
            recommended_items[category] = products
        else:
            optional_items[category] = products

    # Create widget JSON
    widget_json = {
        "template": "product_bundle_results",
        "payload": {
            "bundle_title": bundle_title,
            "bundle_description": bundle_description,
            "essential_items": essential_items,
            "recommended_items": recommended_items,
            "optional_items": optional_items,
            "total_categories": len(bundle_results),
            "total_products": result_count
        }
    }

    # Generate natural language response using LLM
    success_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a friendly and knowledgeable shopping assistant for COMCOM.
        
        ## Your Role
        You help customers discover product bundles tailored to their activities, hobbies, or use cases.
        
        ## Your Communication Style
        - Warm and enthusiastic about helping them get started
        - Use conversational language that feels human and natural
        - Show excitement about the products without being pushy
        - Use "I" and "you" to create a personal connection
        - Keep it concise but engaging (2-4 sentences)
        
        ## Your Task
        The user requested a product bundle for a specific activity. We've found multiple products organized by priority (essential, recommended, optional).
        
        Generate a short, friendly message that:
        1. Acknowledges their request with enthusiasm
        2. Mentions that you've curated a bundle for them
        3. Briefly explains the products are organized by priority
        4. Encourages them to explore the products shown below
        5. Keeps the tone conversational and supportive
        
        Do NOT:
        - List specific products or prices
        - Use markdown formatting
        - Mention technical terms like "widget", "categories", or "payload"
        - Be overly formal or robotic
        
        Example tone:
        "I've put together a great cricket starter kit for you! I've organized everything into must-haves, recommended items, and optional upgrades to make it easy to find what you need. Take a look at the products below and let me know if you'd like to add anything to your cart!"
        """),
        ("user", """User's request: {use_case}
Bundle title: {bundle_title}
Bundle description: {bundle_description}
Total products found: {result_count}
Essential categories: {essential_count}
Recommended categories: {recommended_count}
Optional categories: {optional_count}""")
    ])

    messages = success_prompt.invoke({
        "use_case": use_case,
        "bundle_title": bundle_title,
        "bundle_description": bundle_description,
        "result_count": result_count,
        "essential_count": len(essential_items),
        "recommended_count": len(recommended_items),
        "optional_count": len(optional_items)
    })
    
    llm = llm_service.get_llm_without_tools()
    response = await llm.ainvoke(messages)
    response_text = str(response.content) if hasattr(response, "content") else str(response)

    # Emit widget event for frontend
    widget_event_emitter.emit(
        WidgetEventType.PRODUCT_BUNDLE_RESULTS,
        {
            "bundle_title": bundle_title,
            "bundle_description": bundle_description,
            "essential_items": essential_items,
            "recommended_items": recommended_items,
            "optional_items": optional_items,
            "total_categories": len(bundle_results),
            "total_products": result_count,
            "success_message": response_text,
            "suggested_actions": [
                "Add to cart",
                "View details",
                "Continue shopping"
            ]
        }
    )

    return {
        "workflow_output_text": response_text,
        "workflow_output_json": widget_json
    }

