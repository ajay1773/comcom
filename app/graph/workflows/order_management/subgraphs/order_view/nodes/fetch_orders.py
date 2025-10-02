from app.graph.workflows.order_management.types import OrderViewState
from langchain_core.runnables import RunnableConfig
from app.services.db.order import order_service

async def fetch_orders_node(state: OrderViewState, config: RunnableConfig | None = None) -> OrderViewState:
    """Fetch orders based on the view type and parameters."""
    
    try:
        user_id = state.get("user_id")
        view_type = state.get("view_type")
        order_id = state.get("order_id")
        order_number = state.get("order_number")
        
        # Validate user authentication
        if not user_id:
            state["error_message"] = "User authentication required to view orders"
            state["view_success"] = False
            return state
        
        if view_type == "all_orders":
            # Fetch all orders for the user
            orders = await order_service.get_user_orders_with_order_items(user_id)
            
            if not orders:
                state["orders"] = []
                state["workflow_output_text"] = "You haven't placed any orders yet."
                state["view_success"] = True
                return state
            
            # Group orders and their items (since LEFT JOIN returns multiple rows per order)
            # Column mapping based on the SELECT query:
            # 0: order_id, 1: order_number, 2: order_status, 3: amount, 4: total_items, 5: currency,
            # 6: payment_status, 7: payment_method, 8: shipping_address_id, 9: notes,
            # 10: order_created_at, 11: order_updated_at, 12: item_id, 13: product_id,
            # 14: item_name, 15: item_brand, 16: quantity, 17: unit_price, 18: total_price,
            # 19: size, 20: color, 21: item_status, 22: discount_amount, 23: item_created_at, 24: item_updated_at
                order_id = row[0]  # order_id  # type: ignore
                
                if order_id not in orders_dict:
                    # Create new order entry
                    orders_dict[order_id] = {
                        "id": row[0],           # order_id  # type: ignore
                        "order_number": row[1], # order_number  # type: ignore
                        "status": row[2],       # order_status  # type: ignore
                        "amount": row[3],       # amount  # type: ignore
                        "currency": row[5],     # currency  # type: ignore
                        "total_items": row[4],  # total_items  # type: ignore
                        "payment_status": row[6], # payment_status  # type: ignore
                        "payment_method": row[7], # payment_method  # type: ignore
                        "shipping_address_id": row[8], # shipping_address_id  # type: ignore
                        "notes": row[9],        # notes  # type: ignore
                        "created_at": row[10],  # order_created_at  # type: ignore
                        "updated_at": row[11],  # order_updated_at  # type: ignore
                        "items": []
                    }
                
                # Add order item if it exists (LEFT JOIN might have NULL values)
                if row[12] is not None:  # item_id exists  # type: ignore
                    item = {
                        "id": row[12],          # item_id  # type: ignore
                        "product_id": row[13],  # product_id  # type: ignore
                        "name": row[14],        # item_name  # type: ignore
                        "brand": row[15],       # item_brand  # type: ignore
                        "size": row[19],        # size  # type: ignore
                        "color": row[20],       # color  # type: ignore
                        "quantity": row[16],    # quantity  # type: ignore
                        "unit_price": row[17],  # unit_price  # type: ignore
                        "total_price": row[18], # total_price  # type: ignore
                        "status": row[21] if row[21] is not None else "confirmed", # item_status  # type: ignore
                        "discount_amount": row[22] if row[22] is not None else 0.0  # discount_amount  # type: ignore
                    }
                    orders_dict[order_id]["items"].append(item)
            
            # Convert to list and sort by created_at (most recent first)
            formatted_orders = order_service.format_order_items(orders)
            formatted_orders.sort(key=lambda x: x["created_at"], reverse=True)  # type: ignore
            
            state["orders"] = formatted_orders
            state["view_success"] = True
            
            print(f"Fetched {len(formatted_orders)} orders for user {user_id}")
            
        elif view_type == "single_order":
            # Fetch single order
            order_details = None
            
            if order_id:
                # Fetch by order ID
                order_details = await order_service.get_order_by_id(order_id)
            elif order_number:
                # For order number, we need to get all user orders and find the matching one
                user_orders = await order_service.get_user_orders(user_id)
                for order in user_orders:
                    if order["order_number"] == order_number:
                        order_details = await order_service.get_order_by_id(order["id"])
                        break
            
            if not order_details:
                state["error_message"] = f"Order not found or you don't have permission to view it"
                state["view_success"] = False
                return state
            
            # Verify the order belongs to the authenticated user
            if order_details["user_id"] != user_id:
                state["error_message"] = "You don't have permission to view this order"
                state["view_success"] = False
                return state
            
            state["order_details"] = order_details
            state["view_success"] = True
            
            print(f"Fetched order details for order {order_details['order_number']}")
            
        else:
            state["error_message"] = f"Invalid view type: {view_type}"
            state["view_success"] = False
            return state
        
        return state
        
    except Exception as e:
        print(f"Error fetching orders: {e}")
        state["error_message"] = f"Failed to fetch orders: {str(e)}"
        state["view_success"] = False
        return state
