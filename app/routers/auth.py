from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Employee
from app.schemas import EmployeeCreate, TokenResponse, Employee as EmployeeSchema
from app.security import verify_password, get_password_hash, create_access_token, get_current_user
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=EmployeeSchema)
def register(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_employee = db.query(Employee).filter(Employee.employee_code == employee.employee_code).first()
    if db_employee:
        raise HTTPException(status_code=400, detail="Employee code already exists")
    
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

"""@router.post("/login", response_model=TokenResponse)
def login(email: str, password: str, db: Session = Depends(get_db)):
     # IMPORTANT: Join with role to get role_name
    employee = db.query(Employee).join(Employee.role).filter(Employee.email == email).first()
    if not employee or not verify_password(password, employee.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=80)
    access_token = create_access_token(
        data={"sub": employee.email}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token, user=employee)"""

@router.post("/login", response_model=TokenResponse)
def login(email: str, password: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).join(Employee.role).filter(Employee.email == email).first()
    
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(password, employee.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token data
    token_data = {
        "sub": employee.email,
        "user_id": employee.employee_id,
        "email": employee.email,
        "role_id": employee.role_id,
        "role_name": employee.role.role_name
    }
    
    # Use create_access_token with your 80 minutes expiry
    access_token_expires = timedelta(minutes=80)
    access_token = create_access_token(
        data=token_data, 
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token, user=employee)

@router.get("/me", response_model=EmployeeSchema)
def get_current_user_info(current_user: Employee = Depends(get_current_user)):
    return current_user
