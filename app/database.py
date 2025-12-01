from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import uuid

# Database setup
DATABASE_URL = "sqlite:///./hrms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_uuid():
    return str(uuid.uuid4())

def init_db(engine):
    """Initialize database with sample data"""
    from app.models import Role, Department, LeaveType
    db = SessionLocal()
    
    try:
        # Add default roles if not exist
        if db.query(Role).count() == 0:
            roles = [
                Role(role_name="admin"),
                Role(role_name="manager"),
                Role(role_name="employee"),
            ]
            db.add_all(roles)
        
        # Add default departments if not exist
        if db.query(Department).count() == 0:
            departments = [
                Department(department_name="Engineering"),
                Department(department_name="Sales"),
                Department(department_name="HR"),
                Department(department_name="Finance"),
            ]
            db.add_all(departments)
        
        # Add default leave types if not exist
        if db.query(LeaveType).count() == 0:
            leave_types = [
                LeaveType(leave_name="Casual", annual_limit=12, monthly_accrual=1, is_carry_forward_allowed=True, carry_forward_limit=5),
                LeaveType(leave_name="Sick", annual_limit=10, monthly_accrual=0.83, is_carry_forward_allowed=False),
                LeaveType(leave_name="Earned", annual_limit=20, monthly_accrual=1.67, is_carry_forward_allowed=True, carry_forward_limit=10),
            ]
            db.add_all(leave_types)
        
        db.commit()
        
        from app.seeds import seed_database
        seed_database()
        
    finally:
        db.close()
