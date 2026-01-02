from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Project, Employee, EmployeeProject
from app.schemas import Project as ProjectSchema, ProjectBase
from app.security import get_current_user
# Change 1: Import UserToken and token dependencies
from app.schemas import UserToken
from app.security import get_current_user_token, is_admin


router = APIRouter()

def check_manager_or_admin(current_user: UserToken = Depends(get_current_user_token)):
    if current_user.role_name not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only managers and admins can manage projects")
    return current_user

@router.get("/", response_model=List[ProjectSchema])
def get_all_projects(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    projects = db.query(Project).all()
    return projects

@router.post("/", response_model=ProjectSchema)
def create_project(project: ProjectBase, db: Session = Depends(get_db), manager: UserToken = Depends(check_manager_or_admin)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/{project_id}/assign-employee")
def assign_employee_to_project(project_id: str, employee_id: str, allocation_start, allocation_end, db: Session = Depends(get_db), manager: UserToken = Depends(check_manager_or_admin)):
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    emp_project = EmployeeProject(
        employee_id=employee_id,
        project_id=project_id,
        allocation_start=allocation_start,
        allocation_end=allocation_end
    )
    db.add(emp_project)
    db.commit()
    return {"message": "Employee assigned to project"}
