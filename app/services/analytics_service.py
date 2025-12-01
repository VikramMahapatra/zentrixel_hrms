from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, date
from app.models import (
    Employee, LeaveRequest, Attendance, Timesheet, WeeklyAttendanceSummary,
    Project, Task, EmployeeLeaveBalance, LeaveType, Department
)
from app.security import get_current_user

class AnalyticsService:
    """Comprehensive analytics service for Leave, Attendance, and Timesheet data"""
    
    @staticmethod
    def get_leave_analytics(db: Session, employee_id: str = None, department_id: int = None):
        """Get leave utilization analytics"""
        query = db.query(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Department.department_name,
            func.count(LeaveRequest.leave_id).filter(
                LeaveRequest.status == 'approved'
            ).label('total_approved_leaves'),
            func.sum(LeaveRequest.total_days).filter(
                LeaveRequest.status == 'approved'
            ).label('total_days_taken'),
            func.count(LeaveRequest.leave_id).filter(
                LeaveRequest.status == 'pending'
            ).label('pending_requests'),
        ).outerjoin(
            LeaveRequest, Employee.employee_id == LeaveRequest.employee_id
        ).outerjoin(
            Department, Employee.department_id == Department.department_id
        ).group_by(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Department.department_name
        )
        
        if employee_id:
            query = query.filter(Employee.employee_id == employee_id)
        if department_id:
            query = query.filter(Employee.department_id == department_id)
            
        return query.all()
    
    @staticmethod
    def get_leave_balance_analytics(db: Session, employee_id: str = None):
        """Get detailed leave balance by type"""
        query = db.query(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            LeaveType.leave_name,
            EmployeeLeaveBalance.opening_balance,
            EmployeeLeaveBalance.leaves_taken,
            EmployeeLeaveBalance.accrued_this_month,
            EmployeeLeaveBalance.closing_balance,
            EmployeeLeaveBalance.year,
            EmployeeLeaveBalance.month
        ).join(
            EmployeeLeaveBalance, Employee.employee_id == EmployeeLeaveBalance.employee_id
        ).join(
            LeaveType, EmployeeLeaveBalance.leave_type_id == LeaveType.leave_type_id
        ).filter(
            EmployeeLeaveBalance.year == datetime.now().year
        )
        
        if employee_id:
            query = query.filter(Employee.employee_id == employee_id)
            
        return query.all()
    
    @staticmethod
    def get_attendance_analytics(db: Session, employee_id: str = None, department_id: int = None, days: int = 30):
        """Get attendance patterns and statistics"""
        start_date = date.today() - timedelta(days=days)
        
        query = db.query(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Department.department_name,
            func.count(Attendance.attendance_id).filter(
                Attendance.status == 'present'
            ).label('present_days'),
            func.count(Attendance.attendance_id).filter(
                Attendance.status == 'absent'
            ).label('absent_days'),
            func.count(Attendance.attendance_id).filter(
                Attendance.status == 'leave'
            ).label('leave_days'),
            func.avg(Attendance.total_hours).label('avg_hours_per_day'),
            func.sum(Attendance.total_hours).label('total_hours_month'),
            func.count(Attendance.attendance_id).label('total_records')
        ).outerjoin(
            Attendance, and_(
                Employee.employee_id == Attendance.employee_id,
                Attendance.date >= start_date
            )
        ).outerjoin(
            Department, Employee.department_id == Department.department_id
        ).group_by(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Employee.email,
            Department.department_name
        )
        
        if employee_id:
            query = query.filter(Employee.employee_id == employee_id)
        if department_id:
            query = query.filter(Employee.department_id == department_id)
            
        return query.all()
    
    @staticmethod
    def get_timesheet_analytics(db: Session, employee_id: str = None, department_id: int = None, days: int = 30):
        """Get timesheet completion and project allocation analytics"""
        start_date = date.today() - timedelta(days=days)
        
        query = db.query(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Department.department_name,
            Project.project_name,
            func.count(Timesheet.timesheet_id).label('total_entries'),
            func.count(Timesheet.timesheet_id).filter(
                Timesheet.status == 'approved'
            ).label('approved_entries'),
            func.sum(Timesheet.hours).label('total_hours'),
            func.sum(Timesheet.hours).filter(
                Timesheet.status == 'approved'
            ).label('approved_hours'),
            (func.count(Timesheet.timesheet_id).filter(
                Timesheet.status == 'approved'
            ) * 100.0 / func.count(Timesheet.timesheet_id)).label('approval_rate')
        ).outerjoin(
            Timesheet, and_(
                Employee.employee_id == Timesheet.employee_id,
                Timesheet.date >= start_date
            )
        ).outerjoin(
            Project, Timesheet.project_id == Project.project_id
        ).outerjoin(
            Department, Employee.department_id == Department.department_id
        ).group_by(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Department.department_name,
            Project.project_name
        )
        
        if employee_id:
            query = query.filter(Employee.employee_id == employee_id)
        if department_id:
            query = query.filter(Employee.department_id == department_id)
            
        return query.all()
    
    @staticmethod
    def get_project_productivity_analytics(db: Session, project_id: str = None):
        """Get project-wise productivity and resource allocation"""
        query = db.query(
            Project.project_id,
            Project.project_name,
            Project.client,
            func.count(Employee.employee_id).label('team_size'),
            func.sum(Timesheet.hours).label('total_hours_logged'),
            func.count(Timesheet.timesheet_id).filter(
                Timesheet.status == 'approved'
            ).label('approved_timesheets'),
            func.avg(Timesheet.hours).label('avg_daily_hours')
        ).outerjoin(
            Timesheet, Project.project_id == Timesheet.project_id
        ).outerjoin(
            Employee, Timesheet.employee_id == Employee.employee_id
        ).group_by(
            Project.project_id,
            Project.project_name,
            Project.client
        )
        
        if project_id:
            query = query.filter(Project.project_id == project_id)
            
        return query.all()
    
    @staticmethod
    def get_department_analytics(db: Session, department_id: int = None):
        """Get department-wise consolidated analytics"""
        query = db.query(
            Department.department_id,
            Department.department_name,
            func.count(Employee.employee_id).label('total_employees'),
            func.count(Employee.employee_id).filter(
                Employee.status == 'active'
            ).label('active_employees'),
            func.avg(Attendance.total_hours).label('avg_attendance_hours'),
            func.count(Attendance.attendance_id).filter(
                Attendance.status == 'present'
            ).label('total_present_days')
        ).outerjoin(
            Employee, Department.department_id == Employee.department_id
        ).outerjoin(
            Attendance, Employee.employee_id == Attendance.employee_id
        ).group_by(
            Department.department_id,
            Department.department_name
        )
        
        if department_id:
            query = query.filter(Department.department_id == department_id)
            
        return query.all()
    
    @staticmethod
    def get_compliance_analytics(db: Session, employee_id: str = None):
        """Get compliance metrics - pending approvals, overdue timesheets"""
        pending_leaves = db.query(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            func.count(LeaveRequest.leave_id).label('pending_leave_requests')
        ).outerjoin(
            LeaveRequest, and_(
                Employee.employee_id == LeaveRequest.employee_id,
                LeaveRequest.status == 'submitted'
            )
        ).group_by(
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name
        )
        
        if employee_id:
            pending_leaves = pending_leaves.filter(Employee.employee_id == employee_id)
        
        return pending_leaves.all()
    
    @staticmethod
    def get_manager_team_analytics(db: Session, manager_id: str):
        """Get analytics for all employees managed by a specific manager"""
        employees = db.query(Employee.employee_id).filter(
            Employee.manager_id == manager_id,
            Employee.status == 'active'
        ).all()
        
        emp_ids = [emp.employee_id for emp in employees]
        
        if not emp_ids:
            return {
                "team_size": 0,
                "attendance": [],
                "leaves": [],
                "timesheets": []
            }
        
        return {
            "team_size": len(emp_ids),
            "attendance": db.query(
                Employee.employee_id,
                Employee.first_name,
                Employee.last_name,
                func.sum(Attendance.total_hours).label('total_hours'),
                func.count(Attendance.attendance_id).filter(
                    Attendance.status == 'present'
                ).label('present_days')
            ).filter(
                Employee.employee_id.in_(emp_ids)
            ).outerjoin(
                Attendance, Employee.employee_id == Attendance.employee_id
            ).group_by(
                Employee.employee_id,
                Employee.first_name,
                Employee.last_name
            ).all(),
            "leaves": db.query(
                Employee.employee_id,
                Employee.first_name,
                func.count(LeaveRequest.leave_id).filter(
                    LeaveRequest.status == 'approved'
                ).label('approved_leaves'),
                func.count(LeaveRequest.leave_id).filter(
                    LeaveRequest.status == 'submitted'
                ).label('pending_leaves')
            ).filter(
                Employee.employee_id.in_(emp_ids)
            ).outerjoin(
                LeaveRequest, Employee.employee_id == LeaveRequest.employee_id
            ).group_by(
                Employee.employee_id,
                Employee.first_name
            ).all(),
            "timesheets": db.query(
                Employee.employee_id,
                Employee.first_name,
                func.count(Timesheet.timesheet_id).label('total_entries'),
                func.sum(Timesheet.hours).label('total_hours'),
                func.count(Timesheet.timesheet_id).filter(
                    Timesheet.status == 'approved'
                ).label('approved_entries')
            ).filter(
                Employee.employee_id.in_(emp_ids)
            ).outerjoin(
                Timesheet, Employee.employee_id == Timesheet.employee_id
            ).group_by(
                Employee.employee_id,
                Employee.first_name
            ).all()
        }
