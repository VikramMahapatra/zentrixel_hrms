from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import get_current_user, is_admin, is_manager_or_admin
from app.security import get_current_user, has_role

from app.models import Employee
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics_schema import (
    LeaveAnalyticsResponse, LeaveBalanceResponse, AttendanceAnalyticsResponse,
    TimesheetAnalyticsResponse, ProjectProductivityResponse, DepartmentAnalyticsResponse,
    ComplianceResponse, ManagerTeamAnalyticsResponse
)
from typing import List

router = APIRouter()

# EMPLOYEE ANALYTICS - Personal data only
@router.get("/personal/leave", response_model=List[LeaveAnalyticsResponse], tags=["Analytics - Personal"])
def get_personal_leave_analytics(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get personal leave analytics"""
    result = AnalyticsService.get_leave_analytics(db, employee_id=current_user.employee_id)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "email": r[3],
            "department_name": r[4],
            "total_approved_leaves": r[5] or 0,
            "total_days_taken": r[6] or 0,
            "pending_requests": r[7] or 0
        }
        for r in result
    ]

@router.get("/personal/attendance", response_model=List[AttendanceAnalyticsResponse], tags=["Analytics - Personal"])
def get_personal_attendance_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get personal attendance analytics for the last N days"""
    result = AnalyticsService.get_attendance_analytics(db, employee_id=current_user.employee_id, days=days)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "email": r[3],
            "department_name": r[4],
            "present_days": r[5] or 0,
            "absent_days": r[6] or 0,
            "leave_days": r[7] or 0,
            "avg_hours_per_day": r[8],
            "total_hours_month": r[9],
            "total_records": r[10] or 0
        }
        for r in result
    ]

@router.get("/personal/timesheet", response_model=List[TimesheetAnalyticsResponse], tags=["Analytics - Personal"])
def get_personal_timesheet_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get personal timesheet analytics"""
    result = AnalyticsService.get_timesheet_analytics(db, employee_id=current_user.employee_id, days=days)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "department_name": r[3],
            "project_name": r[4],
            "total_entries": r[5] or 0,
            "approved_entries": r[6] or 0,
            "total_hours": r[7],
            "approved_hours": r[8],
            "approval_rate": r[9] or 0
        }
        for r in result
    ]

# MANAGER ANALYTICS - Team members only
@router.get("/team/overview", response_model=ManagerTeamAnalyticsResponse, tags=["Analytics - Manager"])
def get_team_overview(
    db: Session = Depends(get_db),
    user = Depends(has_role(["manager", "admin"])),
    current_user: Employee = Depends(get_current_user)

):
    """Get consolidated analytics for all team members managed by this manager"""
    result = AnalyticsService.get_manager_team_analytics(db, current_user.employee_id)
    return result

@router.get("/team/attendance", response_model=List[AttendanceAnalyticsResponse], tags=["Analytics - Manager"])
def get_team_attendance_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user = Depends(has_role(["manager", "admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """Get attendance analytics for all managed team members"""
    result = AnalyticsService.get_attendance_analytics(db, department_id=current_user.department_id, days=days)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "email": r[3],
            "department_name": r[4],
            "present_days": r[5] or 0,
            "absent_days": r[6] or 0,
            "leave_days": r[7] or 0,
            "avg_hours_per_day": r[8],
            "total_hours_month": r[9],
            "total_records": r[10] or 0
        }
        for r in result
    ]

@router.get("/team/leaves", response_model=List[LeaveAnalyticsResponse], tags=["Analytics - Manager"])
def get_team_leave_analytics(
    db: Session = Depends(get_db),
    user = Depends(has_role(["manager", "admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """Get leave analytics for all managed team members"""
    result = AnalyticsService.get_leave_analytics(db, department_id=current_user.department_id)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "email": r[3],
            "department_name": r[4],
            "total_approved_leaves": r[5] or 0,
            "total_days_taken": r[6] or 0,
            "pending_requests": r[7] or 0
        }
        for r in result
    ]

@router.get("/team/timesheets", response_model=List[TimesheetAnalyticsResponse], tags=["Analytics - Manager"])
def get_team_timesheet_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user = Depends(has_role(["manager", "admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """Get timesheet analytics for all managed team members"""
    result = AnalyticsService.get_timesheet_analytics(db, department_id=current_user.department_id, days=days)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "department_name": r[3],
            "project_name": r[4],
            "total_entries": r[5] or 0,
            "approved_entries": r[6] or 0,
            "total_hours": r[7],
            "approved_hours": r[8],
            "approval_rate": r[9] or 0
        }
        for r in result
    ]

# ADMIN ANALYTICS - System-wide data
@router.get("/admin/leave-summary", response_model=List[LeaveAnalyticsResponse], tags=["Analytics - Admin"])
def get_admin_leave_summary(
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """[ADMIN] Get leave analytics for all employees"""
    result = AnalyticsService.get_leave_analytics(db)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "email": r[3],
            "department_name": r[4],
            "total_approved_leaves": r[5] or 0,
            "total_days_taken": r[6] or 0,
            "pending_requests": r[7] or 0
        }
        for r in result
    ]

@router.get("/admin/leave-balance", response_model=List[LeaveBalanceResponse], tags=["Analytics - Admin"])
def get_admin_leave_balance(
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """[ADMIN] Get detailed leave balance for all employees by type"""
    result = AnalyticsService.get_leave_balance_analytics(db)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "leave_name": r[3],
            "opening_balance": r[4] or 0,
            "leaves_taken": r[5] or 0,
            "accrued_this_month": r[6] or 0,
            "closing_balance": r[7] or 0,
            "year": r[8],
            "month": r[9]
        }
        for r in result
    ]

@router.get("/admin/attendance-summary", response_model=List[AttendanceAnalyticsResponse], tags=["Analytics - Admin"])
def get_admin_attendance_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """[ADMIN] Get attendance analytics for all employees"""
    result = AnalyticsService.get_attendance_analytics(db, days=days)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "email": r[3],
            "department_name": r[4],
            "present_days": r[5] or 0,
            "absent_days": r[6] or 0,
            "leave_days": r[7] or 0,
            "avg_hours_per_day": r[8],
            "total_hours_month": r[9],
            "total_records": r[10] or 0
        }
        for r in result
    ]

@router.get("/admin/timesheet-summary", response_model=List[TimesheetAnalyticsResponse], tags=["Analytics - Admin"])
def get_admin_timesheet_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """[ADMIN] Get timesheet analytics for all employees"""
    result = AnalyticsService.get_timesheet_analytics(db, days=days)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "department_name": r[3],
            "project_name": r[4],
            "total_entries": r[5] or 0,
            "approved_entries": r[6] or 0,
            "total_hours": r[7],
            "approved_hours": r[8],
            "approval_rate": r[9] or 0
        }
        for r in result
    ]

@router.get("/admin/project-productivity", response_model=List[ProjectProductivityResponse], tags=["Analytics - Admin"])
def get_admin_project_productivity(
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """[ADMIN] Get project-wise productivity metrics"""
    result = AnalyticsService.get_project_productivity_analytics(db)
    return [
        {
            "project_id": r[0],
            "project_name": r[1],
            "client": r[2],
            "team_size": r[3] or 0,
            "total_hours_logged": r[4],
            "approved_timesheets": r[5] or 0,
            "avg_daily_hours": r[6]
        }
        for r in result
    ]

@router.get("/admin/department-summary", response_model=List[DepartmentAnalyticsResponse], tags=["Analytics - Admin"])
def get_admin_department_summary(
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """[ADMIN] Get department-wise consolidated analytics"""
    result = AnalyticsService.get_department_analytics(db)
    return [
        {
            "department_id": r[0],
            "department_name": r[1],
            "total_employees": r[2] or 0,
            "active_employees": r[3] or 0,
            "avg_attendance_hours": r[4],
            "total_present_days": r[5] or 0
        }
        for r in result
    ]

@router.get("/admin/compliance", response_model=List[ComplianceResponse], tags=["Analytics - Admin"])
def get_admin_compliance_metrics(
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"])),
    current_user: Employee = Depends(get_current_user)
):
    """[ADMIN] Get compliance metrics - pending approvals, overdue items"""
    result = AnalyticsService.get_compliance_analytics(db)
    return [
        {
            "employee_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "pending_leave_requests": r[3] or 0
        }
        for r in result
    ]
