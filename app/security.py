from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from app.schemas import UserToken
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 80

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Add this function after your existing create_access_token function
def create_user_token(employee, role_name: str):
    """Create JWT token with user info"""
    token_data = {
        "sub": employee.email,
        "employee_id": employee.employee_id,
        "email": employee.email,
        "role_id": employee.role_id,
        "role_name": role_name
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return access_token

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ========== ADD THIS NEW DEPENDENCY ==========
async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserToken:
    """Get UserToken from JWT (no database query)"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Create UserToken from payload
        user_token = UserToken(
            employee_id=payload.get("employee_id"),
            email=payload.get("email"),
            role_id=payload.get("role_id"),
            role_name=payload.get("role_name")
        )
        # Validate required fields
        if not user_token.user_id or not user_token.email:
            raise HTTPException(status_code=401, detail="Invalid token structure")
        return user_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
# ========== END OF NEW DEPENDENCY ==========    

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    email = decode_token(token)
    from app.database import SessionLocal
    from app.models import Employee
    db = SessionLocal()
    user = db.query(Employee).filter(Employee.email == email).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def is_admin(current_user: UserToken = Depends(get_current_user_token)):
    """Dependency to ensure the current user is an admin."""
    if current_user.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

# ========== REPLACE THIS FUNCTION ==========
def is_manager_or_admin(current_user: UserToken = Depends(get_current_user_token)):
    """Dependency to ensure the current user is a manager or admin."""
    if current_user.role_name not in ("manager", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or admin privileges required")
    return current_user
# ========== NEW VERSION ABOVE ==========
