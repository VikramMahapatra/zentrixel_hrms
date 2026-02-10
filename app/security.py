from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import UserToken
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
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(401, "Invalid token")
        return email
    except JWTError:
        raise HTTPException(401, "Invalid token")


# ✅ MAIN JWT DEPENDENCY (NO DB HIT)
async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserToken:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = UserToken(
            employee_id=payload.get("employee_id"),
            email=payload.get("email"),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", [])
        )
        if not user.employee_id or not user.email:
            raise HTTPException(401, "Invalid token structure")
        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")


# ✅ DB USER (ONLY WHEN NEEDED)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    from app.database import SessionLocal
    from app.models import Employee

    email = decode_token(credentials.credentials)
    db = SessionLocal()
    user = db.query(Employee).filter(Employee.email == email).first()
    db.close()

    if not user:
        raise HTTPException(401, "User not found")
    return user


# ✅ ROLE CHECK (ADMIN / MANAGER)
def has_role(required_roles: list):
    def checker(user: UserToken = Depends(get_current_user_token)):
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(403, "Access denied")
        return user
    return checker


# ✅ PERMISSION CHECK (FINE GRAIN)
def has_permission(permission: str):
    def checker(user: UserToken = Depends(get_current_user_token)):
        if permission not in user.permissions:
            raise HTTPException(403, "Permission denied")
        return user
    return checker






























"""def is_admin(current_user: UserToken = Depends(get_current_user_token)):
    Dependency to ensure the current user is an admin.
    if current_user.role_name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

# ========== REPLACE THIS FUNCTION ==========
def is_manager_or_admin(current_user: UserToken = Depends(get_current_user_token)):
    Dependency to ensure the current user is a manager or admin.
    if current_user.role_name not in ("manager", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager or admin privileges required")
    return current_user
# Add this function after your existing create_access_token function
def create_user_token(employee, role_name: str):
    Create JWT token with user info
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
        raise HTTPException(status_code=401, detail="Invalid token")"""