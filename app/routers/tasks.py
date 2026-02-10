from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Task, Project, Employee,TaskAssignment
from app.schemas import Task as TaskSchema, TaskAssignmentCreate, TaskAssignmentSchema, TaskBase, TaskWithAssignments
from app.security import get_current_user
# Change 1: Import UserToken and token dependencies
from app.schemas import UserToken
from app.security import get_current_user_token, is_admin
from sqlalchemy.orm import joinedload
from app.security import has_role



router = APIRouter()

"""def check_manager_or_admin(current_user: UserToken = Depends(get_current_user_token)):
    if current_user.role_name not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only managers and admins can manage tasks")
    return current_user"""
"""
@router.get("/project/{project_id}", response_model=List[TaskSchema])
def get_project_tasks(project_id: str, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks"""

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskBase, db: Session = Depends(get_db), user = Depends(has_role(["manager", "admin"]))):
    project = db.query(Project).filter(Project.project_id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/project/{project_id}", response_model=List[TaskWithAssignments])
def get_project_tasks(
    project_id: str,
    show_all: bool = False,  # NEW: Checkbox parameter (default: False = show only assigned)
    db: Session = Depends(get_db),
    current_user: UserToken = Depends(get_current_user_token)
):
    """Get tasks for a project - Employees see assigned only, can toggle to see all"""
    
    # Base query
    query = db.query(Task).options(joinedload(Task.assignments)).filter(Task.project_id == project_id)
    
    # Admin/Manager always sees all tasks
    if any(role in current_user.roles for role in ["admin", "manager"]):

        tasks = query.all()
    else:
        # Employee logic:
        if show_all:
            # Employee wants to see ALL tasks (checkbox checked)
            tasks = query.all()
        else:
            # Employee sees only assigned tasks (default)
            tasks = (
                query.join(TaskAssignment, TaskAssignment.task_id == Task.task_id)
                .filter(TaskAssignment.employee_id == current_user.employee_id)
                .all()
            )
    
    # Add is_assigned_to_me flag
    result = []
    for task in tasks:
        task_dict = task.__dict__.copy()
        task_dict["assignments"] = task.assignments
        
        # Get employee names for assignments
        employee_names = []
        for assignment in task.assignments:
            employee = db.query(Employee).filter(Employee.employee_id == assignment.employee_id).first()
            if employee:
                employee_names.append(f"{employee.first_name} {employee.last_name}")
        
        # Find if assigned to current user
        user_assignment = next(
            (a for a in task.assignments if a.employee_id == current_user.employee_id), 
            None
        )
        
        task_dict.update({
            "is_assigned_to_me": user_assignment is not None,
            "assigned_employee_names": employee_names,
            "project_name": task.project.project_name if task.project else None,
            "employee_deadline": user_assignment.deadline if user_assignment else None,
        })
        
        result.append(TaskWithAssignments(**task_dict))
    
    return result


@router.post("/assign", response_model=TaskAssignmentSchema)
def assign_task_to_employee(
    assignment: TaskAssignmentCreate,
    db: Session = Depends(get_db),
    user = Depends(has_role(["manager", "admin"]))
):
        
    task = db.query(Task).filter(Task.task_id == assignment.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    employee = db.query(Employee).filter(Employee.employee_id == assignment.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    existing = db.query(TaskAssignment).filter(
        TaskAssignment.task_id == assignment.task_id,
        TaskAssignment.employee_id == assignment.employee_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Employee already assigned to this task")
    
    db_assignment = TaskAssignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.delete("/assignments/{assignment_id}")
def remove_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    user = Depends(has_role(["manager", "admin"]))
):
     
    assignment = db.query(TaskAssignment).filter(TaskAssignment.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment removed"}
