from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Employee,EmployeeRole, Role
from app.schemas import EmployeeCreate, TokenResponse, Employee as EmployeeSchema
from app.security import verify_password, get_password_hash, create_access_token, get_current_user
from datetime import timedelta
from app.models import RolePolicy
from app.models import EmployeeRole



router = APIRouter()

@router.post("/register", response_model=EmployeeSchema)
def register(employee: EmployeeCreate, db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.email == employee.email).first():
        raise HTTPException(400, "Email already registered")

    hashed_password = get_password_hash(employee.password)

    db_employee = Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        password_hash=hashed_password,
        department_id=employee.department_id,
        role_id=employee.role_id,  # legacy
        manager_id=employee.manager_id,
        join_date=employee.join_date
    )

    db.add(db_employee)
    db.flush()  # 🔥 generates employee_id without commit

    db.add(
        EmployeeRole(
            employee_id=db_employee.employee_id,
            role_id=employee.role_id
        )
    )

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
    employee = db.query(Employee).filter(Employee.email == email).first()
    
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(password, employee.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
   # 🔥 FETCH ROLES
    roles = (
        db.query(Role.role_name, Role.role_id)
        .join(EmployeeRole, EmployeeRole.role_id == Role.role_id)
        .filter(EmployeeRole.employee_id == employee.employee_id)
        .all()
    )

    role_names = [r[0] for r in roles]
    role_ids = [r[1] for r in roles]

    # 🔥 FETCH ROLE POLICIES → PERMISSIONS
    policies = (
        db.query(RolePolicy.resource, RolePolicy.action)
        .filter(RolePolicy.role_id.in_(role_ids))
        .all()
    )

    permissions = list({f"{r}:{a}" for r, a in policies})

    # 🔥 JWT PAYLOAD
    token_data = {
        "sub": employee.email,
        "employee_id": employee.employee_id,
        "email": employee.email,
        "roles": role_names,
        "permissions": permissions
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=80)
    )

    return TokenResponse(access_token=access_token, user=employee)


@router.get("/me", response_model=EmployeeSchema)
def get_current_user_info(current_user: Employee = Depends(get_current_user)):
    return current_user
