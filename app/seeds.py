"""
Seed data for HRMS with Indian employee names
"""
from datetime import datetime, date, timedelta
from app.models import (
    Employee, Role, Department, LeaveType, Project, Task, 
    EmployeeProject, EmployeeLeaveBalance
)
from app.security import get_password_hash
from app.database import SessionLocal, generate_uuid
import random

# Indian employee data
INDIAN_EMPLOYEES = [
    {
        "first_name": "Samyak",
        "last_name": "Verma",
        "email": "samyak.verma@hrms.com",
        "department": "Engineering",
        "role": "employee",
    },
    {
        "first_name": "Prachi",
        "last_name": "Sharma",
        "email": "prachi.sharma@hrms.com",
        "department": "Engineering",
        "role": "manager",
    },
    {
        "first_name": "Bhushan",
        "last_name": "Desai",
        "email": "bhushan.desai@hrms.com",
        "department": "Engineering",
        "role": "employee",
    },
    {
        "first_name": "Chirangibi",
        "last_name": "Nayak",
        "email": "chirangibi.nayak@hrms.com",
        "department": "Sales",
        "role": "manager",
    },
    {
        "first_name": "Vikram",
        "last_name": "Singh",
        "email": "vikram.singh@hrms.com",
        "department": "Sales",
        "role": "employee",
    },
    {
        "first_name": "Ankur",
        "last_name": "Patel",
        "email": "ankur.patel@hrms.com",
        "department": "Finance",
        "role": "employee",
    },
    {
        "first_name": "Raj",
        "last_name": "Kumar",
        "email": "raj.kumar@hrms.com",
        "department": "HR",
        "role": "admin",
    },
    {
        "first_name": "Sandesh",
        "last_name": "Iyer",
        "email": "sandesh.iyer@hrms.com",
        "department": "Engineering",
        "role": "employee",
    },
    {
        "first_name": "Aastha",
        "last_name": "Gupta",
        "email": "aastha.gupta@hrms.com",
        "department": "HR",
        "role": "employee",
    },
    {
        "first_name": "Rohit",
        "last_name": "Malhotra",
        "email": "rohit.malhotra@hrms.com",
        "department": "Engineering",
        "role": "employee",
    },
    {
        "first_name": "Neha",
        "last_name": "Kapoor",
        "email": "neha.kapoor@hrms.com",
        "department": "Sales",
        "role": "employee",
    },
    {
        "first_name": "Arjun",
        "last_name": "Reddy",
        "email": "arjun.reddy@hrms.com",
        "department": "Finance",
        "role": "manager",
    },
    {
        "first_name": "Divya",
        "last_name": "Singh",
        "email": "divya.singh@hrms.com",
        "department": "Finance",
        "role": "employee",
    },
    {
        "first_name": "Karan",
        "last_name": "Chopra",
        "email": "karan.chopra@hrms.com",
        "department": "Sales",
        "role": "employee",
    },
    {
        "first_name": "Pooja",
        "last_name": "Bansal",
        "email": "pooja.bansal@hrms.com",
        "department": "HR",
        "role": "employee",
    },
]

PROJECT_DATA = [
    {
        "project_name": "AI Platform Development",
        "client": "TechCorp India",
        "description": "Building enterprise AI platform with ML capabilities",
        "tasks": ["Backend Development", "Frontend UI", "Database Design", "API Integration"],
    },
    {
        "project_name": "E-Commerce Portal",
        "client": "RetailHub",
        "description": "Next-gen e-commerce solution with real-time inventory",
        "tasks": ["UI/UX Design", "Payment Gateway", "Inventory Management", "Analytics"],
    },
    {
        "project_name": "Mobile App Redesign",
        "client": "FinanceApp Inc",
        "description": "Redesigning mobile banking application",
        "tasks": ["Mobile Development", "Security Enhancement", "Testing", "Deployment"],
    },
]


def seed_database():
    """Seed database with sample data"""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Employee).count() > 1:  # Skip if employees already seeded
            print("Database already seeded!")
            return

        print("Starting database seeding...")

        # Get roles and departments
        roles = {
            r.role_name: r.role_id
            for r in db.query(Role).all()
        }
        departments = {
            d.department_name: d.department_id
            for d in db.query(Department).all()
        }

        # Seed employees
        employees_map = {}
        employee_code_counter = 1000

        # First, create admin user
        admin_employee = Employee(
            employee_id=generate_uuid(),
            employee_code=f"EMP{employee_code_counter}",
            first_name="Admin",
            last_name="User",
            email="admin@hrms.com",
            password_hash=get_password_hash("admin123"),
            department_id=departments.get("HR"),
            role_id=roles.get("admin"),
            join_date=date(2022, 1, 15),
            status="active",
        )
        db.add(admin_employee)
        employees_map["admin@hrms.com"] = admin_employee
        employee_code_counter += 1

        # Add Indian employees
        manager_map = {}
        for emp_data in INDIAN_EMPLOYEES:
            emp_code = f"EMP{employee_code_counter}"
            join_date = date(2021, 1, 1) + timedelta(days=random.randint(0, 700))

            employee = Employee(
                employee_id=generate_uuid(),
                employee_code=emp_code,
                first_name=emp_data["first_name"],
                last_name=emp_data["last_name"],
                email=emp_data["email"],
                password_hash=get_password_hash("password123"),
                department_id=departments.get(emp_data["department"]),
                role_id=roles.get(emp_data["role"]),
                manager_id=None,  # Will be assigned later
                join_date=join_date,
                status="active",
            )
            db.add(employee)
            employees_map[emp_data["email"]] = employee
            if emp_data["role"] == "manager":
                manager_map[emp_data["department"]] = employee
            employee_code_counter += 1

        db.flush()

        # Assign managers to employees
        for emp_data in INDIAN_EMPLOYEES:
            if emp_data["role"] == "employee":
                employee = employees_map[emp_data["email"]]
                department = emp_data["department"]
                if department in manager_map:
                    employee.manager_id = manager_map[department].employee_id

        # Seed projects and tasks
        leave_types = db.query(LeaveType).all()
        leave_type_map = {lt.leave_name: lt.leave_type_id for lt in leave_types}

        projects = []
        for proj_data in PROJECT_DATA:
            project = Project(
                project_id=generate_uuid(),
                project_name=proj_data["project_name"],
                client=proj_data["client"],
                description=proj_data["description"],
                start_date=date.today() - timedelta(days=random.randint(30, 180)),
                end_date=date.today() + timedelta(days=random.randint(100, 300)),
                status="active",
            )
            db.add(project)
            projects.append((project, proj_data["tasks"]))

        db.flush()

        # Add tasks to projects
        for project, task_names in projects:
            for task_name in task_names:
                task = Task(
                    task_id=generate_uuid(),
                    project_id=project.project_id,
                    task_name=task_name,
                    description=f"Task: {task_name} for project {project.project_name}",
                )
                db.add(task)

        db.flush()

        # Assign employees to projects
        all_employees = list(employees_map.values())[1:]  # Skip admin
        for project in [p[0] for p in projects]:
            # Assign 3-5 random employees to each project
            assigned_employees = random.sample(all_employees, min(5, len(all_employees)))
            for emp in assigned_employees:
                emp_project = EmployeeProject(
                    id=generate_uuid(),
                    employee_id=emp.employee_id,
                    project_id=project.project_id,
                    allocation_start=date.today() - timedelta(days=random.randint(10, 60)),
                    allocation_end=date.today() + timedelta(days=random.randint(30, 180)),
                )
                db.add(emp_project)

        db.flush()

        # Initialize leave balances for all employees
        current_date = date.today()
        for emp in all_employees:
            for leave_type in leave_types:
                balance = EmployeeLeaveBalance(
                    balance_id=generate_uuid(),
                    employee_id=emp.employee_id,
                    leave_type_id=leave_type.leave_type_id,
                    opening_balance=leave_type.annual_limit / 2,
                    leaves_taken=random.uniform(0, 3),
                    accrued_this_month=leave_type.monthly_accrual,
                    closing_balance=(leave_type.annual_limit / 2) + leave_type.monthly_accrual,
                    year=current_date.year,
                    month=current_date.month,
                )
                db.add(balance)

        db.commit()
        print("✅ Database seeding completed successfully!")
        print(f"✓ Created {len(employees_map)} employees")
        print(f"✓ Created {len(projects)} projects")
        print(f"✓ Created leave balances for all employees")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
