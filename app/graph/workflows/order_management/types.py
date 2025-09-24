


from typing import Dict, Any, List
from app.types.common import AuthState, CommonState
from app.services.db.db import CartItemWithProductDetails


class AddToCartState(CommonState, AuthState):
    product_details: Dict[str, Any]
    quantity: int
    operation_success: bool
    error_message: str
    cart_details: List[CartItemWithProductDetails]

class ViewCartState(CommonState, AuthState):
    cart_details: List[CartItemWithProductDetails] | None
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None
