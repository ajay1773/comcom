"""Handle edge cases in product comparison with LLM responses and StatusCard events."""

from app.graph.workflows.product_comparison.types import ProductComparisonState
from app.services.widget_events import widget_event_emitter, WidgetEventType
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.utils.conversation_context import format_conversation_context_with_template


async def handle_edge_cases_node(state: ProductComparisonState) -> ProductComparisonState:
    """Handle edge cases like no products found or category mismatches with LLM responses."""
    products = state.get("products", [])
    error_message = state.get("error_message")
    user_message = state.get("search_query", "")
    
    # Get conversation context
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="general",
        limit=3,
        fallback_message=""
    )
    
    # Case 1: No products found or error in fetching
    if error_message or not products:
        await _handle_no_products_found(state, user_message, conversation_context, error_message or "")
        state["edge_case_handled"] = True
        return state
    
    # Case 2: Only one product found
    if len(products) == 1:
        await _handle_single_product_found(state, user_message, conversation_context)
        state["edge_case_handled"] = True
        return state
    
    # Case 3: Check for category mismatch
    categories = [p.get("category", "").lower() for p in products if p.get("category")]
    unique_categories = list(set(categories))
    
    if len(unique_categories) > 1 and len(products) >= 2:
        await _handle_category_mismatch(state, user_message, conversation_context, products)
        state["category_mismatch_handled"] = True
        # Don't set edge_case_handled = True here, let user decide to continue
        return state
    
    # If no edge cases, continue with normal flow
    return state


async def _handle_no_products_found(state: ProductComparisonState, user_message: str, conversation_context: str, error_message: str = ""):
    """Handle case where no products are found."""
    
    # Generate LLM response for no products found
    no_products_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a helpful e-commerce assistant. The user tried to compare products but no products were found.
        
        Generate a friendly, helpful response that:
        1. Acknowledges that no products were found for comparison
        2. Suggests alternative actions the user can take
        3. Offers to help with product search instead
        4. Keeps the tone positive and helpful
        
        User's original request: {user_message}
        Error details: {error_message}
        
        Provide a concise, helpful response (2-3 sentences max).
        """),
        ("user", "{conversation_context}")
    ])
    
    try:
        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(
            no_products_prompt.invoke({
                "user_message": user_message,
                "error_message": error_message or "No products found for comparison",
                "conversation_context": conversation_context
            })
        )
        
        llm_response = str(response.content) if hasattr(response, 'content') else str(response)
        
        # Set state for output
        state["workflow_output_text"] = llm_response
        
        # Emit StatusCard event
        widget_event_emitter.emit(
            WidgetEventType.STATUS_CARD_NO_PRODUCTS_FOUND,
            {
                "title": "No Products Found",
                "subtitle": "I couldn't find products to compare based on your request.",
                "message": llm_response,
                "icon": "search-x",  # Icon identifier for frontend
                "actions": [
                    {"type": "search", "label": "Search Products", "action": "search_products"},
                    {"type": "help", "label": "Get Help", "action": "show_help"}
                ],
                "suggestions": [
                    "Try searching for products first",
                    "Be more specific with product names",
                    "Check product availability"
                ]
            }
        )
        
        state["suggestions"] = [
            "Search for products first",
            "Try different product names",
            "Browse product categories"
        ]
        
    except Exception as e:
        print(f"Error generating no products response: {e}")
        state["workflow_output_text"] = "I couldn't find any products to compare. Please try searching for products first or be more specific with product names."


async def _handle_single_product_found(state: ProductComparisonState, user_message: str, conversation_context: str):
    """Handle case where only one product is found."""
    product = state.get("products", [])[0]
    
    single_product_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a helpful e-commerce assistant. The user wanted to compare products but only one product was found.
        
        Generate a friendly response that:
        1. Acknowledges that only one product was found
        2. Briefly describes the found product
        3. Suggests finding similar products for comparison
        4. Offers alternative actions
        
        Found product: {product_name} by {brand} - ${price}
        User's original request: {user_message}
        
        Provide a helpful response (2-3 sentences max).
        """),
        ("user", "{conversation_context}")
    ])
    
    try:
        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(
            single_product_prompt.invoke({
                "product_name": product.get("title", "Unknown"),
                "brand": product.get("brand", "Unknown"),
                "price": product.get("price", 0),
                "user_message": user_message,
                "conversation_context": conversation_context
            })
        )
        
        llm_response = str(response.content) if hasattr(response, 'content') else str(response)
        
        state["workflow_output_text"] = llm_response
        
        # Emit StatusCard event
        widget_event_emitter.emit(
            WidgetEventType.STATUS_CARD_COMPARISON_ERROR,
            {
                "title": "Need More Products",
                "subtitle": f"Found only 1 product: {product.get('title', 'Unknown')}",
                "message": llm_response,
                "icon": "package-plus",
                "actions": [
                    {"type": "search", "label": "Find Similar Products", "action": "search_similar"},
                    {"type": "view", "label": "View Product", "action": f"view_product_{product.get('id')}"}
                ],
                "product": {
                    "id": product.get("id"),
                    "name": product.get("title"),
                    "brand": product.get("brand"),
                    "price": product.get("price")
                }
            }
        )
        
    except Exception as e:
        print(f"Error generating single product response: {e}")
        state["workflow_output_text"] = f"I found only one product: {product.get('title', 'Unknown')}. Please specify another product to compare with."


async def _handle_category_mismatch(state: ProductComparisonState, user_message: str, conversation_context: str, products: list):
    """Handle case where products are from different categories."""
    
    # Get category information
    product_categories = []
    for product in products:
        product_categories.append({
            "name": product.get("title", "Unknown"),
            "category": product.get("category", "Unknown"),
            "brand": product.get("brand", "Unknown")
        })
    
    category_mismatch_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a helpful e-commerce assistant. The user wants to compare products, but they are from different categories.
        
        Products and their categories:
        {products_info}
        
        Generate a response that:
        1. Explains that the products are from different categories
        2. Mentions why comparing products from different categories might not be meaningful
        3. Suggests comparing products within the same category instead
        4. Offers to help find similar products in the same category
        
        User's original request: {user_message}
        
        Be helpful and suggest alternatives (2-3 sentences max).
        """),
        ("user", "{conversation_context}")
    ])
    
    try:
        # Format products info for prompt
        products_info = "\n".join([
            f"- {p['name']} ({p['brand']}) - Category: {p['category']}"
            for p in product_categories
        ])
        
        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(
            category_mismatch_prompt.invoke({
                "products_info": products_info,
                "user_message": user_message,
                "conversation_context": conversation_context
            })
        )
        
        llm_response = str(response.content) if hasattr(response, 'content') else str(response)
        
        state["workflow_output_text"] = llm_response
        state["error_message"] = "Products from different categories cannot be meaningfully compared"
        
        # Emit StatusCard event
        widget_event_emitter.emit(
            WidgetEventType.STATUS_CARD_CATEGORY_MISMATCH,
            {
                "title": "Different Categories",
                "subtitle": "These products are from different categories and may not be comparable.",
                "message": llm_response,
                "icon": "alert-triangle",
                "products": [
                    {
                        "id": p.get("id"),
                        "name": p.get("title"),
                        "category": p.get("category"),
                        "brand": p.get("brand")
                    }
                    for p in products
                ],
                "actions": [
                    {"type": "search", "label": "Find Similar Products", "action": "search_similar_category"},
                    {"type": "continue", "label": "Compare Anyway", "action": "force_comparison"}
                ],
                "suggestions": [
                    f"Compare products within {product_categories[0]['category']} category",
                    f"Find alternatives to {product_categories[0]['name']}",
                    "Browse by category"
                ]
            }
        )
        
    except Exception as e:
        print(f"Error generating category mismatch response: {e}")
        state["workflow_output_text"] = "These products are from different categories and may not be directly comparable. Consider comparing products within the same category for better insights."
