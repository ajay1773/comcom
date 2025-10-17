"""Node for executing product searches for each bundle item."""

from typing import Dict, Any
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState
from app.services.db.product import product_service


async def execute_bundle_search_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Execute product searches for each bundle item.
    Reuses existing product_service.search_products_fts()
    """

    bundle_items = state.get("bundle_items", [])
    budget_total = state.get("budget_total")

    bundle_results = {}
    total_products = 0

    # Search for each bundle item
    for item in bundle_items:
        category = item["category"]
        keywords = item["keywords"]
        priority = item["priority"]

        # Build search parameters
        search_params = {
            "keywords": keywords,
            "in_stock_only": True,
            "sort_by": "relevance"
        }

        # Search for products (limit based on priority)
        limit = {
            1: 5,  # Essential: show top 5 options
            2: 3,  # Recommended: show top 3
            3: 2,  # Optional: show top 2
        }.get(priority, 3)

        products = await product_service.search_products_fts(search_params, limit=limit)

        # Store results grouped by category
        bundle_results[category] = [
            {
                "id": p.id,
                "title": p.title,
                "brand": p.brand,
                "price": p.price,
                "rating": p.rating,
                "thumbnail": p.thumbnail,
                "category": p.category,
                "priority": priority,
                "purpose": item["purpose"],
                "quantity": item["quantity"]
            }
            for p in products
        ]

        total_products += len(products)

    return {
        "bundle_results": bundle_results,
        "result_count": total_products
    }

