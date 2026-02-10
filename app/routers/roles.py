from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Role, Employee
from app.schemas import Role as RoleSchema, RoleBase
from app.security import get_current_user
# Change 1: Import UserToken and token dependencies
#from app.schemas import UserToken
#from app.security import get_current_user_token, is_admin
from app.security import has_role


router = APIRouter()
"""
def check_admin(current_user: UserToken = Depends(get_current_user_token)):
    if current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    return current_user"""

@router.get("/", response_model=List[RoleSchema])
def get_all_roles(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    roles = db.query(Role).all()
    return roles

@router.post("/", response_model=RoleSchema)
def create_role(role: RoleBase, db: Session = Depends(get_db), user = Depends(has_role(["admin"]))):
    db_role = db.query(Role).filter(Role.role_name == role.role_name).first()
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    db_role = Role(role_name=role.role_name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role
