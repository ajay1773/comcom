"""Type definitions for product bundle search workflow."""

from typing import TypedDict, List, Dict, Any, Optional
from app.types.common import CommonState


class BundleItem(TypedDict):
    """Represents a single item in the bundle."""
    category: str  # e.g., "cricket bat", "cricket ball"
    purpose: str  # e.g., "batting", "bowling"
    keywords: str  # search keywords for this item
    priority: int  # 1 (essential), 2 (recommended), 3 (optional)
    quantity: int  # suggested quantity


class ProductBundleSearchState(CommonState):
    """State for product bundle search workflow."""

    # Input from user
    use_case: str  # "play cricket", "camping trip", "home gym"
    budget_total: Optional[float]  # total budget for bundle
    bundle_query: str  # query for the bundle

    # Extracted bundle structure
    bundle_items: List[BundleItem]  # list of items to search for
    bundle_title: str  # "Cricket Starter Kit"
    bundle_description: str  # "Everything you need to start playing cricket"

    # Search results per item
    bundle_results: Dict[str, List[Any]]  # category -> products
    result_count: int

    # Display output
    formatted_output: str
    widget_json: Optional[Dict[str, Any]]

