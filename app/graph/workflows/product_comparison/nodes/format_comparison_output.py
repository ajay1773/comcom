"""Format comparison output for display to user."""

from app.graph.workflows.product_comparison.types import ProductComparisonState
from app.services.widget_events import widget_event_emitter, WidgetEventType


async def format_comparison_output_node(state: ProductComparisonState) -> ProductComparisonState:
    """Format the comparison analysis and product data for display."""
    products = state.get("products", [])
    comparison_analysis = state.get("comparison_analysis", {})
    error_message = state.get("error_message")
    category_mismatch_handled = state.get("category_mismatch_handled", False)
    
    # Handle error case
    if error_message:
        state["workflow_output_text"] = f"I couldn't complete the comparison: {error_message}"
        state["workflow_output_json"] = {
            "template": "error",
            "payload": {
                "error_message": error_message,
                "suggestion": "Please try specifying product names more clearly or search for products first."
            }
        }
        state["suggestions"] = ["Try searching for products first", "Be more specific with product names"]
        return state
    
    # Handle case where no products found
    if not products or len(products) < 2:
        state["workflow_output_text"] = "I need at least 2 products to create a comparison. Could you please specify which products you'd like to compare?"
        state["workflow_output_json"] = {
            "template": "error",
            "payload": {
                "error_message": "Insufficient products for comparison",
                "suggestion": "Try searching for products first or specify product names more clearly."
            }
        }
        state["suggestions"] = ["Search for products first", "Try: 'Compare Product A vs Product B'"]
        return state
    
    # Get analysis text
    analysis_text = comparison_analysis.get("analysis_text", "")
    
    # Build comparison table data
    comparison_table = {}
    comparison_table["Product Name"] = [p.get("title", "Unknown") for p in products]
    comparison_table["Brand"] = [p.get("brand", "Unknown") for p in products]
    comparison_table["Price"] = [f"${p.get('price', 0)}" for p in products]
    comparison_table["Rating"] = [f"{p.get('rating', 0)}/5 ⭐" for p in products]
    comparison_table["Stock"] = [
        "In Stock" if p.get("stock", 0) > 0 else "Out of Stock" 
        for p in products
    ]
    comparison_table["Discount"] = [f"{p.get('discount_percentage', 0)}% OFF" for p in products]
    
    state["comparison_table"] = comparison_table
    
    # Format output text (the AI analysis)
    state["workflow_output_text"] = analysis_text

    widget_event_emitter.emit(
        WidgetEventType.PRODUCT_COMPARISON_RESULTS,
        {
            "products": [
                {
                    "id": p.get("id"),
                    "name": p.get("title"),
                    "brand": p.get("brand"),
                    "price": p.get("price"),
                    "rating": p.get("rating"),
                    "images": p.get("images", ""),
                    "stock": p.get("stock", 0),
                    "discount": p.get("discount_percentage", 0),
                    "category": p.get("category", "")
                }
                for p in products
            ],
            "comparison_table": comparison_table,
            "product_count": len(products),
            "criteria_used": comparison_analysis.get("criteria_used", []),
            "category_mismatch_warning": category_mismatch_handled,
            "categories": list(set([p.get("category", "Unknown") for p in products])) if category_mismatch_handled else []
        }
    )
    
    # Add helpful suggestions
    state["suggestions"] = [
        "Ask specific questions about the comparison",
        "Search for similar products",
        "Add to cart"
    ]
    
    print(f"Formatted comparison output for {len(products)} products")
    
    return state

