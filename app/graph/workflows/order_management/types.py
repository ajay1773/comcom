


from typing import Dict, Any, List
from app.types.common import AuthState, CommonState


class AddToCartState(CommonState, AuthState):
    product_details: Dict[str, Any]
    quantity: int
    operation_success: bool
    error_message: str
    cart_details: List[Dict[str, Any]]
