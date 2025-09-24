"""Core enums for the application."""

from enum import Enum
from typing import Literal

TypeWorkflowType = Literal["product_search", "place_order", "initiate_payment", "payment_status", "support_query", "fallback", "generate_signin_form", "login_with_credentials", "generate_signup_form", "signup_with_details", "auth_middleware", "add_to_cart", "view_cart", "user_profile", "user_addresses", "add_address_form", "edit_address", "delete_address"]
TypeNodeName = Literal["classifier_node", "orchestrator_node", "output_handler", "error_handler", "product_search_workflow", "place_order_workflow", "initiate_payment_workflow", "payment_status_workflow", "fallback_workflow", "generate_signin_form_workflow", "login_with_credentials_workflow", "generate_signup_form_workflow", "signup_with_details_workflow", "auth_middleware_workflow", "auth_protected_product_search_workflow", "auth_protected_place_order_workflow", "extract_params", "product_lookup", "extract_product_details", "get_selected_product", "prepare_order_details", "generate_payment", "make_payment", "handle_fallback", "send_login_form", "extract_login_credentials", "login_with_credentials", "parse_token", "handle_valid_token", "handle_invalid_token", "add_to_cart_workflow", "view_cart_workflow", "handle_success", "handle_failure", "get_cart_details", "handle_view_cart_success", "handle_view_cart_fail", "extract_address_details", "save_address_details", "handle_address_save_success", "handle_address_save_failure", "auth_protected_add_address_form_workflow", "auth_protected_edit_address_workflow", "auth_protected_delete_address_workflow"]
TypeTemplateType = Literal["send_login_form", "login_with_credentials", "send_signup_form", "signup_with_details", "product_search_results", "order_confirmation", "order_details", "initiate_payment", "payment_form", "payment_status_details", "payment_success", "payment_failed", "error_message", "fallback_response", "auth_success", "auth_error", "send_add_address_form"]
TypeIntentType = Literal["product_search", "place_order", "initiate_payment", "payment_status", "support_query", "generate_signin_form", "login_with_credentials", "fallback", "generate_signup_form", "signup_with_details","auth_middleware", "add_to_cart", "view_cart", "user_profile", "user_addresses", "add_address_form", "edit_address", "delete_address"]
TypeWorkflowStateKey = Literal["user_message", "intent", "conversation_history", "user_profile", "response", "user_id", "session_token", "is_authenticated", "auth_required", "pending_workflow", "thread_id", "current_workflow", "workflow_states", "workflow_history", "confidence", "disfluent_message", "workflow_output_text", "workflow_output_json", "workflow_error", "error_recovery_options"]
TypeError = Literal["validation_error", "authentication_error", "network_error", "database_error", "workflow_error", "unknown_error"]
TypeDatabaseTable = Literal["users", "products", "orders", "order_items", "payments", "sessions"]
TypeProductCategory = Literal["electronics", "clothing", "books", "home", "sports", "beauty", "toys", "automotive"]
TypePaymentStatus = Literal["pending", "processing", "completed", "failed", "cancelled", "refunded"]
TypeOrderStatus = Literal["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "returned"]


class WorkflowType(str, Enum):
    """Enum for workflow types."""
    
    PRODUCT_SEARCH = "product_search"
    PLACE_ORDER = "place_order"
    INITIATE_PAYMENT = "initiate_payment"
    PAYMENT_STATUS = "payment_status"
    SUPPORT_QUERY = "support_query"
    FALLBACK = "fallback"
    GENERATE_SIGNIN_FORM = "generate_signin_form"
    LOGIN_WITH_CREDENTIALS = "login_with_credentials"
    GENERATE_SIGNUP_FORM = "generate_signup_form"
    SIGNUP_WITH_DETAILS = "signup_with_details"
    AUTH_MIDDLEWARE = "auth_middleware"
    ADD_TO_CART = "add_to_cart"
    VIEW_CART = "view_cart"
    USER_PROFILE = "user_profile"
    USER_ADDRESSES = "user_addresses"
    ADD_ADDRESS_FORM = "add_address_form"
    EDIT_ADDRESS = "edit_address"
    DELETE_ADDRESS = "delete_address"

class NodeName(str, Enum):
    """Enum for node names."""
    
    # Core nodes
    CLASSIFIER_NODE = "classifier_node"
    ORCHESTRATOR_NODE = "orchestrator_node"
    OUTPUT_HANDLER = "output_handler"
    ERROR_HANDLER = "error_handler"
    
    # Workflow nodes
    PRODUCT_SEARCH_WORKFLOW = "product_search_workflow"
    PLACE_ORDER_WORKFLOW = "place_order_workflow"
    INITIATE_PAYMENT_WORKFLOW = "initiate_payment_workflow"
    PAYMENT_STATUS_WORKFLOW = "payment_status_workflow"
    FALLBACK_WORKFLOW = "fallback_workflow"
    GENERATE_SIGNIN_FORM_WORKFLOW = "generate_signin_form_workflow"
    LOGIN_WITH_CREDENTIALS_WORKFLOW = "login_with_credentials_workflow"
    GENERATE_SIGNUP_FORM_WORKFLOW = "generate_signup_form_workflow"
    SIGNUP_WITH_DETAILS_WORKFLOW = "signup_with_details_workflow"
    AUTH_MIDDLEWARE_WORKFLOW = "auth_middleware_workflow"
    ADD_TO_CART_WORKFLOW = "add_to_cart_workflow"
    VIEW_CART_WORKFLOW = "view_cart_workflow"
    # Auth-protected workflow nodes
    AUTH_PROTECTED_PRODUCT_SEARCH_WORKFLOW = "auth_protected_product_search_workflow"
    AUTH_PROTECTED_PLACE_ORDER_WORKFLOW = "auth_protected_place_order_workflow"
    AUTH_PROTECTED_ADD_TO_CART_WORKFLOW = "auth_protected_add_to_cart_workflow"
    AUTH_PROTECTED_VIEW_CART_WORKFLOW = "auth_protected_view_cart_workflow"
    AUTH_PROTECTED_USER_PROFILE_WORKFLOW = "auth_protected_user_profile_workflow"
    AUTH_PROTECTED_USER_ADDRESSES_WORKFLOW = "auth_protected_user_addresses_workflow"
    AUTH_PROTECTED_ADD_ADDRESS_FORM_WORKFLOW = "auth_protected_add_address_form_workflow"
    AUTH_PROTECTED_EDIT_ADDRESS_WORKFLOW = "auth_protected_edit_address_workflow"
    AUTH_PROTECTED_DELETE_ADDRESS_WORKFLOW = "auth_protected_delete_address_workflow"
    # Product search nodes
    EXTRACT_PARAMS = "extract_params"
    PRODUCT_LOOKUP = "product_lookup"
    
    # Place order nodes
    EXTRACT_PRODUCT_DETAILS = "extract_product_details"
    GET_SELECTED_PRODUCT = "get_selected_product"
    PREPARE_ORDER_DETAILS = "prepare_order_details"
    
    # Payment nodes
    GENERATE_PAYMENT = "generate_payment"
    MAKE_PAYMENT = "make_payment"
    
    # Fallback nodes
    HANDLE_FALLBACK = "handle_fallback"
    
    # Signin nodes
    SEND_LOGIN_FORM = "send_login_form"
    EXTRACT_LOGIN_CREDENTIALS = "extract_login_credentials"
    LOGIN_WITH_CREDENTIALS = "login_with_credentials"

    # Signup nodes
    SEND_SIGNUP_FORM = "send_signup_form"
    EXTRACT_SIGNUP_DETAILS = "extract_signup_details"
    SAVE_USER_DETAILS = "save_user_details"
    HANDLE_NO_USER_EXISTS = "handle_no_user_exists"
    
    # Auth middleware nodes
    PARSE_TOKEN = "parse_token"
    HANDLE_VALID_TOKEN = "handle_valid_token"
    HANDLE_INVALID_TOKEN = "handle_invalid_token"

    # Add to cart nodes
    EXTRACT_PRODUCT_DETAILS_FROM_PROMPT = "extract_product_details_from_prompt_node"
    GET_PRODUCT_FROM_DB = "get_product_from_db"
    ADD_PRODUCT_TO_CART = "add_product_to_cart"
    HANDLE_SUCCESS = "handle_success"
    HANDLE_FAILURE = "handle_failure"

    # View cart nodes
    GET_CART_DETAILS = "get_cart_details"
    HANDLE_VIEW_CART_SUCCESS = "handle_view_cart_success"
    HANDLE_VIEW_CART_FAIL = "handle_view_cart_fail"
    
    # User profile nodes
    GET_USER_DETAILS = "get_user_details"
    HANDLE_USER_DETAILS_FETCH_SUCCESS = "handle_user_details_fetch_success"
    HANDLE_USER_DETAILS_FETCH_FAILURE = "handle_user_details_fetch_failure"
    
    # User addresses nodes
    GET_USER_ADDRESSES = "get_user_addresses"
    HANDLE_ADDRESSES_FETCH_SUCCESS = "handle_addresses_fetch_success"
    HANDLE_ADDRESSES_FETCH_FAILURE = "handle_addresses_fetch_failure"
    
    # Add address nodes
    EXTRACT_ADDRESS_DETAILS = "extract_address_details"
    SAVE_ADDRESS_DETAILS = "save_address_details"
    HANDLE_ADDRESS_SAVE_SUCCESS = "handle_address_save_success"
    HANDLE_ADDRESS_SAVE_FAILURE = "handle_address_save_failure"
    
    # Edit address nodes
    EXTRACT_EDIT_DETAILS = "extract_edit_details"
    VALIDATE_ADDRESS_OWNERSHIP = "validate_address_ownership"
    UPDATE_ADDRESS_DETAILS = "update_address_details"
    HANDLE_ADDRESS_EDIT_SUCCESS = "handle_address_edit_success"
    HANDLE_ADDRESS_EDIT_FAILURE = "handle_address_edit_failure"
    
    # Delete address nodes
    EXTRACT_ADDRESS_ID = "extract_address_id"
    VALIDATE_DELETE_PERMISSIONS = "validate_delete_permissions"
    DELETE_ADDRESS = "delete_address"
    HANDLE_ADDRESS_DELETE_SUCCESS = "handle_address_delete_success"
    HANDLE_ADDRESS_DELETE_FAILURE = "handle_address_delete_failure"
    
class TemplateType(str, Enum):
    """Enum for template types."""
    
    SEND_LOGIN_FORM = "send_login_form"
    LOGIN_WITH_CREDENTIALS = "login_with_credentials"
    SEND_SIGNUP_FORM = "send_signup_form"
    SIGNUP_WITH_DETAILS = "signup_with_details"
    PRODUCT_SEARCH_RESULTS = "product_search_results"
    ORDER_CONFIRMATION = "order_confirmation"
    ORDER_DETAILS = "order_details"
    INITIATE_PAYMENT = "initiate_payment"
    PAYMENT_FORM = "payment_form"
    PAYMENT_STATUS_DETAILS = "payment_status_details"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    ERROR_MESSAGE = "error_message"
    FALLBACK_RESPONSE = "fallback_response"
    AUTH_SUCCESS = "auth_success"
    AUTH_ERROR = "auth_error"
    SEND_ADD_ADDRESS_FORM = "send_add_address_form"


class IntentType(str, Enum):
    """Enum for intent types."""
    
    PRODUCT_SEARCH = "product_search"
    PLACE_ORDER = "place_order"
    INITIATE_PAYMENT = "initiate_payment"
    PAYMENT_STATUS = "payment_status"
    SUPPORT_QUERY = "support_query"
    GENERATE_SIGNIN_FORM = "generate_signin_form"
    LOGIN_WITH_CREDENTIALS = "login_with_credentials"
    FALLBACK = "fallback"
    VIEW_CART = "view_cart"
    USER_PROFILE = "user_profile"
    USER_ADDRESSES = "user_addresses"
    ADD_ADDRESS_FORM = "add_address_form"
    EDIT_ADDRESS = "edit_address"
    DELETE_ADDRESS = "delete_address"


class WorkflowStateKey(str, Enum):
    """Enum for workflow state keys."""
    
    # Core state keys
    USER_MESSAGE = "user_message"
    INTENT = "intent"
    CONVERSATION_HISTORY = "conversation_history"
    USER_PROFILE = "user_profile"
    RESPONSE = "response"
    
    # Authentication state keys
    USER_ID = "user_id"
    SESSION_TOKEN = "session_token"
    IS_AUTHENTICATED = "is_authenticated"
    AUTH_REQUIRED = "auth_required"
    PENDING_WORKFLOW = "pending_workflow"
    THREAD_ID = "thread_id"
    
    # Workflow management keys
    CURRENT_WORKFLOW = "current_workflow"
    WORKFLOW_STATES = "workflow_states"
    WORKFLOW_HISTORY = "workflow_history"
    CONFIDENCE = "confidence"
    
    # Output keys
    WORKFLOW_OUTPUT_TEXT = "workflow_output_text"
    WORKFLOW_OUTPUT_JSON = "workflow_output_json"
            
    # Error handling keys
    WORKFLOW_ERROR = "workflow_error"
    ERROR_RECOVERY_OPTIONS = "error_recovery_options"


class ErrorType(str, Enum):
    """Enum for error types."""
    
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    WORKFLOW_ERROR = "workflow_error"
    UNKNOWN_ERROR = "unknown_error"


class DatabaseTable(str, Enum):
    """Enum for database table names."""
    
    USERS = "users"
    PRODUCTS = "products"
    ORDERS = "orders"
    ORDER_ITEMS = "order_items"
    PAYMENTS = "payments"
    SESSIONS = "sessions"


class ProductCategory(str, Enum):
    """Enum for product categories."""
    
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME = "home"
    SPORTS = "sports"
    BEAUTY = "beauty"
    TOYS = "toys"
    AUTOMOTIVE = "automotive"


class PaymentStatus(str, Enum):
    """Enum for payment status."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderStatus(str, Enum):
    """Enum for order status."""
    
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
