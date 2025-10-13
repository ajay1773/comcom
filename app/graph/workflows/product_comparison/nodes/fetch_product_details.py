"""Fetch product details from database for comparison."""

from app.services.db.product import product_service
from app.graph.workflows.product_comparison.types import ProductComparisonState


async def fetch_product_details_node(state: ProductComparisonState) -> ProductComparisonState:
    """Fetch full product details from database for each product to compare."""
    product_identifiers = state.get("product_identifiers", [])
    
    if not product_identifiers:
        state["error_message"] = "No products identified for comparison"
        state["products"] = []
        return state
    
    if len(product_identifiers) < 2:
        state["error_message"] = "Need at least 2 products to compare"
        state["products"] = []
        return state
    
    if len(product_identifiers) > 5:
        state["error_message"] = "Cannot compare more than 5 products at once"
        state["products"] = []
        return state
    
    fetched_products = []
    
    try:
        for identifier in product_identifiers:
            product_name = identifier.get("name", "")
            brand = identifier.get("brand", "")
            
            # Search for product by name and brand
            search_query = f"{brand} {product_name}".strip() if brand else product_name
            
            # Use the product service to search for products
            results = await product_service.search_products_fts(
                search_params={"keywords": search_query},
                limit=1
            )
            
            if results and len(results) > 0:
                fetched_products.append(results[0])
        
        state["products"] = fetched_products
        state["result_count"] = len(fetched_products)
        
        # Check if we have enough products
        if len(fetched_products) < 2:
            state["error_message"] = f"Could only find {len(fetched_products)} product(s). Need at least 2 products to compare."
        elif len(fetched_products) < len(product_identifiers):
            print(f"Warning: Could only find {len(fetched_products)} out of {len(product_identifiers)} requested products")
        
    except Exception as e:
        print(f"Error fetching products for comparison: {e}")
        state["error_message"] = f"Failed to fetch product details: {str(e)}"
        state["products"] = []
    
    return state

