from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Employee
from app.schemas import Employee as EmployeeSchema, EmployeeCreate, EmployeeUpdate, UserToken
from app.security import get_current_user, get_current_user_token, get_password_hash

router = APIRouter()

def check_admin(current_user: UserToken = Depends(get_current_user_token)):
    if current_user.role_name != "admin":
        raise HTTPException(status_code=403, detail="Only admin can perform this action")
    return current_user

@router.get("/", response_model=List[EmployeeSchema])
def get_all_employees(db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    employees = db.query(Employee).all()
    return employees

@router.get("/{employee_id}", response_model=EmployeeSchema)
def get_employee(employee_id: str, db: Session = Depends(get_db), current_user: Employee = Depends(get_current_user)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/", response_model=EmployeeSchema)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db), admin: UserToken = Depends(check_admin)):# Changed to UserToken
    db_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(employee.password)
    db_employee = Employee(
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        password_hash=hashed_password,
        department_id=employee.department_id,
        role_id=employee.role_id,
        manager_id=employee.manager_id,
        join_date=employee.join_date
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.put("/{employee_id}", response_model=EmployeeSchema)
def update_employee(employee_id: str, employee: EmployeeUpdate, db: Session = Depends(get_db), admin:UserToken  = Depends(check_admin)):# Changed to UserToken
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee.first_name is not None:
        db_employee.first_name = employee.first_name
    if employee.last_name is not None:
        db_employee.last_name = employee.last_name
    if employee.department_id is not None:
        db_employee.department_id = employee.department_id
    if employee.role_id is not None:
        db_employee.role_id = employee.role_id
    if employee.manager_id is not None:
        db_employee.manager_id = employee.manager_id
    if employee.status is not None:
        db_employee.status = employee.status
    
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: str, db: Session = Depends(get_db), admin: UserToken = Depends(check_admin)):# Changed to UserToken
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_employee)
    db.commit()
    return None
