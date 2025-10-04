
from typing import Any, Dict, List, TypedDict
from app.types.common import CommonState, AuthState


class Product(TypedDict):
    id: int
    title: str
    description: str
    category: str
    price: float
    discount_percentage: float
    rating: float
    stock: int
    tags: List[str]
    brand: str
    sku: str
    weight: float
    dimensions: Dict[str, float]
    warranty_information: str
    shipping_information: str
    availability_status: str
    return_policy: str
    minimum_order_quantity: int
    thumbnail: str
    images: List[str]
    barcode: str
    qr_code: str
    available_sizes: List[str]
    unit: str
    color: str | None
    
class ProductSearchState(CommonState, AuthState):
    search_parameters: Dict[str, Any]
    search_results: List[Product]
    result_count: int
    # search_query, suggestions, thread_id, conversation_history inherited from CommonState
    # user_id, session_token, is_authenticated, auth_required inherited from AuthState


