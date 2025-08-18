import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings
from ..api.models import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Path to users database file
USERS_DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "users.json")

def load_users_db() -> Dict[str, Dict[str, Any]]:
    """Load users from JSON file."""
    if not os.path.exists(USERS_DB_FILE):
        return {}
    
    try:
        with open(USERS_DB_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_users_db(users_db: Dict[str, Dict[str, Any]]) -> None:
    """Save users to JSON file."""
    os.makedirs(os.path.dirname(USERS_DB_FILE), exist_ok=True)
    with open(USERS_DB_FILE, 'w') as f:
        # Convert datetime objects to strings for JSON serialization
        serializable_db = {}
        for username, user_data in users_db.items():
            serializable_user = user_data.copy()
            if isinstance(serializable_user.get("created_at"), datetime):
                serializable_user["created_at"] = serializable_user["created_at"].isoformat()
            serializable_db[username] = serializable_user
        json.dump(serializable_db, f, indent=2)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get user from database."""
    users_db = load_users_db()
    user = users_db.get(username)
    if user and isinstance(user.get("created_at"), str):
        # Convert ISO string back to datetime for internal use
        user["created_at"] = datetime.fromisoformat(user["created_at"])
    return user

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user."""
    users_db = load_users_db()
    
    if username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(password)
    user_data = {
        "id": len(users_db) + 1,
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    users_db[username] = user_data
    save_users_db(users_db)
    return user_data

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get the current active user."""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user