from sqlalchemy import Column, String, Integer, Text, Date, DateTime, ForeignKey, Enum, Float, Boolean, text,UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base, generate_uuid
from datetime import datetime
import enum
from sqlalchemy import Sequence
from sqlalchemy import event

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True, nullable=False)
    employees = relationship("Employee", back_populates="role")

class Department(Base):
    __tablename__ = "departments"
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String, unique=True, nullable=False)
    employees = relationship("Employee", back_populates="department")

class RolePolicy(Base):
    __tablename__ = "role_policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=False)

    resource = Column(String(50), nullable=False)   # employees, leave, attendance
    action = Column(String(30), nullable=False)     # view, create, delete, approve, export

    __table_args__ = (
        UniqueConstraint("role_id", "resource", "action", name="uq_role_resource_action"),
    )


class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    employee_code :str = Column(String(64), unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    manager_id = Column(String, ForeignKey("employees.employee_id"), nullable=True)
    join_date = Column(Date, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    department = relationship("Department", back_populates="employees")
    role = relationship("Role", back_populates="employees")
    manager = relationship("Employee", remote_side=[employee_id], foreign_keys=[manager_id])
    leave_requests = relationship("LeaveRequest", foreign_keys="LeaveRequest.employee_id", back_populates="employee")
    leave_balance = relationship("EmployeeLeaveBalance", back_populates="employee")
    attendance = relationship("Attendance", back_populates="employee")
    timesheets = relationship("Timesheet", foreign_keys="Timesheet.employee_id", back_populates="employee")
    approved_leaves = relationship("LeaveRequest", foreign_keys="LeaveRequest.approved_by", back_populates="approver")
    task_assignments = relationship("TaskAssignment", back_populates="employee")

@event.listens_for(Employee, "before_insert")
def generate_employee_code(mapper, connection, target):
    if target.employee_code:
        return

    result = connection.execute(
        text("SELECT employee_code FROM employees ORDER BY created_at DESC LIMIT 1")
    ).fetchone()

    if result and result[0]:
        last_num = int(result[0].replace("EMP", ""))
        next_num = last_num + 1
    else:
        next_num = 1001

    target.employee_code = f"EMP{next_num}"

class LeaveType(Base):
    __tablename__ = "leave_types"
    leave_type_id = Column(Integer, primary_key=True, index=True)
    leave_name = Column(String, nullable=False)
    annual_limit = Column(Integer, default=0)
    monthly_accrual = Column(Float, default=0)
    carry_forward_limit = Column(Integer, default=0)
    is_carry_forward_allowed = Column(Boolean, default=False)
    
    leave_balances = relationship("EmployeeLeaveBalance", back_populates="leave_type")
    leave_requests = relationship("LeaveRequest", back_populates="leave_type")

class EmployeeLeaveBalance(Base):
    __tablename__ = "employee_leave_balance"
    balance_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.employee_id"))
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id"))
    opening_balance = Column(Float, default=0)
    leaves_taken = Column(Float, default=0)
    accrued_this_month = Column(Float, default=0)
    closing_balance = Column(Float, default=0)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    
    employee = relationship("Employee", back_populates="leave_balance")
    leave_type = relationship("LeaveType", back_populates="leave_balances")


class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    id = Column(String, primary_key=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)

    employee = relationship("Employee", backref="employee_roles")
    role = relationship("Role")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    leave_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.employee_id"))
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Float, nullable=False)
    reason = Column(Text)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)
    approved_by = Column(String, ForeignKey("employees.employee_id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_requests")
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    approver = relationship("Employee", foreign_keys=[approved_by], back_populates="approved_leaves")

class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.employee_id"))
    date = Column(Date, nullable=False, index=True)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    total_hours = Column(Float)
    status = Column(String, default="present")
    
    employee = relationship("Employee", back_populates="attendance")

class WeeklyAttendanceSummary(Base):
    __tablename__ = "weekly_attendance_summary"
    summary_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.employee_id"))
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    total_hours = Column(Float, default=0)
    over_time = Column(Float, default=0)

class Project(Base):
    __tablename__ = "projects"
    project_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    project_name = Column(String, nullable=False)
    description = Column(Text)
    client = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="active")
    
    tasks = relationship("Task", back_populates="project")
    employee_projects = relationship("EmployeeProject", back_populates="project")
    timesheets = relationship("Timesheet", back_populates="project")

class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.project_id"))
    task_name = Column(String, nullable=False)
    description = Column(Text)
    
    project = relationship("Project", back_populates="tasks")
    timesheets = relationship("Timesheet", back_populates="task")
    # ADD THIS LINE:
    assignments = relationship("TaskAssignment", back_populates="task")

class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    assignment_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.task_id"), nullable=False)
    employee_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    assigned_date = Column(DateTime, default=datetime.utcnow)
    deadline = Column(Date, nullable=True)
    
    task = relationship("Task", back_populates="assignments")
    employee = relationship("Employee", back_populates="task_assignments")

class EmployeeProject(Base):
    __tablename__ = "employee_projects"
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.employee_id"))
    project_id = Column(String, ForeignKey("projects.project_id"))
    allocation_start = Column(Date)
    allocation_end = Column(Date)
    
    project = relationship("Project", back_populates="employee_projects")

class Timesheet(Base):
    __tablename__ = "timesheets"
    timesheet_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    employee_id = Column(String, ForeignKey("employees.employee_id"))
    project_id = Column(String, ForeignKey("projects.project_id"))
    task_id = Column(String, ForeignKey("tasks.task_id"))
    date = Column(Date, nullable=False)
    hours = Column(Float, nullable=False)
    description = Column(Text)
    status = Column(String, default="open")
    approved_by = Column(String, ForeignKey("employees.employee_id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="timesheets")
    project = relationship("Project", back_populates="timesheets")
    task = relationship("Task", back_populates="timesheets")

class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflow"
    workflow_id = Column(String, primary_key=True, index=True, default=generate_uuid)
    request_type = Column(String, nullable=False)
    request_id = Column(String, nullable=False)
    approver_id = Column(String, ForeignKey("employees.employee_id"))
    action = Column(String, nullable=False)
    action_at = Column(DateTime, default=datetime.utcnow)
    remarks = Column(Text)
