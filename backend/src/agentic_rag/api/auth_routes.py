from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from .models import UserLogin, Token, User
from ..core.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from ..core.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Authenticate user and return access token."""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information."""
    return User(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )

@router.post("/logout")
async def logout_user():
    """Logout user (client should delete token)."""
    return JSONResponse(content={"message": "Successfully logged out"})