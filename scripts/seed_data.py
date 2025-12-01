"""
Standalone script to seed the HRMS database with Indian employee data.
Run this script independently to populate the database.

Usage: python scripts/seed_data.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.seeds import seed_database
from app.models import Role, Department, LeaveType

def main():
    print("=" * 60)
    print("HRMS Database Seeding Script")
    print("=" * 60)
    
    # Create tables
    print("\n1. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")
    
    # Initialize base data (roles, departments, leave types)
    print("\n2. Initializing base configuration...")
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
            print("✓ Roles created")
        
        # Add default departments if not exist
        if db.query(Department).count() == 0:
            departments = [
                Department(department_name="Engineering"),
                Department(department_name="Sales"),
                Department(department_name="HR"),
                Department(department_name="Finance"),
            ]
            db.add_all(departments)
            print("✓ Departments created")
        
        # Add default leave types if not exist
        if db.query(LeaveType).count() == 0:
            leave_types = [
                LeaveType(
                    leave_name="Casual",
                    annual_limit=12,
                    monthly_accrual=1,
                    is_carry_forward_allowed=True,
                    carry_forward_limit=5
                ),
                LeaveType(
                    leave_name="Sick",
                    annual_limit=10,
                    monthly_accrual=0.83,
                    is_carry_forward_allowed=False
                ),
                LeaveType(
                    leave_name="Earned",
                    annual_limit=20,
                    monthly_accrual=1.67,
                    is_carry_forward_allowed=True,
                    carry_forward_limit=10
                ),
            ]
            db.add_all(leave_types)
            print("✓ Leave types configured")
        
        db.commit()
    finally:
        db.close()
    
    # Seed employee and project data
    print("\n3. Seeding employee and project data...")
    seed_database()
    
    print("\n" + "=" * 60)
    print("Database seeding completed successfully!")
    print("=" * 60)
    print("\n📋 Sample Credentials:")
    print("   Admin: admin@hrms.com / admin123")
    print("   Employee: samyak.verma@hrms.com / password123")
    print("   Manager: prachi.sharma@hrms.com / password123")
    print("\n🚀 Start the server with: python run.py")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
