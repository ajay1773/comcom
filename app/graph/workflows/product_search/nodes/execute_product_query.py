from app.graph.workflows.product_search.types import ProductSearchState
from app.services.db.db import db_service
import json
from typing import Dict, Any


async def execute_product_query_node(state: ProductSearchState) -> Dict[str, Any]:
    """
    LangGraph node for looking up products in the database based on extracted parameters.
    Returns only updates to the state (LangGraph merges them automatically).
    """
    filters = state.get("search_parameters", {})

    # Build query
    conditions = []
    params = []

    if filters.get("product_category"):
        conditions.append("category = ?")
        params.append(filters["product_category"])

    if filters.get("gender"):
        conditions.append("gender = ?")
        params.append(filters["gender"][0].upper())

    if filters.get("color"):
        conditions.append("color = ?")
        params.append(filters["color"].capitalize())

    if filters.get("price_max"):
        conditions.append("price <= ?")
        params.append(filters["price_max"])

    if filters.get("price_min"):
        conditions.append("price >= ?")
        params.append(filters["price_min"])

    query = "SELECT * FROM products"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " LIMIT 10"

    results = await db_service.execute_query(query, params)

    # Convert results into product dicts
    products = []
    if results:
        for row in results:
            images = json.loads(row[10]) if row[10] else []
            available_sizes = json.loads(row[11]) if row[11] else []
            products.append({
                "id": row[0],
                "name": row[1],
                "gender": row[4],
                "category": row[2],
                "min_price": row[3],
                "max_price": row[3],
                "color": row[9],
                "brand": row[5],
                "material": row[6],
                "style": row[7],
                "pattern": row[8],
                "images": images,
                "available_sizes": available_sizes,
                "unit": row[12],
            })

    # ✅ Return only updated fields (LangGraph will merge this into state)
    return {
        "search_results": products,
        "result_count": len(products),
        "suggestions": [],  # can be populated later
    }
