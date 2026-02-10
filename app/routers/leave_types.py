from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import LeaveType, Employee
from app.schemas import LeaveType as LeaveTypeSchema, LeaveTypeBase
from app.security import get_current_user
from app.security import has_role
# Change 1: Import UserToken and token dependencies
from app.schemas import UserToken
from app.security import get_current_user_token, is_admin

router = APIRouter()

"""def check_admin(current_user: UserToken = Depends(get_current_user_token)):
    if current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    return current_user"""

@router.get("/", response_model=List[LeaveTypeSchema])
def get_all_leave_types(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    leave_types = db.query(LeaveType).all()
    return leave_types

@router.post("/", response_model=LeaveTypeSchema)
def create_leave_type(leave_type: LeaveTypeBase, db: Session = Depends(get_db), user = Depends(has_role(["admin"]))):
    db_leave_type = db.query(LeaveType).filter(LeaveType.leave_name == leave_type.leave_name).first()
    if db_leave_type:
        raise HTTPException(status_code=400, detail="Leave type already exists")
    db_leave_type = LeaveType(**leave_type.dict())
    db.add(db_leave_type)
    db.commit()
    db.refresh(db_leave_type)
    return db_leave_type
