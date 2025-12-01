# HRMS Database Seeding Guide

This document describes the seed data structure and how to seed the database with sample Indian employee data.

## Seed Data Overview

The HRMS system comes with pre-configured seed data including:

### 1. Employees (15 Total)
All employees use the password: `password123`
Admin uses: `admin123`

**Engineering Department:**
- Samyak Verma (Employee) - samyak.verma@hrms.com
- Prachi Sharma (Manager) - prachi.sharma@hrms.com
- Bhushan Desai (Employee) - bhushan.desai@hrms.com
- Sandesh Iyer (Employee) - sandesh.iyer@hrms.com
- Rohit Malhotra (Employee) - rohit.malhotra@hrms.com

**Sales Department:**
- Chirangibi Nayak (Manager) - chirangibi.nayak@hrms.com
- Vikram Singh (Employee) - vikram.singh@hrms.com
- Neha Kapoor (Employee) - neha.kapoor@hrms.com
- Karan Chopra (Employee) - karan.chopra@hrms.com

**Finance Department:**
- Ankur Patel (Employee) - ankur.patel@hrms.com
- Arjun Reddy (Manager) - arjun.reddy@hrms.com
- Divya Singh (Employee) - divya.singh@hrms.com

**HR Department:**
- Raj Kumar (Admin) - raj.kumar@hrms.com
- Aastha Gupta (Employee) - aastha.gupta@hrms.com

**System Admin:**
- Admin User (Admin) - admin@hrms.com

### 2. Projects (3 Total)

1. **AI Platform Development**
   - Client: TechCorp India
   - Tasks: Backend Development, Frontend UI, Database Design, API Integration

2. **E-Commerce Portal**
   - Client: RetailHub
   - Tasks: UI/UX Design, Payment Gateway, Inventory Management, Analytics

3. **Mobile App Redesign**
   - Client: FinanceApp Inc
   - Tasks: Mobile Development, Security Enhancement, Testing, Deployment

### 3. Leave Types (3 Total)

| Leave Type | Annual Limit | Monthly Accrual | Carry Forward |
|-----------|--------------|-----------------|---------------|
| Casual | 12 days | 1 day | Yes (Max 5) |
| Sick | 10 days | 0.83 days | No |
| Earned | 20 days | 1.67 days | Yes (Max 10) |

## How to Seed the Database

### Option 1: Automatic Seeding (Recommended)
The database is automatically seeded when you start the server:

\`\`\`bash
python run.py
\`\`\`

The seeding process:
1. Creates all database tables
2. Initializes roles, departments, and leave types
3. Creates all employees with proper manager assignments
4. Creates projects and tasks
5. Assigns employees to projects
6. Initializes leave balances for all employees

### Option 2: Manual Seeding Script
Run the standalone seeding script:

\`\`\`bash
python scripts/seed_data.py
\`\`\`

This will display a summary of created data and provide test credentials.

### Option 3: Using Python Direct
\`\`\`python
from app.database import engine, Base, init_db
from app.models import Role, Department, LeaveType

# Create tables and seed data
Base.metadata.create_all(bind=engine)
init_db(engine)
\`\`\`

## Testing with Seed Data

### 1. Login as Different Roles

**Admin User:**
\`\`\`bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hrms.com",
    "password": "admin123"
  }'
\`\`\`

**Manager:**
\`\`\`bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "prachi.sharma@hrms.com",
    "password": "password123"
  }'
\`\`\`

**Employee:**
\`\`\`bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "samyak.verma@hrms.com",
    "password": "password123"
  }'
\`\`\`

### 2. Explore API Endpoints

Visit the interactive Swagger documentation:
\`\`\`
http://localhost:8000/docs
\`\`\`

### 3. Test Common Workflows

**Apply Leave:**
- Login as an employee
- POST to `/api/leave-requests` with start_date, end_date, and reason

**Approve Leave:**
- Login as the manager
- GET `/api/leave-requests` to view pending leaves
- PATCH `/api/leave-requests/{leave_id}` to approve/reject

**Check-in/Check-out:**
- POST to `/api/attendance/check-in`
- POST to `/api/attendance/check-out`

**Submit Timesheet:**
- GET `/api/projects` to see assigned projects
- POST to `/api/timesheets` with project_id, task_id, and hours

## Database Cleanup

To reset and re-seed the database:

\`\`\`bash
# Delete the database file
rm hrms.db

# Restart the server
python run.py
\`\`\`

## Seed Data Structure

### Employee Manager Hierarchy

\`\`\`
Engineering Department:
├── Prachi Sharma (Manager)
│   ├── Samyak Verma (Employee)
│   ├── Bhushan Desai (Employee)
│   ├── Sandesh Iyer (Employee)
│   └── Rohit Malhotra (Employee)

Sales Department:
├── Chirangibi Nayak (Manager)
│   ├── Vikram Singh (Employee)
│   ├── Neha Kapoor (Employee)
│   └── Karan Chopra (Employee)

Finance Department:
├── Arjun Reddy (Manager)
│   ├── Ankur Patel (Employee)
│   └── Divya Singh (Employee)

HR Department:
├── Raj Kumar (Admin)
└── Aastha Gupta (Employee)
\`\`\`

## Customizing Seed Data

To modify seed data, edit the `app/seeds.py` file:

1. **Add/Remove Employees:** Modify the `INDIAN_EMPLOYEES` list
2. **Add/Remove Projects:** Modify the `PROJECT_DATA` list
3. **Change Leave Types:** Update the leave types in `init_db()` function

After making changes, reset the database and re-seed:

\`\`\`bash
rm hrms.db
python run.py
\`\`\`

## Notes

- All passwords in seed data are plain text for testing purposes only
- In production, use environment variables and secure password management
- Employee-to-project assignments are randomized (3-5 per project)
- Leave balances are initialized based on the current month
- All dates are relative to the current system date

---

For more information, see the main README.md file.
