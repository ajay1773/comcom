from typing import List, Optional
from app.services.db.db import db_service, UserCart, CartItem, CartItemCreate
from datetime import datetime, timedelta


class CartService:
    """Service for managing user shopping carts."""
    
    def __init__(self):
        self.db_service = db_service
    
    async def get_or_create_cart(self, user_id: int, session_id: Optional[str] = None) -> UserCart:
        """Get existing cart for user or create a new one."""
        # Try to get existing active cart
        result = await self.db_service.execute_query(
            "SELECT id, user_id, total_amount, total_items, currency, status, session_id, expires_at, created_at, updated_at FROM user_carts WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        
        if result:
            row = result[0]
            return UserCart(
                id=row[0],
                user_id=row[1],
                total_amount=row[2],
                total_items=row[3],
                currency=row[4],
                status=row[5],
                session_id=row[6],
                expires_at=row[7],
                created_at=row[8],
                updated_at=row[9]
            )
        
        # Create new cart if none exists
        expires_at = datetime.now() + timedelta(days=30)  # Cart expires in 30 days
        cart_result = await self.db_service.execute_query(
            """INSERT INTO user_carts (user_id, session_id, expires_at) 
               VALUES (?, ?, ?) RETURNING id, user_id, total_amount, total_items, currency, status, session_id, expires_at, created_at, updated_at""",
            (user_id, session_id, expires_at.isoformat())
        )
        
        if cart_result:
            row = cart_result[0]
            return UserCart(
                id=row[0],
                user_id=row[1],
                total_amount=row[2],
                total_items=row[3],
                currency=row[4],
                status=row[5],
                session_id=row[6],
                expires_at=row[7],
                created_at=row[8],
                updated_at=row[9]
            )
        
        raise Exception("Failed to create cart")
    
    async def add_item_to_cart(self, user_id: int, item: CartItemCreate) -> CartItem:
        """Add an item to the user's cart."""
        # Get or create cart
        cart = await self.get_or_create_cart(user_id)
        
        # Calculate total price
        total_price = item.unit_price * item.quantity
        
        # Check if item with same product_id, size, color, and unit already exists
        existing_item = await self.db_service.execute_query(
            """SELECT id, quantity, total_price FROM cart_items 
               WHERE cart_id = ? AND product_id = ? AND 
               (size IS NULL AND ? IS NULL OR size = ?) AND 
               (color IS NULL AND ? IS NULL OR color = ?) AND
               (unit IS NULL AND ? IS NULL OR unit = ?)""",
            (cart.id, item.product_id, item.size, item.size, item.color, item.color, item.unit, item.unit)
        )
        
        if existing_item:
            # Update existing item
            existing_id = existing_item[0][0]
            new_quantity = existing_item[0][1] + item.quantity
            new_total = item.unit_price * new_quantity
            
            await self.db_service.execute_query(
                """UPDATE cart_items SET quantity = ?, total_price = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (new_quantity, new_total, existing_id)
            )
            
            # Get updated item
            updated_result = await self.db_service.execute_query(
                """SELECT id, cart_id, product_id, quantity, unit_price, total_price, size, color, unit, selected_options, added_at, updated_at 
                   FROM cart_items WHERE id = ?""",
                (existing_id,)
            )
            row = updated_result[0]
        else:
            # Add new item
            result = await self.db_service.execute_query(
                """INSERT INTO cart_items (cart_id, product_id, quantity, unit_price, total_price, size, color, unit, selected_options)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
                   RETURNING id, cart_id, product_id, quantity, unit_price, total_price, size, color, unit, selected_options, added_at, updated_at""",
                (cart.id, item.product_id, item.quantity, item.unit_price, total_price, item.size, item.color, item.unit, item.selected_options)
            )
            row = result[0]
        
        # Update cart totals
        await self._update_cart_totals(cart.id)
        
        return CartItem(
            id=row[0],
            cart_id=row[1],
            product_id=row[2],
            quantity=row[3],
            unit_price=row[4],
            total_price=row[5],
            size=row[6],
            color=row[7],
            unit=row[8],
            selected_options=row[9],
            added_at=row[10],
            updated_at=row[11]
        )
    
    async def get_cart_items(self, user_id: int) -> List[CartItem]:
        """Get all items in user's cart."""
        cart = await self.get_or_create_cart(user_id)
        
        result = await self.db_service.execute_query(
            """SELECT id, cart_id, product_id, quantity, unit_price, total_price, size, color, unit, selected_options, added_at, updated_at
               FROM cart_items WHERE cart_id = ? ORDER BY added_at DESC""",
            (cart.id,)
        )
        
        return [
            CartItem(
                id=row[0],
                cart_id=row[1],
                product_id=row[2],
                quantity=row[3],
                unit_price=row[4],
                total_price=row[5],
                size=row[6],
                color=row[7],
                selected_options=row[8],
                added_at=row[9],
                updated_at=row[10],
                unit=row[11]
            )
            for row in result
        ]
    
    async def update_item_quantity(self, user_id: int, item_id: int, new_quantity: int) -> Optional[CartItem]:
        """Update quantity of an item in the cart."""
        if new_quantity <= 0:
            return await self.remove_item_from_cart(user_id, item_id)
        
        cart = await self.get_or_create_cart(user_id)
        
        # Update item quantity and total price
        result = await self.db_service.execute_query(
            """UPDATE cart_items 
               SET quantity = ?, total_price = unit_price * ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND cart_id = ?
               RETURNING id, cart_id, product_id, quantity, unit_price, total_price, size, color, unit, selected_options, added_at, updated_at""",
            (new_quantity, new_quantity, item_id, cart.id)
        )
        
        if not result:
            return None
        
        # Update cart totals
        await self._update_cart_totals(cart.id)
        
        row = result[0]
        return CartItem(
            id=row[0],
            cart_id=row[1],
            product_id=row[2],
            quantity=row[3],
            unit_price=row[4],
            total_price=row[5],
            size=row[6],
            color=row[7],
            unit=row[8],
            selected_options=row[9],
            added_at=row[10],
            updated_at=row[11]
        )
    
    async def remove_item_from_cart(self, user_id: int, item_id: int) -> bool:
        """Remove an item from the cart."""
        cart = await self.get_or_create_cart(user_id)
        
        result = await self.db_service.execute_query(
            "DELETE FROM cart_items WHERE id = ? AND cart_id = ?",
            (item_id, cart.id)
        )
        
        # Update cart totals
        await self._update_cart_totals(cart.id)
        
        return True
    
    async def clear_cart(self, user_id: int) -> bool:
        """Clear all items from the user's cart."""
        cart = await self.get_or_create_cart(user_id)
        
        await self.db_service.execute_query(
            "DELETE FROM cart_items WHERE cart_id = ?",
            (cart.id,)
        )
        
        # Update cart totals
        await self._update_cart_totals(cart.id)
        
        return True
    
    async def get_cart_summary(self, user_id: int) -> UserCart:
        """Get cart summary with current totals."""
        cart = await self.get_or_create_cart(user_id)
        await self._update_cart_totals(cart.id)  # Ensure totals are current
        
        # Get updated cart
        result = await self.db_service.execute_query(
            "SELECT id, user_id, total_amount, total_items, currency, status, session_id, expires_at, created_at, updated_at FROM user_carts WHERE id = ?",
            (cart.id,)
        )
        
        if result:
            row = result[0]
            return UserCart(
                id=row[0],
                user_id=row[1],
                total_amount=row[2],
                total_items=row[3],
                currency=row[4],
                status=row[5],
                session_id=row[6],
                expires_at=row[7],
                created_at=row[8],
                updated_at=row[9]
            )
        
        return cart
    
    async def convert_cart_to_order(self, user_id: int) -> bool:
        """Mark cart as converted when order is placed."""
        cart = await self.get_or_create_cart(user_id)
        
        await self.db_service.execute_query(
            "UPDATE user_carts SET status = 'converted', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (cart.id,)
        )
        
        return True
    
    async def _update_cart_totals(self, cart_id: int) -> None:
        """Internal method to update cart totals based on current items."""
        result = await self.db_service.execute_query(
            "SELECT COALESCE(SUM(total_price), 0), COALESCE(SUM(quantity), 0) FROM cart_items WHERE cart_id = ?",
            (cart_id,)
        )
        
        if result:
            total_amount = result[0][0]
            total_items = result[0][1]
            
            await self.db_service.execute_query(
                "UPDATE user_carts SET total_amount = ?, total_items = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (total_amount, total_items, cart_id)
            )


# Global instance
cart_service = CartService()
