from app.core.config import settings
from typing import List, Any, Sequence
from pydantic import BaseModel
import aiosqlite
from app.models.user import UserSession


class Order(BaseModel):
    product_id: int
    user_id: int
    quantity: int
    price: float
    status: str

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    gender: str
    brand: str
    material: str
    style: str
    pattern: str
    color: str
    images: str
    available_sizes: str  # JSON string containing available sizes
    unit: str  # Unit of measurement (e.g., "piece", "pair", "set")

class UserCart(BaseModel):
    id: int
    user_id: int
    total_amount: float
    total_items: int
    currency: str
    status: str
    session_id: str | None
    expires_at: str | None
    created_at: str
    updated_at: str

class CartItem(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    size: str | None
    color: str | None
    unit: str | None  # Unit of measurement
    selected_options: str | None  # JSON string
    added_at: str
    updated_at: str

class CartItemWithProductDetails(CartItem):
    product_details: Product | None
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    size: str | None = None
    color: str | None = None
    unit: str | None = None
    selected_options: str | None = None

class DatabaseService:
    """Service for database operations."""

    def __init__(self):
        self.db_url = settings.APP_DATABASE_URL

    async def execute_query(self, query: str, params: Sequence[Any] | None = None) -> List[Any]:
        """Execute a query and return results."""
        async with aiosqlite.connect(self.db_url) as db:
            cursor = None
            try:
                if params:
                    if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (list, tuple)):
                        # Handle bulk insert - check if first element is a sequence (tuple/list)
                        cursor = await db.executemany(query, params)
                    else:
                        # Single parameterized query
                        cursor = await db.execute(query, params)
                else:
                    # Query without parameters
                    cursor = await db.execute(query)

                # Fetch results for SELECT queries and queries with RETURNING clause
                query_upper = query.strip().upper()
                if query_upper.startswith("SELECT") or "RETURNING" in query_upper:
                    rows = await cursor.fetchall()
                    result = list(rows) if rows else []
                else:
                    result = []

                # Explicitly close cursor before commit
                await cursor.close()
                await db.commit()
                return result
            except aiosqlite.Error as e:
                if cursor:
                    await cursor.close()
                await db.rollback()
                raise e

    async def init_db(self):
        """Initialize the database schema."""
        # Create users table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Create user sessions table
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            thread_id TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """

        # Create user carts table (one-to-one with users)
        create_user_carts_table = """
        CREATE TABLE IF NOT EXISTS user_carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            total_amount REAL DEFAULT 0.0,
            total_items INTEGER DEFAULT 0,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'abandoned', 'converted')),
            session_id TEXT,
            expires_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """

        # Create cart items table (one-to-many with carts)
        create_cart_items_table = """
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price > 0),
            total_price REAL NOT NULL CHECK(total_price > 0),
            size TEXT,
            color TEXT,
            unit TEXT,
            selected_options TEXT, -- JSON string for additional product options
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cart_id) REFERENCES user_carts (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
            UNIQUE(cart_id, product_id, size, color, unit) -- Prevent duplicate items with same options
        )
        """

        # Create user addresses table
        create_addresses_table = """
        CREATE TABLE IF NOT EXISTS user_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('home', 'work', 'other', 'billing', 'shipping')),
            street TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            zip_code TEXT NOT NULL,
            country TEXT DEFAULT 'US',
            is_default BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """

        # Create products table
        create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            gender TEXT NOT NULL,
            brand TEXT NOT NULL,
            material TEXT NOT NULL,
            style TEXT NOT NULL,
            pattern TEXT NOT NULL,
            color TEXT NOT NULL,
            images TEXT NOT NULL,
            available_sizes TEXT NOT NULL DEFAULT '[]',
            unit TEXT NOT NULL DEFAULT 'piece'
        )
        """

        # Create orders table with constraints
        create_orders_table = """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            price REAL NOT NULL CHECK(price > 0),
            status TEXT NOT NULL DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """

        # Execute table creation queries separately
        await self.execute_query(create_users_table)
        await self.execute_query(create_sessions_table)
        await self.execute_query(create_user_carts_table)
        await self.execute_query(create_cart_items_table)
        await self.execute_query(create_addresses_table)
        await self.execute_query(create_products_table)
        await self.execute_query(create_orders_table)

        # Create indexes for better performance
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_sessions_thread ON user_sessions(thread_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_addresses_user ON user_addresses(user_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        
        # Cart-related indexes
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_user_carts_user_id ON user_carts(user_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_user_carts_status ON user_carts(status)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id)")

    async def create_order(self, order: Order):
        """Create an order in the database."""
        await self.execute_query("INSERT INTO orders (product_id, user_id, quantity, price, status) VALUES (?, ?, ?, ?, ?)",
                                (order.product_id, order.user_id, order.quantity, order.price, order.status))

    # Session management methods
    async def create_session(self, user_id: int, session_token: str, thread_id: str, expires_at) -> None:
        """Create a new user session."""
        await self.execute_query(
            "INSERT INTO user_sessions (user_id, session_token, thread_id, expires_at) VALUES (?, ?, ?, ?)",
            (user_id, session_token, thread_id, expires_at)
        )

    async def get_session(self, session_token: str) -> UserSession | None:
        """Get session by token."""
        result = await self.execute_query(
            "SELECT id, user_id, session_token, thread_id, expires_at, created_at FROM user_sessions WHERE session_token = ?",
            (session_token,)
        )
        if result:
            row = result[0]
            return UserSession(
                id=row[0],
                user_id=row[1],
                session_token=row[2],
                thread_id=row[3],
                expires_at=row[4],
                created_at=row[5]
            )
        return None

    async def get_session_by_thread(self, thread_id: str) -> UserSession | None:
        """Get active session by thread ID."""
        result = await self.execute_query(
            "SELECT id, user_id, session_token, thread_id, expires_at, created_at FROM user_sessions WHERE thread_id = ? AND expires_at > datetime('now')",
            (thread_id,)
        )
        if result:
            row = result[0]
            return UserSession(
                id=row[0],
                user_id=row[1],
                session_token=row[2],
                thread_id=row[3],
                expires_at=row[4],
                created_at=row[5]
            )
        return None

    async def delete_session(self, session_token: str) -> None:
        """Delete a session (logout)."""
        await self.execute_query(
            "DELETE FROM user_sessions WHERE session_token = ?",
            (session_token,)
        )

    async def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        await self.execute_query(
            "DELETE FROM user_sessions WHERE expires_at <= datetime('now')"
        )

# Create a singleton instance
db_service = DatabaseService()
