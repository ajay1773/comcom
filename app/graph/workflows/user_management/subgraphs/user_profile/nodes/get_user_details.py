"""Get user details from database including user info, orders, and addresses."""

from app.graph.workflows.user_management.types import UserProfileState
from app.services.db.user import user_service
from app.services.db.db import db_service
from app.models.user import UserAddress


async def get_user_details_node(state: UserProfileState) -> UserProfileState:
    """Fetch comprehensive user details from all relevant tables."""
    
    try:
        user_id = state.get("user_id")
        if not user_id:
            state["error_message"] = "User ID not found in state"
            state["profile_fetch_success"] = False
            return state
        
        # Get user basic details
        user_details = await user_service.get_user_by_id(user_id)
        if not user_details:
            state["error_message"] = "User not found"
            state["profile_fetch_success"] = False
            return state
        
        # Get user orders
        user_orders_result = await db_service.execute_query(
            """
            SELECT o.id, o.product_id, o.quantity, o.price, o.status, o.created_at, o.updated_at,
                   p.name as product_name, p.category, p.brand, p.color, p.images
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
            """,
            (user_id,)
        )
        
        # Convert orders to dictionaries
        user_orders = []
        if user_orders_result:
            for row in user_orders_result:
                order_dict = {
                    "id": row[0],
                    "product_id": row[1],
                    "quantity": row[2],
                    "price": row[3],
                    "status": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "product_name": row[7],
                    "category": row[8],
                    "brand": row[9],
                    "color": row[10],
                    "images": row[11]
                }
                user_orders.append(order_dict)
        
        # Get user addresses
        user_addresses_result = await db_service.execute_query(
            """
            SELECT id, user_id, type, street, city, state, zip_code, country, is_default, created_at
            FROM user_addresses
            WHERE user_id = ?
            ORDER BY is_default DESC, created_at DESC
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
        
        # Update state with fetched data
        state["user_details"] = user_details
        state["user_orders"] = user_orders
        state["user_addresses"] = user_addresses
        state["profile_fetch_success"] = True
        state["error_message"] = None
        
    except Exception as e:
        print(f"Error in get_user_details_node: {e}")
        state["error_message"] = f"Failed to fetch user details: {str(e)}"
        state["profile_fetch_success"] = False
        state["user_details"] = None
        state["user_orders"] = []
        state["user_addresses"] = []
    
    return state
