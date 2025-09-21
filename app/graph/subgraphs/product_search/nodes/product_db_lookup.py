from app.models.chat import GlobalState
from app.services.db.db import db_service
from app.services.workflow_state import get_workflow_state, update_workflow_state
import json

async def product_db_lookup_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for looking up products in the database based on extracted parameters.
    """
    # Get workflow-specific state
    workflow_state = get_workflow_state(state, "product_search")

    # Get filters from workflow state
    filters = workflow_state.get("filters", {})
    filters = filters.model_dump()

    # Build query conditions
    conditions = []
    params = []

    if filters.get("product_category"):
        conditions.append("category = ?")
        params.append(filters["product_category"])

    if filters.get("gender"):
        conditions.append("gender = ?")
        params.append(filters["gender"][0].upper())  # Convert 'male'/'female' to 'M'/'F'

    if filters.get("color"):
        conditions.append("color = ?")
        params.append(filters["color"].capitalize())

    if filters.get("price_max"):
        conditions.append("price <= ?")
        params.append(filters["price_max"])

    if filters.get("price_min"):
        conditions.append("price >= ?")
        params.append(filters["price_min"])

    # Build and execute query
    query = "SELECT * FROM products"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Add limit to prevent too many results
    query += " LIMIT 10"

    results = await db_service.execute_query(query, params)

    # Convert results to list of dicts for easier handling
    products = []
    if results:
        for row in results:
            # Parse images JSON string
            images = json.loads(row[10]) if row[10] else {}
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

    # Update workflow state with search results
    workflow_state = {
        "query": workflow_state.get("query", ""),
        "filters": filters,
        "products": products,
    }

    # Debug logging before update
    print("📝 Saving product search state:", workflow_state)

    # Update global state with workflow-specific state
    state = update_workflow_state(state, "product_search", workflow_state)

    # Debug logging after update
    print("✅ Updated workflow states:", state.get("workflow_states", {}))

    # Set standardized workflow outputs
    state["workflow_output_text"] = f"Found {len(products)} matching products."
    state["workflow_output_json"] = {
        "template":"product_search_results",
        "payload":products
    }

    return state
