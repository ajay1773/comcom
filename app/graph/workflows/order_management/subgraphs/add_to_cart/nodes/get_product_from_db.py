

from typing import Any, Dict, cast
from app.graph.workflows.order_management.types import AddToCartState
from app.services.db.product import product_service
async def get_product_from_db_node(state: AddToCartState) -> AddToCartState:
    """Get the product from the database."""

    product_details = state.get("product_details", {})
    product = await product_service.get_product(product_details)

    state['product_details'] = cast(Dict[str, Any], product) if product else {}
    return state