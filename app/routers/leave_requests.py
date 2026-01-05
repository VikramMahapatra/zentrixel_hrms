from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import LeaveRequest, Employee, EmployeeLeaveBalance, LeaveType, Attendance
from app.schemas import LeaveRequest as LeaveRequestSchema, LeaveRequestCreate, LeaveRequestApprove
from app.security import get_current_user
# Change 1: Import UserToken and token dependencies
from app.schemas import UserToken
from app.security import get_current_user_token, is_admin

router = APIRouter()

def calculate_days(start_date, end_date):
    return (end_date - start_date).days + 1

@router.get("/", response_model=List[LeaveRequestSchema])
def get_leave_requests(db: Session = Depends(get_db), current_user: UserToken = Depends(get_current_user_token)):  # Changed to UserToken
    # Build query
    query = (
        db.query(LeaveRequest, Employee.first_name, Employee.last_name, LeaveType.leave_name)
        .join(Employee, LeaveRequest.employee_id == Employee.employee_id)
        .join(LeaveType, LeaveRequest.leave_type_id == LeaveType.leave_type_id)
    )
    
    # Apply filters
    if current_user.role_name != "admin":
        query = query.filter(LeaveRequest.employee_id == current_user.employee_id)
    
    # Get results
    results = query.order_by(LeaveRequest.created_at.desc()).all()
    
    # Return transformed results
    return [
        LeaveRequestSchema.model_validate(
            {
                **lr.__dict__,
                "employee_name": f"{first_name} {last_name}",
                "leave_name": leave_name
            }
        )
        for lr, first_name, last_name, leave_name in results
    ]
@router.post("/", response_model=LeaveRequestSchema)
def create_leave_request(request: LeaveRequestCreate, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    total_days = calculate_days(request.start_date, request.end_date)
    leave_request = LeaveRequest(
        employee_id=current_user.employee_id,
        leave_type_id=request.leave_type_id,
        start_date=request.start_date,
        end_date=request.end_date,
        total_days=total_days,
        reason=request.reason
    )
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    return leave_request

# FIX THIS FUNCTION - It has current_user.role.role_name

@router.put("/{leave_id}/submit")
def submit_leave_request(leave_id: str, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.leave_id == leave_id).first()
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if leave_request.employee_id != current_user.employee_id and current_user.role.role_name != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    leave_request.status = "submitted"
    leave_request.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(leave_request)
    return leave_request

@router.put("/{leave_id}/approve")
def approve_leave_request(leave_id: str, approval: LeaveRequestApprove, db: Session = Depends(get_db), current_user: UserToken = Depends(get_current_user_token)):
    if current_user.role_name not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only managers and admins can approve")
    
    
    
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.leave_id == leave_id).first()
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    
    
    if approval.action == "approved":
        leave_request.status = "approved"
        leave_request.approved_by = current_user.employee_id
        leave_request.approved_at = datetime.utcnow()
        
        # Mark attendance as leave for those dates
        from datetime import timedelta
        current_date = leave_request.start_date
        while current_date <= leave_request.end_date:
            attendance = db.query(Attendance).filter(
                Attendance.employee_id == leave_request.employee_id,
                Attendance.date == current_date
            ).first()
            if not attendance:
                attendance = Attendance(
                    employee_id=leave_request.employee_id,
                    date=current_date,
                    status="leave"
                )
                db.add(attendance)
            else:
                attendance.status = "leave"
            current_date += timedelta(days=1)
    else:
        leave_request.status = "rejected"
        leave_request.approved_by = current_user.employee_id # FIX: Use user_id instead of employee_id (UserToken has user_id)
        leave_request.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(leave_request)
    return leave_request

@router.get("/{leave_id}", response_model=LeaveRequestSchema)
def get_leave_request(leave_id: str, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.leave_id == leave_id).first()
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave_request
