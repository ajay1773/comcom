from typing import Dict, Any, List
import json
from app.graph.workflows.product_search.types import ProductSearchState


async def format_results_node(state: ProductSearchState) -> Dict[str, Any]:
    """
    Format product results for frontend consumption with deduplication.
    
    This node:
    1. Removes duplicate products (by SKU)
    2. Parses JSON strings in products (tags, images, etc.)
    3. Adds metadata (final_price, badges, etc.)
    4. Prepares final response structure
    """
    
    products = state.get("search_results", [])
    
    # Remove duplicates first (by SKU)
    products = _remove_duplicates(products)
    
    # Format each product
    formatted_products = []
    for product in products:
        formatted_product = format_product(product)
        formatted_products.append(formatted_product)
    
    return {
        "search_results": formatted_products,
        "result_count": len(formatted_products)
    }


def _remove_duplicates(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate products by SKU."""
    seen_skus = set()
    unique_products = []
    
    for product in products:
        sku = product.get("sku")
        if sku and sku not in seen_skus:
            seen_skus.add(sku)
            unique_products.append(product)
        elif not sku:
            # If no SKU, keep the product
            unique_products.append(product)
    
    return unique_products


def format_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a single product for frontend.
    
    Parses JSON strings and adds computed fields.
    """
    formatted = product.copy()
    
    # Parse JSON strings to objects/arrays
    if isinstance(formatted.get("tags"), str):
        try:
            formatted["tags"] = json.loads(formatted["tags"])
        except (json.JSONDecodeError, TypeError):
            formatted["tags"] = []
    
    if isinstance(formatted.get("images"), str):
        try:
            formatted["images"] = json.loads(formatted["images"])
        except (json.JSONDecodeError, TypeError):
            formatted["images"] = []
    
    if isinstance(formatted.get("dimensions"), str):
        try:
            formatted["dimensions"] = json.loads(formatted["dimensions"])
        except (json.JSONDecodeError, TypeError):
            formatted["dimensions"] = {}
    
    if isinstance(formatted.get("available_sizes"), str):
        try:
            formatted["available_sizes"] = json.loads(formatted["available_sizes"])
        except (json.JSONDecodeError, TypeError):
            formatted["available_sizes"] = []
    
    # Add computed fields
    # Calculate final price after discount
    price = formatted.get("price", 0)
    discount = formatted.get("discount_percentage", 0)
    if price and discount:
        final_price = price * (1 - discount / 100)
        formatted["final_price"] = round(final_price, 2)
        formatted["savings"] = round(price - final_price, 2)
    else:
        formatted["final_price"] = price
        formatted["savings"] = 0
    
    # Add availability badge
    stock = formatted.get("stock", 0)
    if stock == 0:
        formatted["availability_badge"] = "Out of Stock"
    elif stock < 10:
        formatted["availability_badge"] = "Low Stock"
    elif stock < 50:
        formatted["availability_badge"] = "Limited Stock"
    else:
        formatted["availability_badge"] = "In Stock"
    
    # Add rating badge
    rating = formatted.get("rating", 0)
    if rating >= 4.5:
        formatted["rating_badge"] = "Excellent"
    elif rating >= 4.0:
        formatted["rating_badge"] = "Very Good"
    elif rating >= 3.5:
        formatted["rating_badge"] = "Good"
    elif rating >= 3.0:
        formatted["rating_badge"] = "Average"
    else:
        formatted["rating_badge"] = "Fair"
    
    return formatted

