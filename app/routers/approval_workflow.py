from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import ApprovalWorkflow, Employee
from app.security import get_current_user
# Change 1: Import UserToken and get_current_user_token
from app.schemas import UserToken
from app.security import  get_current_user_token, is_admin

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_approval_workflows(db: Session = Depends(get_db), current_user: UserToken= Depends(get_current_user_token)):# Changed to UserToken
    if current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view all workflows")
    
    workflows = db.query(ApprovalWorkflow).all()
    return workflows

@router.get("/pending")
def get_pending_approvals(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    pending = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.approver_id == current_user.employee_id,
        ApprovalWorkflow.action == "submitted"
    ).all()
    return pending
