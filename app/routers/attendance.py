from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, date
from app.database import get_db
from app.models import Attendance, WeeklyAttendanceSummary, Employee
from app.schemas import Attendance as AttendanceSchema, AttendanceCreate
from app.security import get_current_user
from app.schemas import UserToken
from app.security import get_current_user_token, is_admin, is_manager_or_admin

router = APIRouter()

@router.post("/checkin", response_model=AttendanceSchema)
def check_in(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    today = date.today()
    attendance = db.query(Attendance).filter(
        Attendance.employee_id == current_user.employee_id,
        Attendance.date == today
    ).first()
    
    if attendance and attendance.check_in:
        raise HTTPException(status_code=400, detail="Already checked in")
    
    if not attendance:
        attendance = Attendance(
            employee_id=current_user.employee_id,
            date=today,
            check_in=datetime.utcnow(),
            status="present"
        )
        db.add(attendance)
    else:
        attendance.check_in = datetime.utcnow()
        attendance.status = "present"
    
    db.commit()
    db.refresh(attendance)
    return attendance

@router.post("/checkout", response_model=AttendanceSchema)
def check_out(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    today = date.today()
    attendance = db.query(Attendance).filter(
        Attendance.employee_id == current_user.employee_id,
        Attendance.date == today
    ).first()
    
    if not attendance or not attendance.check_in:
        raise HTTPException(status_code=400, detail="Please check in first")
    
    if attendance.check_out:
        raise HTTPException(status_code=400, detail="Already checked out")
    
    attendance.check_out = datetime.utcnow()
    hours = (attendance.check_out - attendance.check_in).total_seconds() / 3600
    if hours > 8:
        hours = 8
    attendance.total_hours = round(hours, 2)
    
    db.commit()
    db.refresh(attendance)
    return attendance

@router.get("/daily/{emp_id}", response_model=List[AttendanceSchema])
def get_daily_attendance(emp_id: str, db: Session = Depends(get_db), current_user: UserToken = Depends(get_current_user_token)): # Changed to UserToken
    if current_user.role_name not in ["admin", "manager"] and current_user.employee_id != emp_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
     # Build query
    results = (
        db.query(Attendance, Employee.first_name, Employee.last_name)
        .join(Employee, Attendance.employee_id == Employee.employee_id)
        .filter(Attendance.employee_id == emp_id)
        .order_by(Attendance.date.desc())
        .all()
    )
    
    # Return transformed results
    return [
        AttendanceSchema.model_validate(
            {
                **attendance.__dict__,
                "employee_name": f"{first_name} {last_name}"
            }
        )
        for attendance, first_name, last_name in results
    ]

@router.post("/weekly-summary")
def generate_weekly_summary(db: Session = Depends(get_db), current_user: UserToken = Depends(get_current_user_token)): # Changed to UserToken
    if current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can generate summaries")
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    employees = db.query(Employee).all()
    summaries = []
    
    for emp in employees:
        attendance_records = db.query(Attendance).filter(
            Attendance.employee_id == emp.employee_id,
            Attendance.date >= week_start,
            Attendance.date <= week_end
        ).all()
        
        total_hours = sum(a.total_hours or 0 for a in attendance_records)
        over_time = max(0, total_hours - 40)
        
        summary = WeeklyAttendanceSummary(
            employee_id=emp.employee_id,
            week_start_date=week_start,
            week_end_date=week_end,
            total_hours=round(total_hours, 2),
            over_time=round(over_time, 2)
        )
        db.add(summary)
        summaries.append(summary)
    
    db.commit()
    return {"message": "Weekly summaries generated", "count": len(summaries)}

@router.get("/weekly-summary/{emp_id}")
def get_weekly_summary(emp_id: str, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    # Build query
    results = (
        db.query(WeeklyAttendanceSummary, Employee.first_name, Employee.last_name)
        .join(Employee, WeeklyAttendanceSummary.employee_id == Employee.employee_id)
        .filter(WeeklyAttendanceSummary.employee_id == emp_id)
        .order_by(WeeklyAttendanceSummary.week_start_date.desc())
        .all()
    )
    
    # Return transformed results
    return [
        {
            **summary.__dict__,
            "employee_name": f"{first_name} {last_name}"
        }
        for summary, first_name, last_name in results
    ]
