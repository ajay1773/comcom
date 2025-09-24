from typing import Dict, Any, List
from app.types.common import AuthState, CommonState
from app.models.user import User, UserAddress


class UserProfileState(CommonState, AuthState):
    """State for user profile management workflow."""
    user_details: User | None
    user_orders: List[Dict[str, Any]]
    user_addresses: List[UserAddress]
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None
    profile_fetch_success: bool


class UserAddressesState(CommonState, AuthState):
    """State for user addresses management workflow."""
    user_addresses: List[UserAddress]
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None
    addresses_fetch_success: bool


class AddAddressState(CommonState, AuthState):
    """State for add address workflow."""
    extracted_address: Dict[str, Any] | None
    address_save_success: bool
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None


class EditAddressState(CommonState, AuthState):
    """State for edit address workflow."""
    address_id: int | None
    extracted_address: Dict[str, Any] | None
    existing_address: Dict[str, Any] | None
    address_edit_success: bool
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None


class DeleteAddressState(CommonState, AuthState):
    """State for delete address workflow."""
    address_id: int | None
    user: User | None
    existing_address: Dict[str, Any] | None
    address_delete_success: bool
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None
