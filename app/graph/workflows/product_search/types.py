
from typing import Any, Dict, List, TypedDict


class Product(TypedDict):
    id: int
    name: str
    gender: str
    category: str
    min_price: float
    max_price: float
    color: str
    brand: str
    material: str
    style: str
    pattern: str
    images: str
    available_sizes: List[str]
    unit: str
    
class ProductSearchState(TypedDict):
    search_query: str
    search_parameters: Dict[str, Any]
    search_results: List[Product]
    suggestions: List[str]
    result_count: int
    workflow_widget_json: Dict[str, Any]

