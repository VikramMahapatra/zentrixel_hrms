from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Department, Employee
from app.schemas import Department as DepartmentSchema, DepartmentBase
from app.security import get_current_user

router = APIRouter()

def check_admin(current_user: Employee = Depends(get_current_user)):
    if current_user.role.role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    return current_user

@router.get("/", response_model=List[DepartmentSchema])
def get_all_departments(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    departments = db.query(Department).all()
    return departments

@router.post("/", response_model=DepartmentSchema)
def create_department(department: DepartmentBase, db: Session = Depends(get_db), admin: Employee = Depends(check_admin)):
    db_department = db.query(Department).filter(Department.department_name == department.department_name).first()
    if db_department:
        raise HTTPException(status_code=400, detail="Department already exists")
    db_department = Department(department_name=department.department_name)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department
