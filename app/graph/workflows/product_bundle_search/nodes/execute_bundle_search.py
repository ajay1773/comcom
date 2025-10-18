"""Node for executing product searches for each bundle item."""

from typing import Dict, Any, List, cast
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState
from app.services.db.product import product_service
from app.services.db.db import Product


async def execute_bundle_search_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Execute product searches for each bundle item.
    Reuses existing product_service.search_products_fts()
    """

    bundle_items = state.get("bundle_items", [])
    budget_total = state.get("budget_total")

    bundle_results = {

    }
    total_products = 0

    # Search for each bundle item
    for item in bundle_items:
        category = item["category"]
        keywords = item["keywords"]
        priority = item["priority"]

        if category not in bundle_results:
            bundle_results[category] = []

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
        if products:
            bundle_results[category].extend([
                {
                    "id": p.get("id"),
                    "title": p.get("title", ""),
                    "brand": p.get("brand", ""),
                    "price": p.get("price", 0),
                    "rating": p.get("rating", 0),
                    "thumbnail": p.get("thumbnail", ""),
                    "category": p.get("category", ""),
                    "priority": priority,
                    "purpose": item["purpose"],
                    "quantity": item["quantity"]
                } for p in cast(List[Dict[str, Any]], products)
            ])

        total_products += len(products)

    return {
        "bundle_results": bundle_results,
        "result_count": total_products
    }

