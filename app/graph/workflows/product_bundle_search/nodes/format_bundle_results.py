"""Node for formatting bundle results for display."""

from typing import Dict, Any
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState


async def format_bundle_results_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Format bundle results for display.
    Creates widget JSON for frontend rendering.
    """

    bundle_results = state.get("bundle_results", {})
    bundle_title = state.get("bundle_title", "Recommended Bundle")
    bundle_description = state.get("bundle_description", "")
    result_count = state.get("result_count", 0)

    if result_count == 0:
        return {
            "formatted_output": "I couldn't find products for your use case. Please try a different activity or provide more details.",
            "widget_json": None
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

    # Create text summary
    essential_text = "\n".join([f"- {cat}: {len(prods)} options" for cat, prods in essential_items.items()])
    recommended_text = "\n".join([f"- {cat}: {len(prods)} options" for cat, prods in recommended_items.items()])
    optional_text = "\n".join([f"- {cat}: {len(prods)} options" for cat, prods in optional_items.items()])

    formatted_output = f"""I've prepared a **{bundle_title}** for you!

{bundle_description}

📦 **Essential Items** ({len(essential_items)} categories)
{essential_text}

{'✨ **Recommended Items** (' + str(len(recommended_items)) + ' categories)' if recommended_items else ''}
{recommended_text if recommended_items else ''}

{'💎 **Optional Upgrades** (' + str(len(optional_items)) + ' categories)' if optional_items else ''}
{optional_text if optional_items else ''}

Select products from each category to create your custom bundle!"""

    return {
        "formatted_output": formatted_output,
        "widget_json": widget_json
    }

