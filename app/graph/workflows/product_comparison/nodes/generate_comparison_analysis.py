"""Generate intelligent comparison analysis using LLM."""

from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.utils.conversation_context import format_conversation_context_with_template
from app.graph.workflows.product_comparison.types import ProductComparisonState
from app.types.common import BASE_PERSONA_PROMPT
import json



async def generate_comparison_analysis_node(state: ProductComparisonState) -> ProductComparisonState:
    """Generate intelligent comparison insights using LLM."""
    products = state.get("products", [])
    criteria = state.get("comparison_criteria", [])
    user_context = state.get("user_context", "")
    category_mismatch_handled = state.get("category_mismatch_handled", False)
    
    if not products or len(products) < 2:
        state["error_message"] = "Need at least 2 products for analysis"
        return state
    
    # Get conversation context
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="general",
        limit=5,
        fallback_message=""
    )
    
    # Prepare product data for LLM (simplified version)
    products_summary = []
    for product in products:
        products_summary.append({
            "name": product.get("title", "Unknown"),
            "brand": product.get("brand", "Unknown"),
            "price": product.get("price", 0),
            "rating": product.get("rating", 0),
            "description": product.get("description", "")[:200],  # Limit description length
            "category": product.get("category", ""),
            "stock": product.get("stock", 0),
            "discount": product.get("discount_percentage", 0)
        })
    
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", BASE_PERSONA_PROMPT + """
        
        TASK:
        Generate a detailed comparison analysis in markdown format that includes:
        
        1. **Overview**: Brief introduction to the products being compared
        2. **Key Differences**: What sets these products apart (most important first)
        3. **Similarities**: What they have in common
        4. **Detailed Comparison**: Compare based on:
           - Price & Value
           - Features & Specifications
           - Quality & Ratings
           - Availability & Stock
        5. **Pros & Cons**: For each product
        6. **Best For**: Ideal use cases for each product
        7. **Recommendation**: Your expert suggestion based on the context
        
        GUIDELINES:
        - Be objective, fair, and unbiased
        - Consider user's context and preferences from conversation history
        - Highlight the most important differences first
        - Use clear, concise language in markdown format
        - Use bullet points and tables where appropriate
        - Consider price, features, ratings, availability, and specifications
        - If user has a specific question, answer it explicitly
        - Compare actual values (e.g., "$999 vs $899") not just descriptions
        
        {category_warning}
        
        Products to compare:
        {products_json}
        
        Comparison criteria focus:
        {criteria}
        
        User's specific question/context:
        {user_context}
        """),
        ("user", "Generate a detailed comparison analysis in markdown format"),
        ("user", "{conversation_context}")
    ])
    
    try:
        # Prepare category warning if needed
        category_warning = ""
        if category_mismatch_handled:
            categories = [p.get("category", "Unknown") for p in products]
            category_warning = f"""
            ⚠️ **IMPORTANT NOTE**: These products are from different categories ({', '.join(set(categories))}). 
            While they can still be compared, keep in mind that they serve different purposes and may not be directly comparable in all aspects.
            Focus on the aspects that matter most to the user's specific needs.
            """
        
        llm = llm_service.get_llm_without_tools()
        response = await llm.ainvoke(
            analysis_prompt.invoke({
                "products_json": json.dumps(products_summary, indent=2),
                "criteria": ", ".join(criteria),
                "user_context": user_context or "General comparison for shopping decision",
                "conversation_context": conversation_context,
                "category_warning": category_warning
            })
        )
        
        analysis_text = str(response.content) if hasattr(response, 'content') else str(response)
        
        state["comparison_analysis"] = {
            "analysis_text": analysis_text,
            "criteria_used": criteria,
            "product_count": len(products)
        }
        
        print(f"Generated comparison analysis for {len(products)} products")
        
    except Exception as e:
        print(f"Error generating comparison analysis: {e}")
        state["error_message"] = f"Failed to generate comparison analysis: {str(e)}"
    
    return state

