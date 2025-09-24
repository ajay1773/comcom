from typing import List, Dict, Any
from app.models.user import User, UserCreate, UserAddress
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

    async def create_user_address(self, address_data: Dict[str, Any]) -> UserAddress | None:
        """Create a new user address."""
        try:
            result = await self.db_service.execute_query(
                """INSERT INTO user_addresses (user_id, type, street, city, state, zip_code, country, is_default) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?) 
                   RETURNING id, user_id, type, street, city, state, zip_code, country, is_default, created_at, updated_at""",
                (
                    address_data["user_id"],
                    address_data["type"],
                    address_data["street"],
                    address_data["city"],
                    address_data["state"],
                    address_data["zip_code"],
                    address_data["country"],
                    address_data["is_default"]
                )
            )
            
            if result:
                row = result[0]
                return UserAddress(
                    id=row[0],
                    user_id=row[1],
                    type=row[2],
                    street=row[3],
                    city=row[4],
                    state=row[5],
                    zip_code=row[6],
                    country=row[7],
                    is_default=bool(row[8]),
                    created_at=row[9],
                    updated_at=row[10]
                )
            return None
        except Exception as e:
            print(f"Error creating user address: {e}")
            return None

    async def unset_default_addresses(self, user_id: int, address_type: str) -> bool:
        """Unset all default addresses for a user of a specific type."""
        try:
            await self.db_service.execute_query(
                "UPDATE user_addresses SET is_default = FALSE WHERE user_id = ? AND type = ?",
                (user_id, address_type)
            )
            return True
        except Exception as e:
            print(f"Error unsetting default addresses: {e}")
            return False

    async def get_user_addresses(self, user_id: int) -> List[UserAddress]:
        """Get all addresses for a user."""
        try:
            result = await self.db_service.execute_query(
                "SELECT id, user_id, type, street, city, state, zip_code, country, is_default, created_at, updated_at FROM user_addresses WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            
            addresses = []
            for row in result:
                addresses.append(UserAddress(
                    id=row[0],
                    user_id=row[1],
                    type=row[2],
                    street=row[3],
                    city=row[4],
                    state=row[5],
                    zip_code=row[6],
                    country=row[7],
                    is_default=bool(row[8]),
                    created_at=row[9],
                    updated_at=row[10]
                ))
            
            return addresses
        except Exception as e:
            print(f"Error getting user addresses: {e}")
            return []

    async def get_user_address_by_id(self, user_id: int, address_id: int) -> UserAddress | None:
        """Get a specific address by ID for a user."""
        try:
            result = await self.db_service.execute_query(
                "SELECT id, user_id, type, street, city, state, zip_code, country, is_default, created_at FROM user_addresses WHERE id = ? AND user_id = ?",
                (address_id, user_id)
            )
            
            if result:
                row = result[0]
                return UserAddress(
                    id=row[0],
                    user_id=row[1],
                    type=row[2],
                    street=row[3],
                    city=row[4],
                    state=row[5],
                    zip_code=row[6],
                    country=row[7],
                    is_default=bool(row[8]),
                    created_at=row[9],
                )
            return None
        except Exception as e:
            print(f"Error getting user address by ID: {e}")
            return None

    

    async def update_user_address(self, address_id: int, address_data: Dict[str, Any]) -> UserAddress | None:
        """Update an existing user address."""
        try:
            result = await self.db_service.execute_query(
                """UPDATE user_addresses 
                   SET type = ?, street = ?, city = ?, state = ?, zip_code = ?, country = ?, is_default = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ? AND user_id = ?
                   RETURNING id, user_id, type, street, city, state, zip_code, country, is_default, created_at, updated_at""",
                (
                    address_data["type"],
                    address_data["street"],
                    address_data["city"],
                    address_data["state"],
                    address_data["zip_code"],
                    address_data["country"],
                    address_data["is_default"],
                    address_id,
                    address_data["user_id"]
                )
            )
            
            if result:
                row = result[0]
                return UserAddress(
                    id=row[0],
                    user_id=row[1],
                    type=row[2],
                    street=row[3],
                    city=row[4],
                    state=row[5],
                    zip_code=row[6],
                    country=row[7],
                    is_default=bool(row[8]),
                    created_at=row[9],
                    updated_at=row[10]
                )
            return None
        except Exception as e:
            print(f"Error updating user address: {e}")
            return None

    async def delete_user_address(self, address_id: int) -> bool:
        """Delete a user address."""
        try:
            result = await self.db_service.execute_query(
                "DELETE FROM user_addresses WHERE id = ? RETURNING id",
                (address_id,)
            )
            return len(result) > 0 if result else False
        except Exception as e:
            print(f"Error deleting user address: {e}")
            return False

    async def set_first_address_as_default(self, user_id: int, address_type: str) -> bool:
        """Set the first address of a given type as default for a user."""
        try:
            result = await self.db_service.execute_query(
                "SELECT id FROM user_addresses WHERE user_id = ? AND type = ? ORDER BY created_at ASC LIMIT 1",
                (user_id, address_type)
            )
            
            if result:
                first_address_id = result[0][0]
                await self.db_service.execute_query(
                    "UPDATE user_addresses SET is_default = TRUE WHERE id = ?",
                    (first_address_id,)
                )
                return True
            return False
        except Exception as e:
            print(f"Error setting first address as default: {e}")
            return False

user_service = UserService()