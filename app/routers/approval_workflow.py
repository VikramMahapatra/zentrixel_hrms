from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import ApprovalWorkflow, Employee, LeaveRequest, Role
from app.security import get_current_user
# Change 1: Import UserToken and get_current_user_token
from app.schemas import ApprovalWorkflowSchema, UserToken
from app.security import  get_current_user_token, is_admin
from app.security import has_role

router = APIRouter()

@router.get("/", response_model=List[ApprovalWorkflowSchema])
def get_approval_workflows(db: Session = Depends(get_db),  user = Depends(has_role(["admin"]))):
    workflows = db.query(ApprovalWorkflow).all()
    
    # Get approver names for each workflow
    result = []
    for workflow in workflows:
        approver = db.query(Employee).filter(Employee.employee_id == workflow.approver_id).first()
        
        # Create dict that matches the schema
        workflow_dict = {
            **workflow.__dict__,
            "approver_name": f"{approver.first_name} {approver.last_name}" if approver else "Unknown"
        }
        
        # Remove SQLAlchemy internal attributes
        workflow_dict.pop('_sa_instance_state', None)
        
        result.append(workflow_dict)
    
    return result

@router.get("/pending")
def get_pending_approvals(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    pending = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.approver_id == current_user.employee_id,
        ApprovalWorkflow.action == "submitted"
    ).all()
    return pending

@router.get("/{leave_id}/workflow-history")
def get_leave_workflow_history(
    leave_id: str, db: Session = Depends(get_db),
    user = Depends(has_role(["admin", "manager", "employee"])),
    current_user: Employee = Depends(get_current_user)):
    """Get workflow history for a specific leave request"""
    
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.leave_id == leave_id).first()
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    if (leave_request.employee_id != current_user.employee_id and "admin" not in user.roles):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    workflow_logs = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.request_id == leave_id,
        ApprovalWorkflow.request_type == "leave_request"
    ).order_by(ApprovalWorkflow.action_at.asc()).all()
    
    result = []
    for log in workflow_logs:
        # DIRECT JOIN QUERY - This always works
        approver_data = db.query(
            Employee.first_name,
            Employee.last_name,
            Role.role_name
        ).join(Role, Employee.role_id == Role.role_id).filter(
            Employee.employee_id == log.approver_id
        ).first()
        
        if approver_data:
            approver_name = f"{approver_data.first_name} {approver_data.last_name}"
            approver_role = approver_data.role_name
        else:
            approver_name = "Unknown"
            approver_role = "Unknown"
        
        result.append({
            "workflow_id": log.workflow_id,
            "request_type": log.request_type,
            "request_id": log.request_id,
            "action": log.action,
            "remarks": log.remarks,
            "action_at": log.action_at,
            "approver_id": log.approver_id,
            "approver_name": approver_name,
            "approver_role": approver_role
        })
    
    return result
