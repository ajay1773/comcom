"""Get user details from database including user info, orders, and addresses."""

from app.graph.workflows.user_management.types import UserProfileState
from app.services.db.user import user_service
from app.services.db.db import db_service
from app.services.db.order import order_service
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
        user_addresses = await user_service.get_user_addresses(user_id)
        user_orders = await order_service.get_user_orders_with_order_items(user_id)
        user_orders = order_service.format_order_items(user_orders)
        if not user_details:
            state["error_message"] = "User not found"
            state["profile_fetch_success"] = False
            return state
        
        # Get user orders
        # user_orders_result = await db_service.execute_query(
        #     """
        #     SELECT o.id, o.product_id, o.quantity, o.price, o.status, o.created_at, o.updated_at,
        #            p.name as product_name, p.category, p.brand, p.color, p.images
        #     FROM orders o
        #     LEFT JOIN products p ON o.product_id = p.id
        #     WHERE o.user_id = ?
        #     ORDER BY o.created_at DESC
        #     """,
        #     (user_id,)
        # )
        
        # # Convert orders to dictionaries
        # user_orders = []
        # if user_orders_result:
        #     for row in user_orders_result:
        #         order_dict = {
        #             "id": row[0],
        #             "product_id": row[1],
        #             "quantity": row[2],
        #             "price": row[3],
        #             "status": row[4],
        #             "created_at": row[5],
        #             "updated_at": row[6],
        #             "product_name": row[7],
        #             "category": row[8],
        #             "brand": row[9],
        #             "color": row[10],
        #             "images": row[11]
        #         }
        #         user_orders.append(order_dict)
        
        
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
        state["user_orders"] = user_orders
        state["user_addresses"] = user_addresses
    
    return state
