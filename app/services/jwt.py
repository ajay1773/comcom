import jwt
from app.core.config import settings


class JWTService:
   
    @staticmethod
    async def generate_jwt(user_id: int) -> str:
        """Generate a JWT token for the user."""
        secret = settings.JWT_SECRET
        payload = {
            "user_id": user_id
        }
        return jwt.encode(payload, secret, algorithm="HS256")

    @staticmethod
    async def verify_jwt(token: str) -> int:
        """Verify a JWT token and return the user ID."""
        secret = settings.JWT_SECRET
        return jwt.decode(token, secret, algorithms=["HS256"])["user_id"]
