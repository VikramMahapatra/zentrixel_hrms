from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Task, Project, Employee
from app.schemas import Task as TaskSchema, TaskBase
from app.security import get_current_user

router = APIRouter()

def check_manager_or_admin(current_user: Employee = Depends(get_current_user)):
    if current_user.role.role_name not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only managers and admins can manage tasks")
    return current_user

@router.get("/project/{project_id}", response_model=List[TaskSchema])
def get_project_tasks(project_id: str, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return tasks

@router.post("/", response_model=TaskSchema)
def create_task(task: TaskBase, db: Session = Depends(get_db), manager: Employee = Depends(check_manager_or_admin)):
    project = db.query(Project).filter(Project.project_id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
