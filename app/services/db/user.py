from app.models.user import User, UserCreate
from app.services.db.db import db_service


class UserService:

    def __init__(self):
        self.db_service = db_service

    async def create_user(self, user_data: UserCreate, password_hash: str) -> int | None:
        """Create a new user and return the user ID."""
        result = await self.db_service.execute_query(
            "INSERT INTO users (email, password_hash, first_name, last_name, phone) VALUES (?, ?, ?, ?, ?) RETURNING id",
            (user_data.email, password_hash, user_data.first_name, user_data.last_name, user_data.phone)
        )
        return result[0][0] if result else None



    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        result = await self.db_service.execute_query(
            "SELECT id, email, first_name, last_name, phone, is_active, created_at, updated_at FROM users WHERE id = ? AND is_active = TRUE",
            (user_id,)
        )
        if result:
            row = result[0]
            return User(
                id=row[0],
                email=row[1],
                first_name=row[2],
                last_name=row[3],
                phone=row[4],
                is_active=bool(row[5]),
                created_at=row[6],
                updated_at=row[7]
            )
        return None

    async def get_password_hash(self, email: str) -> str | None:
        """Get password hash for user authentication."""
        result = await self.db_service.execute_query(
            "SELECT password_hash FROM users WHERE email = ? AND is_active = TRUE",
            (email,)
        )
        return result[0][0] if result else None

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = await self.db_service.execute_query(
            "SELECT id, email, first_name, last_name, phone, is_active, created_at, updated_at FROM users WHERE email = ? AND is_active = TRUE",
            (email,)
        )
        if result:
            row = result[0]
            return User(
                id=row[0],
                email=row[1],
                first_name=row[2],
                last_name=row[3],
                phone=row[4],
                is_active=bool(row[5]),
                created_at=row[6],
                updated_at=row[7]
            )
        return None

user_service = UserService()