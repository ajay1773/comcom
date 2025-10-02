


from typing import Dict, Any, List
from app.types.common import AuthState, CommonState
from app.services.db.db import CartItemWithProductDetails
from app.models.user import UserAddress


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


class DeleteFromCartState(CommonState, AuthState):
    product_details: Dict[str, Any]
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None
    cart_delete_success: bool

class CheckoutState(CommonState, AuthState):
    # Routing
    checkout_route: str | None  # "ui_data" or "process_submission"
    
    # Checkout flow data
    checkout_type: str | None  # "cart" or "direct"
    product_details: Dict[str, Any] | None  # For direct purchase
    cart_items: List[Dict[str, Any]] | None  # For cart checkout
    
    # Address selection
    available_addresses: List[UserAddress] | None
    selected_address_id: int | None
    
    # Payment details
    payment_method: str | None
    payment_details: Dict[str, Any] | None
    
    # Order creation
    order_id: int | None
    order_number: str | None
    total_amount: float | None
    
    # Workflow control
    checkout_success: bool
    current_step: str | None  # "address", "payment", "confirmation"
    
    # Standard workflow outputs
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None


class CheckoutUIProviderState(CommonState, AuthState):
    """State for checkout UI data provider subgraph."""
    # Input
    checkout_type: str | None  # "cart" or "direct"
    product_details: Dict[str, Any] | None  # For direct purchase
    
    # Output data for UI
    product_items: List[Dict[str, Any]] | None
    saved_addresses: List[Dict[str, Any]] | None
    allowed_payment_methods: List[str] | None
    total_amount: float | None
    
    # Standard workflow outputs
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None
    ui_data_success: bool


class CheckoutProcessorState(CommonState, AuthState):
    """State for checkout processor subgraph."""
    # Input from user submission
    selected_address_id: int | None
    payment_method: str | None
    payment_details: Dict[str, Any] | None  # Credit card details, etc.
    checkout_type: str | None
    product_details: Dict[str, Any] | None  # For direct purchase
    cart_items: List[Dict[str, Any]] | None  # For cart checkout
    total_amount: float | None
    
    # Order creation results
    order_id: int | None
    order_number: str | None
    checkout_success: bool
    
    # Standard workflow outputs
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None


class OrderViewState(CommonState, AuthState):
    """State for order view workflow."""
    # Input parameters
    view_type: str | None  # "all_orders" or "single_order"
    order_id: int | None  # For single order view
    order_number: str | None  # Alternative to order_id
    
    # Output data
    orders: List[Dict[str, Any]] | None  # For all orders
    order_details: Dict[str, Any] | None  # For single order
    
    # Standard workflow outputs
    workflow_output_text: str | None
    error_message: str | None
    view_success: bool
