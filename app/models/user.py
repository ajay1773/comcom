from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    """User model for authenticated users."""
    id: Optional[int] = None
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """Model for creating new users."""
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    phone: Optional[str] = Field(None, description="User's phone number")


class UserLogin(BaseModel):
    """Model for user login."""
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserSession(BaseModel):
    """Model for user sessions."""
    id: Optional[int] = None
    user_id: int
    session_token: str
    thread_id: str
    expires_at: datetime
    created_at: Optional[datetime] = None


class UserAddress(BaseModel):
    """Model for user addresses."""
    id: Optional[int] = None
    user_id: int
    type: str = Field(..., description="Address type: 'billing' or 'shipping'")
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    is_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None



class AuthStatus(BaseModel):
    """Model for authentication status."""
    is_authenticated: bool
    user: Optional[User] = None
    needs_signin: bool = False
    needs_signup: bool = False
    message: str = ""
