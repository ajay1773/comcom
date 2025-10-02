from app.services.db.db import db_service
from typing import List, Dict, Any
import uuid
from datetime import datetime

class OrderService:
    def __init__(self):
        self.db_service = db_service

    def generate_order_number(self) -> str:
        """Generate a unique order number."""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"

    async def create_order(self, user_id: int, cart_items: List[Dict[str, Any]], 
                          shipping_address_id: int | None = None, payment_method: str | None = None, 
                          notes: str | None = None) -> Dict[str, Any]:
        """Create a new order from cart items."""
        
        # Calculate totals
        total_amount = sum(item['total_price'] for item in cart_items)
        total_items = sum(item['quantity'] for item in cart_items)
        order_number = self.generate_order_number()
        
        # Create order
        order_query = """
        INSERT INTO orders (user_id, order_number, amount, total_items, shipping_address_id, 
                           payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        await self.db_service.execute_query(
            order_query, 
            (user_id, order_number, total_amount, total_items, shipping_address_id, 
             payment_method, notes)
        )
        
        # Get the order ID by querying for the order number
        order_id_query = "SELECT id FROM orders WHERE order_number = ?"
        order_id_result = await self.db_service.execute_query(order_id_query, (order_number,))
        
        if not order_id_result:
            raise Exception("Failed to create order")
        
        order_id = order_id_result[0][0]
        
        # Create order items
        for item in cart_items:
            item_query = """
            INSERT INTO order_items (order_id, product_id, name, brand, quantity, 
                                   unit_price, total_price, size, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            await self.db_service.execute_query(
                item_query,
                (order_id, item['product_id'], item['name'], item['brand'],
                 item['quantity'], item['unit_price'], item['total_price'],
                 item.get('size'), item.get('color'))
            )
        
        return {
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total_amount,
            "total_items": total_items
        }

    async def get_order_by_id(self, order_id: int) -> Dict[str, Any] | None:
        """Get order details by ID."""
        order_query = """
        SELECT * FROM orders WHERE id = ?
        """
        
        order_result = await self.db_service.execute_query(order_query, (order_id,))
        
        if not order_result:
            return None
        
        order_row = order_result[0]
        
        # Get order items
        items_query = """
        SELECT * FROM order_items WHERE order_id = ? ORDER BY created_at
        """
        
        items_result = await self.db_service.execute_query(items_query, (order_id,))
        
        return {
            "id": order_row[0],
            "user_id": order_row[1],
            "order_number": order_row[2],
            "status": order_row[3],
            "amount": order_row[4],
            "total_items": order_row[5],
            "currency": order_row[6],
            "payment_status": order_row[7],
            "payment_method": order_row[8],
            "shipping_address_id": order_row[9],
            "notes": order_row[10],
            "created_at": order_row[11],
            "updated_at": order_row[12],
            "items": [
                {
                    "id": item[0],
                    "product_id": item[2],
                    "name": item[3],
                    "brand": item[4],
                    "quantity": item[5],
                    "unit_price": item[6],
                    "total_price": item[7],
                    "size": item[8],
                    "color": item[9],
                    "status": item[10],
                    "discount_amount": item[11],
                    "created_at": item[12],
                    "updated_at": item[13]
                }
                for item in items_result
            ] if items_result else []
        }

    async def get_user_orders(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all orders for a user."""
        query = """
        SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC
        """
        
        result = await self.db_service.execute_query(query, (user_id,))
        
        if not result:
            return []
        
        orders = []
        for row in result:
            order_data = {
                "id": row[0],
                "user_id": row[1],
                "order_number": row[2],
                "status": row[3],
                "amount": row[4],
                "total_items": row[5],
                "currency": row[6],
                "payment_status": row[7],
                "payment_method": row[8],
                "shipping_address_id": row[9],
                "notes": row[10],
                "created_at": row[11],
                "updated_at": row[12]
            }
            orders.append(order_data)
        
        return orders

    async def get_user_orders_with_order_items(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all orders for a user with order items."""
        try:
            query = """
                SELECT 
                    orders.id as order_id,
                    orders.order_number,
                    orders.status as order_status,
                    orders.amount,
                    orders.total_items,
                    orders.currency,
                    orders.payment_status,
                    orders.payment_method,
                    orders.shipping_address_id,
                    orders.notes,
                    orders.created_at as order_created_at,
                    orders.updated_at as order_updated_at,
                    order_items.id as item_id,
                    order_items.product_id,
                    order_items.name as item_name,
                    order_items.brand as item_brand,
                    order_items.quantity,
                    order_items.unit_price,
                    order_items.total_price,
                    order_items.size,
                    order_items.color,
                    order_items.status as item_status,
                    order_items.discount_amount,
                    order_items.created_at as item_created_at,
                    order_items.updated_at as item_updated_at
                FROM orders
                LEFT JOIN order_items ON orders.id = order_items.order_id
                WHERE orders.user_id = ?
                ORDER BY orders.created_at DESC
            """
        
            result = await self.db_service.execute_query(query, (user_id,))
            return result
        except Exception as e:
            print(f"Error getting user orders with order items: {e}")
            return []
    
    async def update_order_status(self, order_id: int, status: str) -> bool:
        """Update order status."""
        query = """
        UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """
        
        result = await self.db_service.execute_query(query, (status, order_id))
        return result is not None

    async def update_payment_status(self, order_id: int, payment_status: str) -> bool:
        """Update payment status."""
        query = """
        UPDATE orders SET payment_status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """
        
        result = await self.db_service.execute_query(query, (payment_status, order_id))
        return result is not None

    def format_order_items(self, order_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format order items."""
        orders_dict = {}
        for row in order_items:
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
                
        return list(orders_dict.values())

order_service = OrderService()
