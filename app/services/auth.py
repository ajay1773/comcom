"""Authentication service for user management."""
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import User, UserCreate, UserLogin, AuthStatus
from app.services.db.db import db_service
from app.services.db.user import user_service


class AuthService:
    """Service for handling user authentication and session management."""

    def __init__(self):
        self.db_service = db_service
        self.session_duration_hours = 24 * 7  # 7 days
        self.security = HTTPBearer(auto_error=False)

    async def signup_user(self, user_data: UserCreate) -> Tuple[User, str]:
        """
        Create a new user account.
        Returns: (User, session_token)
        """
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        password_hash = self._hash_password(user_data.password)

        # Create user
        user_id = await user_service.create_user(user_data, password_hash)
        if not user_id:
            raise ValueError("Failed to create user")

        # Get the created user
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("Failed to retrieve created user")

        return user, ""  # Return empty string for session token (will be created in workflow)

    async def signin_user(self, credentials: UserLogin) -> Tuple[User, str]:
        """
        Sign in a user with email and password.
        Returns: (User, session_token)
        """
        # Get user
        user = await user_service.get_user_by_email(credentials.email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        password_hash = await user_service.get_password_hash(credentials.email)
        if not password_hash or not self._verify_password(credentials.password, password_hash):
            raise ValueError("Invalid email or password")

        return user, ""  # Return empty string for session token (will be created in workflow)

    async def create_session(self, user_id: int, thread_id: str) -> str:
        """Create a new session for the user."""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=self.session_duration_hours)

        await self.db_service.create_session(user_id, session_token, thread_id, expires_at)
        return session_token

    async def get_user_from_thread(self, thread_id: str) -> Optional[User]:
        """Get authenticated user from thread ID."""
        session = await self.db_service.get_session_by_thread(thread_id)
        if not session:
            return None

        # Check if session is still valid
        expires_at = session.expires_at
        if isinstance(expires_at, str):
            # Handle ISO format datetime strings
            try:
                if expires_at.endswith('Z'):
                    expires_at_str = expires_at[:-1] + '+00:00'
                else:
                    expires_at_str = expires_at
                expires_at = datetime.fromisoformat(expires_at_str)
            except ValueError:
                # If parsing fails, treat as expired
                expires_at = datetime.min
        elif not isinstance(expires_at, datetime):
            # Handle other formats if needed
            expires_at = datetime.now()  # Default to now to trigger expiration
        
        if expires_at < datetime.now():
            await self.db_service.delete_session(session.session_token)
            return None

        return await user_service.get_user_by_id(session.user_id)

    async def verify_session(self, session_token: str) -> Optional[User]:
        """Verify a session token and return the user."""
        session = await self.db_service.get_session(session_token)
        if not session:
            return None

        # Check if session is still valid
        expires_at = session.expires_at
        if isinstance(expires_at, str):
            # Handle ISO format datetime strings
            try:
                if expires_at.endswith('Z'):
                    expires_at_str = expires_at[:-1] + '+00:00'
                else:
                    expires_at_str = expires_at
                expires_at = datetime.fromisoformat(expires_at_str)
            except ValueError:
                # If parsing fails, treat as expired
                expires_at = datetime.min
        elif not isinstance(expires_at, datetime):
            # Handle other formats if needed
            expires_at = datetime.now()  # Default to now to trigger expiration
        
        if expires_at < datetime.now():
            await self.db_service.delete_session(session_token)
            return None

        return await user_service.get_user_by_id(session.user_id)

    async def logout_user(self, session_token: str) -> bool:
        """Log out a user by deleting their session."""
        try:
            await self.db_service.delete_session(session_token)
            return True
        except Exception:
            return False

    async def check_auth_status(self, thread_id: str, email: Optional[str] = None) -> AuthStatus:
        """
        Check authentication status for a thread.
        If email is provided, also check if user exists.
        """
        # Check if user is already authenticated in this thread
        user = await self.get_user_from_thread(thread_id)
        if user:
            return AuthStatus(
                is_authenticated=True,
                user=user,
                message=f"Welcome back, {user.first_name or user.email}!"
            )

        # If email provided, check if user exists
        if email:
            existing_user = await user_service.get_user_by_email(email)
            if existing_user:
                return AuthStatus(
                    is_authenticated=False,
                    needs_signin=True,
                    message="I found your account! Please provide your password to sign in."
                )
            else:
                return AuthStatus(
                    is_authenticated=False,
                    needs_signup=True,
                    message="I don't see an account with that email. Let's create a new account for you!"
                )

        # No authentication
        return AuthStatus(
            is_authenticated=False,
            needs_signin=True,
            message="To continue, I need you to sign in. Do you have an account with us?"
        )

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    async def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from JWT/session token."""
        if not token:
            return None
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        try:
            # First try to verify as session token
            user = await self.verify_session(token)
            if user:
                return user
        except Exception:
            pass
        
        try:
            # Fallback: try to verify as JWT token
            from app.services.jwt import JWTService
            payload = await JWTService.verify_jwt(token)
            user_id = payload.get("user_id") if isinstance(payload, dict) else payload
            if user_id:
                return await user_service.get_user_by_id(user_id)
        except Exception:
            pass
        
        return None

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
        """Get current authenticated user (required)."""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await self.get_user_from_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user

    async def get_current_user_optional(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:
        """Get current authenticated user (optional)."""
        if not credentials:
            return None
        
        return await self.get_user_from_token(credentials.credentials)

    async def cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions (should be called periodically)."""
        await self.db_service.cleanup_expired_sessions()


# Create singleton instance
auth_service = AuthService()
