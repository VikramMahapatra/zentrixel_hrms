from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List

# Role Schemas
class RoleBase(BaseModel):
	role_name: str

class RoleCreate(RoleBase):
	pass

class Role(RoleBase):
	role_id: int
	class Config:
		from_attributes = True

# Department Schemas
class DepartmentBase(BaseModel):
	department_name: str

class Department(DepartmentBase):
	department_id: int
	class Config:
		from_attributes = True

# Employee Schemas
class EmployeeBase(BaseModel):
	employee_code: str
	first_name: str
	last_name: str
	email: EmailStr
	department_id: int
	role_id: int
	manager_id: Optional[str] = None
	join_date: date

class EmployeeCreate(EmployeeBase):
	password: str

class EmployeeUpdate(BaseModel):
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	department_id: Optional[int] = None
	role_id: Optional[int] = None
	manager_id: Optional[str] = None
	status: Optional[str] = None

class Employee(EmployeeBase):
	employee_id: str
	status: str
	created_at: datetime
	class Config:
		from_attributes = True

# Leave Type Schemas
class LeaveTypeBase(BaseModel):
	leave_name: str
	annual_limit: int = 0
	monthly_accrual: float = 0
	carry_forward_limit: int = 0
	is_carry_forward_allowed: bool = False

class LeaveType(LeaveTypeBase):
	leave_type_id: int
	class Config:
		from_attributes = True

# Leave Request Schemas
class LeaveRequestBase(BaseModel):
	leave_type_id: int
	start_date: date
	end_date: date
	reason: Optional[str] = None

class LeaveRequestCreate(LeaveRequestBase):
	pass

class LeaveRequestApprove(BaseModel):
	action: str  # approved or rejected
	remarks: Optional[str] = None

class LeaveRequest(LeaveRequestBase):
	leave_id: str
	employee_id: str
	total_days: float
	status: str
	created_at: datetime
	submitted_at: Optional[datetime] = None
	approved_at: Optional[datetime] = None
	class Config:
		from_attributes = True

# Attendance Schemas
class AttendanceBase(BaseModel):
	date: date
	check_in: Optional[datetime] = None
	check_out: Optional[datetime] = None
	status: str = "present"

class AttendanceCreate(AttendanceBase):
	pass

class Attendance(AttendanceBase):
	attendance_id: str
	employee_id: str
	total_hours: Optional[float] = None
	class Config:
		from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
	project_name: str
	description: Optional[str] = None
	client: Optional[str] = None
	start_date: Optional[date] = None
	end_date: Optional[date] = None
	status: str = "active"

class Project(ProjectBase):
	project_id: str
	class Config:
		from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
	project_id: str
	task_name: str
	description: Optional[str] = None

class Task(TaskBase):
	task_id: str
	class Config:
		from_attributes = True

# Timesheet Schemas
class TimesheetBase(BaseModel):
	project_id: str
	task_id: str
	date: date
	hours: float
	description: Optional[str] = None

class TimesheetCreate(TimesheetBase):
	pass

class TimesheetApprove(BaseModel):
	action: str  # approved or rejected
	remarks: Optional[str] = None

class Timesheet(TimesheetBase):
	timesheet_id: str
	employee_id: str
	status: str
	approved_by: Optional[str] = None
	approved_at: Optional[datetime] = None
	class Config:
		from_attributes = True

# New schemas for bulk weekly timesheet entry
class DailyTimesheetEntry(BaseModel):
	"""Individual day entry for weekly timesheet"""
	date: date
	hours: float
	description: Optional[str] = None

class WeeklyTimesheetCreate(BaseModel):
	"""Bulk timesheet entry for an entire week"""
	project_id: str
	task_id: str
	week_start_date: date  # Monday of the week
	entries: List[DailyTimesheetEntry]  # 5-7 entries for weekdays
    
class WeeklyTimesheetResponse(BaseModel):
	"""Response after bulk weekly timesheet creation"""
	week_start_date: date
	week_end_date: date
	total_hours: float
	entries_created: int
	timesheets: List[Timesheet]

# Authentication Schemas
class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"
	user: Employee

# Analytics schemas
from .analytics_schema import *
