# HRMS Backend API

A comprehensive Human Resource Management System built with FastAPI and SQLite.

## Features

- **Employee Management**: Create, update, and manage employee records
- **Leave Management**: Apply for leaves, track balances, approval workflow
- **Attendance Tracking**: Check-in/check-out, daily attendance, weekly summaries
- **Timesheet Management**: Log project hours, task allocation, manager approval
- **Role-Based Access Control**: Admin, Manager, Employee roles with different permissions
- **Approval Workflow**: Generic workflow for leave and timesheet approvals
- **Notifications**: Ready for email/Slack integration

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Running the Server

\`\`\`bash
python run.py
\`\`\`

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database

SQLite database is automatically created at `hrms.db`

## Authentication

The API uses JWT tokens for authentication. Use the `/api/auth/login` endpoint to get a token.

## Default Data

The system automatically initializes with:
- Roles: Admin, Manager, Employee
- Departments: Engineering, Sales, HR, Finance
- Leave Types: Casual, Sick, Earned

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new employee
- POST `/api/auth/login` - Login and get token
- GET `/api/auth/me` - Get current user info

### Employees
- GET `/api/employees/` - List all employees
- POST `/api/employees/` - Create new employee (admin only)
- GET `/api/employees/{employee_id}` - Get employee details
- PUT `/api/employees/{employee_id}` - Update employee

### Leave Management
- GET `/api/leave-requests/` - Get leave requests
- POST `/api/leave-requests/` - Create leave request
- PUT `/api/leave-requests/{leave_id}/submit` - Submit for approval
- PUT `/api/leave-requests/{leave_id}/approve` - Approve/reject leave

### Attendance
- POST `/api/attendance/checkin` - Check in
- POST `/api/attendance/checkout` - Check out
- GET `/api/attendance/daily/{emp_id}` - Get daily attendance
- POST `/api/attendance/weekly-summary` - Generate weekly summary

### Timesheet
- POST `/api/timesheets/` - Create timesheet entry
- GET `/api/timesheets/` - Get timesheets
- PUT `/api/timesheets/{timesheet_id}/submit` - Submit timesheet
- PUT `/api/timesheets/{timesheet_id}/approve` - Approve timesheet

### Projects & Tasks
- GET `/api/projects/` - List projects
- POST `/api/projects/` - Create project
- POST `/api/tasks/` - Create task
- GET `/api/tasks/project/{project_id}` - Get project tasks

## Environment Variables

- `SECRET_KEY` - JWT secret key (default: change-in-production)
- `PORT` - Server port (default: 8000)

## Business Rules

### Leave Management
- Auto accrue monthly leaves based on policy
- Carry forward allowed based on leave type settings
- Auto-deduct from balance when approved
- No negative balance unless LOP

### Attendance
- Max 8 hours per day
- Auto weekly summary with 40-hour limit
- Auto-sync with approved leaves
- Status: present, leave, holiday, absent

### Timesheet
- Only assigned projects can be selected
- Max 8 hours per day
- Manager approval required
- Tracks by project and task

## Security

- Password hashing with bcrypt
- JWT token-based authentication
- Role-based access control
- Environment variable for secret key
