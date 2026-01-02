from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, date
import uuid
from app.database import get_db
from app.models import Timesheet, Employee, Project, Task, ApprovalWorkflow
from app.schemas import Timesheet as TimesheetSchema, TimesheetCreate, TimesheetApprove, WeeklyTimesheetCreate, WeeklyTimesheetResponse, DailyTimesheetEntry
from app.security import get_current_user
# Change 1: Import UserToken and token dependencies
from app.schemas import UserToken
from app.security import get_current_user_token, is_admin

router = APIRouter()

@router.post("/", response_model=TimesheetSchema)
def create_timesheet(timesheet: TimesheetCreate, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    project = db.query(Project).filter(Project.project_id == timesheet.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task = db.query(Task).filter(Task.task_id == timesheet.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if timesheet.hours > 8:
        raise HTTPException(status_code=400, detail="Cannot log more than 8 hours per day")
    
    db_timesheet = Timesheet(
        employee_id=current_user.employee_id,
        project_id=timesheet.project_id,
        task_id=timesheet.task_id,
        date=timesheet.date,
        hours=timesheet.hours,
        description=timesheet.description
    )
    db.add(db_timesheet)
    db.commit()
    db.refresh(db_timesheet)
    return db_timesheet

@router.post("/weekly", response_model=WeeklyTimesheetResponse)
def create_weekly_timesheet(
    weekly_timesheet: WeeklyTimesheetCreate, 
    db: Session = Depends(get_db), 
    current_user: Employee = Depends(get_current_user)
):
    """
    Create timesheet entries for an entire week in one go.
    week_start_date should be Monday.
    Entries can include weekdays (Mon-Fri) or full week (Mon-Sun).
    """
    # Validate project and task exist
    project = db.query(Project).filter(Project.project_id == weekly_timesheet.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task = db.query(Task).filter(Task.task_id == weekly_timesheet.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Validate week_start_date is Monday
    if weekly_timesheet.week_start_date.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start_date must be a Monday")
    
    # Validate entries
    if not weekly_timesheet.entries or len(weekly_timesheet.entries) == 0:
        raise HTTPException(status_code=400, detail="At least one day entry is required")
    
    if len(weekly_timesheet.entries) > 7:
        raise HTTPException(status_code=400, detail="Maximum 7 entries (Mon-Sun) allowed per week")
    
    # Check for duplicate dates
    entry_dates = [entry.date for entry in weekly_timesheet.entries]
    if len(entry_dates) != len(set(entry_dates)):
        raise HTTPException(status_code=400, detail="Duplicate dates in entries")
    
    # Validate each entry
    total_weekly_hours = 0
    for entry in weekly_timesheet.entries:
        if entry.hours > 8:
            raise HTTPException(status_code=400, detail=f"Cannot log more than 8 hours per day. Date: {entry.date}")
        if entry.hours < 0:
            raise HTTPException(status_code=400, detail=f"Hours cannot be negative. Date: {entry.date}")
        total_weekly_hours += entry.hours
    
    if total_weekly_hours > 40:
        raise HTTPException(status_code=400, detail=f"Total weekly hours ({total_weekly_hours}) cannot exceed 40 hours")
    
    # Create timesheet entries for each day
    created_timesheets = []
    for entry in weekly_timesheet.entries:
        db_timesheet = Timesheet(
            timesheet_id=str(uuid.uuid4()),
            employee_id=current_user.employee_id,
            project_id=weekly_timesheet.project_id,
            task_id=weekly_timesheet.task_id,
            date=entry.date,
            hours=entry.hours,
            description=entry.description,
            status="open"
        )
        db.add(db_timesheet)
        created_timesheets.append(db_timesheet)
    
    db.commit()
    
    # Refresh all entries
    for ts in created_timesheets:
        db.refresh(ts)
    
    # Calculate week end date
    week_end_date = weekly_timesheet.week_start_date + timedelta(days=6)
    
    return WeeklyTimesheetResponse(
        week_start_date=weekly_timesheet.week_start_date,
        week_end_date=week_end_date,
        total_hours=total_weekly_hours,
        entries_created=len(created_timesheets),
        timesheets=created_timesheets
    )

@router.get("/week/{week_start_date}", response_model=List[TimesheetSchema])
def get_week_timesheets(
    week_start_date: date,
    db: Session = Depends(get_db), 
    current_user: UserToken = Depends(get_current_user_token)
):
    """Get all timesheets for a specific week"""
    if week_start_date.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start_date must be a Monday")
    
    week_end_date = week_start_date + timedelta(days=6)
    
    query = db.query(Timesheet).filter(
        Timesheet.date >= week_start_date,
        Timesheet.date <= week_end_date
    )
    
    # Non-admin users can only see their own timesheets
    if current_user.role_name != "admin":
        query = query.filter(Timesheet.employee_id == current_user.user_id)
    
    return query.all()

@router.put("/week/{week_start_date}/submit")
def submit_week_timesheet(
    week_start_date: date,
    db: Session = Depends(get_db), 
    current_user: Employee = Depends(get_current_user)
):
    """Submit all open timesheets for a week"""
    if week_start_date.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start_date must be a Monday")
    
    week_end_date = week_start_date + timedelta(days=6)
    
    timesheets = db.query(Timesheet).filter(
        Timesheet.date >= week_start_date,
        Timesheet.date <= week_end_date,
        Timesheet.employee_id == current_user.employee_id,
        Timesheet.status == "open"
    ).all()
    
    if not timesheets:
        raise HTTPException(status_code=404, detail="No open timesheets found for this week")
    
    for timesheet in timesheets:
        timesheet.status = "submitted"
    
    db.commit()
    
    return {
        "message": f"Submitted {len(timesheets)} timesheets for week starting {week_start_date}",
        "count": len(timesheets)
    }

@router.get("/", response_model=List[TimesheetSchema])
def get_timesheets(db: Session = Depends(get_db), current_user: UserToken = Depends(get_current_user_token)):
    if current_user.role_name == "admin":
        timesheets = db.query(Timesheet).all()
    else:
        timesheets = db.query(Timesheet).filter(Timesheet.employee_id == current_user.user_id).all()
    return timesheets

@router.put("/{timesheet_id}/submit")
def submit_timesheet(timesheet_id: str, db: Session = Depends(get_db), current_user: UserToken = Depends(get_current_user_token)):
    timesheet = db.query(Timesheet).filter(Timesheet.timesheet_id == timesheet_id).first()
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    if timesheet.employee_id != current_user.user_id and current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    timesheet.status = "submitted"
    db.commit()
    return timesheet

@router.put("/{timesheet_id}/approve")
def approve_timesheet(timesheet_id: str, approval: TimesheetApprove, db: Session = Depends(get_db), current_user: UserToken = Depends(get_current_user_token)):
    timesheet = db.query(Timesheet).filter(Timesheet.timesheet_id == timesheet_id).first()
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if current_user.role_name == "employee":
        raise HTTPException(status_code=403, detail="Only managers and admins can approve")
    
    if approval.action == "approved":
        timesheet.status = "approved"
    else:
        timesheet.status = "rejected"
    
    timesheet.approved_by = current_user.user_id
    timesheet.approved_at = datetime.utcnow()
    
    workflow = ApprovalWorkflow(
        request_type="timesheet",
        request_id=timesheet_id,
        approver_id=current_user.user_id,
        action=approval.action,
        remarks=approval.remarks
    )
    db.add(workflow)
    db.commit()
    return timesheet
