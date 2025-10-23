from app.core.config import settings
from typing import List, Any, Sequence, Dict
from pydantic import BaseModel
import aiosqlite
from app.models.user import UserSession


class Order(BaseModel):
    id: int | None = None
    user_id: int
    order_number: str
    status: str  # pending, confirmed, processing, shipped, delivered, cancelled
    amount: float
    total_items: int
    currency: str = "USD"
    payment_status: str  # pending, paid, failed, refunded
    payment_method: str | None = None
    shipping_address_id: int | None = None
    notes: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

class OrderItem(BaseModel):
    id: int | None = None
    order_id: int
    product_id: int
    name: str
    brand: str
    quantity: int
    unit_price: float
    total_price: float
    size: str | None = None
    status: str = "pending"  # pending, confirmed, shipped, delivered, cancelled
    discount_amount: float = 0.0
    created_at: str | None = None
    updated_at: str | None = None

class Product(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    discount_percentage: float
    rating: float
    stock: int
    tags: List[str]
    brand: str
    sku: str
    weight: float
    dimensions: Dict[str, float]
    warranty_information: str
    shipping_information: str
    availability_status: str
    return_policy: str
    minimum_order_quantity: int
    thumbnail: str
    images: List[str]
    barcode: str
    qr_code: str
    available_sizes: List[str]
    unit: str
    gender: str | None
    material: str | None
    style: str | None
    pattern: str | None
    color: str | None

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

class Conversation(BaseModel):
    """Model for conversation metadata."""
    id: int | None = None
    thread_id: str
    user_id: int | None = None
    title: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    last_message_at: str | None = None
    message_count: int = 0

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

        # Create user token usage table (for logged-in users - daily token quota tracking)
        create_user_token_usage_table = """
        CREATE TABLE IF NOT EXISTS user_token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            daily_limit INTEGER DEFAULT 100000,
            reset_date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id, reset_date)
        )
        """

        # Create rate limit tracking table (for logged-out users - IP-based rate limiting)
        create_rate_limit_table = """
        CREATE TABLE IF NOT EXISTS rate_limit_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            request_count INTEGER DEFAULT 0,
            window_start DATETIME NOT NULL,
            window_end DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ip_address, window_start)
        )
        """

        # Create products table
        create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            discount_percentage REAL DEFAULT 0.0,
            rating REAL DEFAULT 0.0,
            stock INTEGER DEFAULT 0,
            tags TEXT NOT NULL DEFAULT '[]',
            brand TEXT NOT NULL,
            sku TEXT NOT NULL,
            weight REAL DEFAULT 0.0,
            dimensions TEXT NOT NULL DEFAULT '{}',
            warranty_information TEXT DEFAULT '',
            shipping_information TEXT DEFAULT '',
            availability_status TEXT DEFAULT 'In Stock',
            return_policy TEXT DEFAULT '',
            minimum_order_quantity INTEGER DEFAULT 1,
            thumbnail TEXT NOT NULL,
            images TEXT NOT NULL DEFAULT '[]',
            barcode TEXT DEFAULT '',
            qr_code TEXT DEFAULT '',
            available_sizes TEXT NOT NULL DEFAULT '[]',
            unit TEXT NOT NULL DEFAULT 'piece',
            -- Legacy fields for backward compatibility
            gender TEXT,
            material TEXT,
            style TEXT,
            pattern TEXT,
            color TEXT
        )
        """

        # Create orders table with constraints
        create_orders_table = """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_number TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')),
            amount REAL NOT NULL CHECK(amount >= 0),
            total_items INTEGER NOT NULL DEFAULT 0 CHECK(total_items >= 0),
            currency TEXT NOT NULL DEFAULT 'USD',
            payment_status TEXT NOT NULL DEFAULT 'pending' CHECK(payment_status IN ('pending', 'paid', 'failed', 'refunded')),
            payment_method TEXT,
            shipping_address_id INTEGER,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (shipping_address_id) REFERENCES user_addresses (id) ON DELETE SET NULL
        )
        """

        # Create order_items table
        create_order_items_table = """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            total_price REAL NOT NULL CHECK(total_price >= 0),
            size TEXT,
            color TEXT,
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
            discount_amount REAL NOT NULL DEFAULT 0.0 CHECK(discount_amount >= 0),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
        """

        # Create conversations table for chat management
        create_conversations_table = """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            title TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_message_at DATETIME,
            message_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """

        # Execute table creation queries separately
        await self.execute_query(create_users_table)
        await self.execute_query(create_sessions_table)
        await self.execute_query(create_conversations_table)
        await self.execute_query(create_user_carts_table)
        await self.execute_query(create_cart_items_table)
        await self.execute_query(create_addresses_table)
        await self.execute_query(create_user_token_usage_table)
        await self.execute_query(create_rate_limit_table)
        await self.execute_query(create_products_table)
        await self.execute_query(create_orders_table)
        await self.execute_query(create_order_items_table)

        # Create indexes for better performance
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_sessions_thread ON user_sessions(thread_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_token_usage_user_date ON user_token_usage(user_id, reset_date)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_rate_limit_ip_window ON rate_limit_tracking(ip_address, window_start)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_addresses_user ON user_addresses(user_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id)")
        
        # Cart-related indexes
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_user_carts_user_id ON user_carts(user_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_user_carts_status ON user_carts(status)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id)")
        
        # Conversation-related indexes
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_conversations_thread_id ON conversations(thread_id)")
        await self.execute_query("CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at)")

    async def create_order(self, order: Order):
        """Create an order in the database."""
        await self.execute_query("INSERT INTO orders (order_number, user_id, amount, total_items, status) VALUES (?, ?, ?, ?, ?)",
                                (order.order_number, order.user_id, order.amount, order.total_items, order.status))

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
