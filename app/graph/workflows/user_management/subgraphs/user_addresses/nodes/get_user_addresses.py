"""Get user addresses from database."""

from app.graph.workflows.user_management.types import UserAddressesState
from app.services.db.db import db_service
from app.models.user import UserAddress


async def get_user_addresses_node(state: UserAddressesState) -> UserAddressesState:
    """Fetch user addresses from database."""
    
    try:
        user_id = state.get("user_id")
        if not user_id:
            state["error_message"] = "User ID not found in state"
            state["addresses_fetch_success"] = False
            return state
        
        # Get user addresses from database
        user_addresses_result = await db_service.execute_query(
            """
            SELECT id, user_id, type, street, city, state, zip_code, country, is_default, created_at
            FROM user_addresses
            WHERE user_id = ?
            ORDER BY is_default DESC, type ASC, created_at DESC
            """,
            (user_id,)
        )
        
        # Convert addresses to UserAddress objects
        user_addresses = []
        if user_addresses_result:
            for row in user_addresses_result:
                address = UserAddress(
                    id=row[0],
                    user_id=row[1],
                    type=row[2],
                    street=row[3],
                    city=row[4],
                    state=row[5],
                    zip_code=row[6],
                    country=row[7],
                    is_default=bool(row[8])
                )
                user_addresses.append(address)
        
        # Update state with fetched addresses
        state["user_addresses"] = user_addresses
        state["addresses_fetch_success"] = True
        state["error_message"] = None
        
    except Exception as e:
        print(f"Error in get_user_addresses_node: {e}")
        state["error_message"] = f"Failed to fetch user addresses: {str(e)}"
        state["addresses_fetch_success"] = False
        state["user_addresses"] = []
    
    return state
