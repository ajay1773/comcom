"""Widget Event System for decoupled UI component streaming."""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class WidgetEventType(str, Enum):
    """Enumeration of all widget event types."""
    PRODUCT_SEARCH_RESULTS = "product_search_results"
    CART_DETAILS = "cart_details"
    USER_PROFILE_DETAILS = "user_profile_details"
    USER_ADDRESSES = "user_addresses"
    CHECKOUT_FORM = "checkout_form"
    ADDRESS_SELECTION = "address_selection"
    
    SIGNUP_FORM = "signup_form"
    SIGNIN_FORM = "signin_form"
    SIGNUP_SUCCESS = "signup_success"
    SIGNUP_FAILURE = "signup_failure"


    SIGNIN_SUCCESS = "signin_success"
    SIGNIN_FAILURE = "signin_failure"
    ADD_TO_CART_SUCCESS = "add_to_cart_success"
    DELETE_FROM_CART_SUCCESS = "delete_from_cart_success"
    ORDER_CONFIRMATION = "order_confirmation"
    PAYMENT_STATUS = "payment_status"
    ERROR_MESSAGE = "error_message"
    SUCCESS_MESSAGE = "success_message"

    DELETE_FROM_CART_FAILURE = "delete_from_cart_failure"
    ADD_TO_CART_FAILURE = "add_to_cart_failure"
    VIEW_CART_FAILURE = "view_cart_failure"
    VIEW_CART_SUCCESS = "view_cart_success"

    ADD_ADDRESS_SUCCESS = "add_address_success"
    ADD_ADDRESS_FAILURE = "add_address_failure"
    DELETE_ADDRESS_SUCCESS = "delete_address_success"
    DELETE_ADDRESS_FAILURE = "delete_address_failure"
    EDIT_ADDRESS_SUCCESS = "edit_address_success"
    EDIT_ADDRESS_FAILURE = "edit_address_failure"
    USER_ADDRESSES_FETCH_FAILURE = "user_addresses_fetch_failure"
    USER_ADDRESSES_FETCH_SUCCESS = "user_addresses_fetch_success"

    CHECKOUT_UI_PROVIDER_DATA = "checkout_ui_provider_data"
    ORDER_VIEW_SUCCESS = "order_view_success"
    ORDER_VIEW_FAILURE = "order_view_failure"


@dataclass
class WidgetEvent:
    """Base widget event structure."""
    event_type: Union[WidgetEventType, str]
    payload: Dict[str, Any]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        event_type_value = self.event_type.value if isinstance(self.event_type, WidgetEventType) else str(self.event_type)
        return {
            "event_type": event_type_value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {}
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class WidgetEventEmitter:
    """Centralized widget event emitter for workflows."""
    
    def __init__(self):
        self._events: List[WidgetEvent] = []
        self._listeners: Dict[str, List] = {}
    
    def emit(
        self, 
        event_type: Union[WidgetEventType, str], 
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> WidgetEvent:
        """
        Emit a widget event.
        
        Args:
            event_type: Type of widget event
            payload: Event payload data
            metadata: Optional metadata
            
        Returns:
            The created widget event
        """
        # Convert string to enum if possible, otherwise keep as string for extensibility
        if isinstance(event_type, str):
            try:
                event_type = WidgetEventType(event_type)
            except ValueError:
                logger.warning(f"Unknown widget event type: {event_type}")
                # Keep as string for extensibility
        
        event = WidgetEvent(
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        self._events.append(event)
        
        # Notify listeners
        event_key = event_type.value if isinstance(event_type, WidgetEventType) else str(event_type)
        for listener in self._listeners.get(event_key, []):
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in widget event listener: {e}")
        
        logger.debug(f"Emitted widget event: {event_type}")
        return event
    
    def get_events(self) -> List[WidgetEvent]:
        """Get all emitted events."""
        return self._events.copy()
    
    def get_latest_event(self) -> Optional[WidgetEvent]:
        """Get the most recently emitted event."""
        return self._events[-1] if self._events else None
    
    def clear_events(self):
        """Clear all events."""
        self._events.clear()
    
    def add_listener(self, event_type: Union[WidgetEventType, str], listener):
        """Add an event listener."""
        event_key = event_type.value if isinstance(event_type, WidgetEventType) else str(event_type)
        if event_key not in self._listeners:
            self._listeners[event_key] = []
        self._listeners[event_key].append(listener)


# Global widget event emitter instance
widget_event_emitter = WidgetEventEmitter()


# Convenience functions for common widget events
def emit_product_search_results(
    products: List[Dict[str, Any]], 
    search_parameters: Dict[str, Any],
    result_count: int,
    success_message: Optional[str] = None
) -> WidgetEvent:
    """Emit product search results widget event."""
    return widget_event_emitter.emit(
        WidgetEventType.PRODUCT_SEARCH_RESULTS,
        {
            "products": products,
            "search_parameters": search_parameters,
            "result_count": result_count,
            "success_message": success_message,
            "suggested_actions": [
                "Refine search",
                "Add to cart",
                "View details",
                "Compare products"
            ]
        }
    )


def emit_cart_details(
    cart_items: List[Dict[str, Any]],
    cart_summary: Dict[str, Any],
    success_message: Optional[str] = None
) -> WidgetEvent:
    """Emit cart details widget event."""
    return widget_event_emitter.emit(
        WidgetEventType.CART_DETAILS,
        {
            "cart_details": cart_items,
            "cart_summary": cart_summary,
            "success_message": success_message,
            "suggested_actions": [
                "Continue shopping",
                "Proceed to checkout",
                "Remove items" if cart_items else None,
                "Add more items" if cart_items else "Browse products"
            ]
        }
    )


def emit_user_profile_details(
    user_details: Dict[str, Any],
    user_orders: List[Dict[str, Any]],
    user_addresses: List[Dict[str, Any]],
    success_message: Optional[str] = None
) -> WidgetEvent:
    """Emit user profile details widget event."""
    return widget_event_emitter.emit(
        WidgetEventType.USER_PROFILE_DETAILS,
        {
            "user_details": user_details,
            "user_orders": user_orders,
            "user_addresses": user_addresses,
            "profile_summary": {
                "total_orders": len(user_orders),
                "total_addresses": len(user_addresses),
                "account_status": "Active" if user_details and user_details.get("is_active") else "Inactive"
            },
            "success_message": success_message,
            "suggested_actions": [
                "Update profile information",
                "View order history",
                "Manage addresses",
                "Continue shopping"
            ]
        }
    )


def emit_user_addresses(
    addresses: List[Dict[str, Any]],
    success_message: Optional[str] = None
) -> WidgetEvent:
    """Emit user addresses widget event."""
    return widget_event_emitter.emit(
        WidgetEventType.USER_ADDRESSES,
        {
            "addresses": addresses,
            "address_summary": {
                "total_addresses": len(addresses),
                "has_default": any(addr.get("is_default", False) for addr in addresses)
            },
            "success_message": success_message,
            "suggested_actions": [
                "Add new address",
                "Edit address",
                "Delete address",
                "Set as default"
            ]
        }
    )


def emit_checkout_form(
    cart_items: List[Dict[str, Any]],
    available_addresses: List[Dict[str, Any]],
    cart_summary: Dict[str, Any],
    success_message: Optional[str] = None
) -> WidgetEvent:
    """Emit checkout form widget event."""
    return widget_event_emitter.emit(
        WidgetEventType.CHECKOUT_FORM,
        {
            "cart_items": cart_items,
            "available_addresses": available_addresses,
            "cart_summary": cart_summary,
            "success_message": success_message,
            "suggested_actions": [
                "Select address",
                "Add new address",
                "Continue to payment",
                "Back to cart"
            ]
        }
    )


def emit_success_message(
    message: str,
    action_type: Optional[str] = None,
    suggested_actions: Optional[List[str]] = None
) -> WidgetEvent:
    """Emit a generic success message widget event."""
    return widget_event_emitter.emit(
        WidgetEventType.SUCCESS_MESSAGE,
        {
            "message": message,
            "action_type": action_type,
            "suggested_actions": suggested_actions or []
        }
    )


def emit_error_message(
    message: str,
    error_type: Optional[str] = None,
    suggested_actions: Optional[List[str]] = None
) -> WidgetEvent:
    """Emit an error message widget event."""
    return widget_event_emitter.emit(
        WidgetEventType.ERROR_MESSAGE,
        {
            "message": message,
            "error_type": error_type,
            "suggested_actions": suggested_actions or ["Try again", "Contact support"]
        }
    )


def emit_order_view_success(
    view_type: str,
    orders: Optional[List[Dict[str, Any]]] = None,
    order_details: Optional[Dict[str, Any]] = None,
    total_orders: Optional[int] = None,
    total_spent: Optional[float] = None,
    success_message: Optional[str] = None
) -> WidgetEvent:
    """Emit order view success widget event."""
    payload = {
        "view_type": view_type,
        "success_message": success_message,
        "suggested_actions": [
            "View order details",
            "Track order",
            "Reorder items",
            "Contact support"
        ]
    }
    
    payload.update({
        "orders": orders or [],
        "total_orders": total_orders or 0,
        "total_spent": total_spent or 0.0
    })
    
    return widget_event_emitter.emit(
        WidgetEventType.ORDER_VIEW_SUCCESS,
        payload
    )


def emit_order_view_failure(
    message: str,
    view_type: Optional[str] = None,
    error_type: Optional[str] = None,
    suggested_actions: Optional[List[str]] = None
) -> WidgetEvent:
    """Emit order view failure widget event."""
    default_suggestions = [
        "Try again",
        "Check order number",
        "View all orders",
        "Contact support"
    ]
    
    return widget_event_emitter.emit(
        WidgetEventType.ORDER_VIEW_FAILURE,
        {
            "message": message,
            "view_type": view_type,
            "error_type": error_type,
            "suggested_actions": suggested_actions or default_suggestions
        }
    )
