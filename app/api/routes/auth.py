"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, status
from app.models.user import UserLogin, UserCreate, User
from app.services.auth import auth_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class SigninRequest(BaseModel):
    """Request model for signin."""
    email: str
    password: str


class SignupRequest(BaseModel):
    """Request model for signup."""
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str


class AuthResponse(BaseModel):
    """Response model for authentication (signin/signup)."""
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None


@router.post("/signin", response_model=AuthResponse)
async def signin(request: SigninRequest):
    """
    Sign in a user with email and password.
    
    Args:
        request: Signin credentials containing email and password
        
    Returns:
        SigninResponse with token and user details if successful
        
    Raises:
        401: Invalid credentials
        500: Internal server error
    """
    try:
        # Create UserLogin object
        credentials = UserLogin(email=request.email, password=request.password)
        
        # Authenticate user
        user, _ = await auth_service.signin_user(credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT token using the JWT service
        from app.services.jwt import JWTService
        token = await JWTService.generate_jwt(user.id)
        
        # Return user details and token
        return AuthResponse(
            success=True,
            message="Sign in successful",
            token=token,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
            }
        )
        
    except ValueError as e:
        # Authentication failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        # Internal error
        print(f"❌ Error in signin: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during sign in"
        )


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """
    Sign up a new user with email, password, and profile information.
    
    Args:
        request: Signup data containing email, password, and user details
        
    Returns:
        AuthResponse with token and user details if successful
        
    Raises:
        400: User already exists or validation error
        500: Internal server error
    """
    try:
        # Create UserCreate object
        user_data = UserCreate(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone
        )
        
        # Create user
        user, _ = await auth_service.signup_user(user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Generate JWT token using the JWT service
        from app.services.jwt import JWTService
        token = await JWTService.generate_jwt(user.id)
        
        # Return user details and token
        return AuthResponse(
            success=True,
            message="Account created successfully",
            token=token,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
            }
        )
        
    except ValueError as e:
        # User already exists or validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Internal error
        print(f"❌ Error in signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during sign up"
        )


@router.post("/signout")
async def signout():
    """
    Sign out a user.
    
    Note: With JWT tokens, logout is typically handled client-side by removing the token.
    This endpoint is provided for consistency but doesn't need to do much server-side.
    """
    return {
        "success": True,
        "message": "Signed out successfully"
    }

