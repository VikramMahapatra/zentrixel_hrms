from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class LeaveAnalyticsResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: str
    department_name: Optional[str]
    total_approved_leaves: int
    total_days_taken: Optional[float]
    pending_requests: int

class LeaveBalanceResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    leave_name: str
    opening_balance: float
    leaves_taken: float
    accrued_this_month: float
    closing_balance: float
    year: int
    month: int

class AttendanceAnalyticsResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: str
    department_name: Optional[str]
    present_days: int
    absent_days: int
    leave_days: int
    avg_hours_per_day: Optional[float]
    total_hours_month: Optional[float]
    total_records: int

class TimesheetAnalyticsResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    department_name: Optional[str]
    project_name: Optional[str]
    total_entries: int
    approved_entries: int
    total_hours: Optional[float]
    approved_hours: Optional[float]
    approval_rate: Optional[float]

class ProjectProductivityResponse(BaseModel):
    project_id: str
    project_name: str
    client: Optional[str]
    team_size: int
    total_hours_logged: Optional[float]
    approved_timesheets: int
    avg_daily_hours: Optional[float]

class DepartmentAnalyticsResponse(BaseModel):
    department_id: int
    department_name: str
    total_employees: int
    active_employees: int
    avg_attendance_hours: Optional[float]
    total_present_days: int

class ComplianceResponse(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    pending_leave_requests: int

class TeamMemberAnalytics(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    total_hours: Optional[float]
    present_days: int

class ManagerTeamAnalyticsResponse(BaseModel):
    team_size: int
    attendance: List[TeamMemberAnalytics]
    leaves: List[dict]
    timesheets: List[dict]

class DashboardSummaryResponse(BaseModel):
    total_employees: int
    active_employees: int
    avg_attendance_rate: float
    pending_approvals: int
    total_projects: int
    total_hours_logged: float
    timesheet_completion_rate: float
