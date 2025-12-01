# HRMS Backend - Complete API Documentation

## Table of Contents
1. [Authentication Flow](#authentication-flow)
2. [Role-Based Access Control](#rbac)
3. [API Endpoints by Module](#endpoints)
4. [Database Tables Reference](#database-tables)
5. [SQL Queries for Testing](#sql-queries)
6. [Complete Request/Response Examples](#examples)

---

## Authentication Flow

### 1. User Registration
**Endpoint**: `POST /auth/register`

**Purpose**: Register a new employee (typically done by Admin)

**Request Body**:
\`\`\`json
{
  "employee_code": "EMP001",
  "first_name": "Samyak",
  "last_name": "Kumar",
  "email": "samyak@company.com",
  "password": "password123",
  "department_id": 1,
  "role_id": 3,
  "manager_id": null,
  "join_date": "2025-01-01"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "employee_code": "EMP001",
  "first_name": "Samyak",
  "last_name": "Kumar",
  "email": "samyak@company.com",
  "department_id": 1,
  "role_id": 3,
  "manager_id": null,
  "join_date": "2025-01-01",
  "status": "active"
}
\`\`\`

**Tables Used**: `employees`, `roles`, `departments`

**Roles with Access**: `admin`

**SQL to verify registration**:
\`\`\`sql
SELECT * FROM employees WHERE email = 'samyak@company.com';
\`\`\`

---

### 2. User Login
**Endpoint**: `POST /auth/login`

**Purpose**: Authenticate user and get JWT token

**Request Parameters**:
\`\`\`
?email=samyak@company.com&password=password123
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_code": "EMP001",
    "first_name": "Samyak",
    "last_name": "Kumar",
    "email": "samyak@company.com",
    "role": {
      "role_id": 3,
      "role_name": "employee"
    },
    "department": {
      "department_id": 1,
      "department_name": "Engineering"
    }
  }
}
\`\`\`

**Tables Used**: `employees`, `roles`, `departments`

**All Roles**: All authenticated users can login

**SQL to verify credentials**:
\`\`\`sql
SELECT e.employee_id, e.first_name, e.last_name, e.email, r.role_name 
FROM employees e
JOIN roles r ON e.role_id = r.role_id
WHERE e.email = 'samyak@company.com';
\`\`\`

---

## Role-Based Access Control (RBAC)

Three roles in the system:

| Module | Employee | Manager | Admin |
|--------|----------|---------|-------|
| Apply Leave | ✅ | ✅ | ✅ |
| Approve Leave | ❌ | ✅ | ✅ |
| View Own Attendance | ✅ | ✅ | ✅ |
| View Team Attendance | ❌ | ✅ | ✅ |
| View All Attendance | ❌ | ❌ | ✅ |
| Create Timesheet | ✅ | ✅ | ✅ |
| Approve Timesheet | ❌ | ✅ | ✅ |
| Manage Employees | ❌ | ❌ | ✅ |
| View Analytics (Personal) | ✅ | ✅ | ✅ |
| View Analytics (Team) | ❌ | ✅ | ✅ |
| View Analytics (System) | ❌ | ❌ | ✅ |
| Generate Reports | ❌ | ❌ | ✅ |

---

## API Endpoints by Module

### MASTER DATA MANAGEMENT

#### 1. Employee Management

##### Create Employee (Admin Only)
**Endpoint**: `POST /employees/`

**Authorization**: Bearer token (Admin role required)

**Request Body**:
\`\`\`json
{
  "employee_code": "EMP002",
  "first_name": "Prachi",
  "last_name": "Singh",
  "email": "prachi@company.com",
  "password": "password123",
  "department_id": 1,
  "role_id": 2,
  "manager_id": "550e8400-e29b-41d4-a716-446655440000",
  "join_date": "2025-01-05"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440001",
  "employee_code": "EMP002",
  "first_name": "Prachi",
  "last_name": "Singh",
  "email": "prachi@company.com",
  "status": "active"
}
\`\`\`

**Tables Used**: 
- `employees` (INSERT)
- `roles` (FK reference)
- `departments` (FK reference)

**SQL to verify creation**:
\`\`\`sql
SELECT e.*, d.department_name, r.role_name 
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN roles r ON e.role_id = r.role_id
WHERE e.employee_code = 'EMP002';
\`\`\`

---

##### Get All Employees
**Endpoint**: `GET /employees/`

**Authorization**: Bearer token (All authenticated users)

**Response** (200 OK):
\`\`\`json
[
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_code": "EMP001",
    "first_name": "Samyak",
    "last_name": "Kumar",
    "email": "samyak@company.com",
    "status": "active"
  },
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440001",
    "employee_code": "EMP002",
    "first_name": "Prachi",
    "last_name": "Singh",
    "email": "prachi@company.com",
    "status": "active"
  }
]
\`\`\`

**Tables Used**: `employees`, `roles`, `departments`

**SQL to retrieve**:
\`\`\`sql
SELECT e.employee_id, e.employee_code, e.first_name, e.last_name, 
       e.email, e.status, d.department_name, r.role_name, 
       e.manager_id, e.join_date
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN roles r ON e.role_id = r.role_id
ORDER BY e.employee_code;
\`\`\`

---

##### Get Employee by ID
**Endpoint**: `GET /employees/{employee_id}`

**Authorization**: Bearer token (All authenticated users)

**Response** (200 OK):
\`\`\`json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "employee_code": "EMP001",
  "first_name": "Samyak",
  "last_name": "Kumar",
  "email": "samyak@company.com",
  "department_id": 1,
  "role_id": 3,
  "manager_id": null,
  "join_date": "2025-01-01",
  "status": "active"
}
\`\`\`

**Tables Used**: `employees`, `roles`, `departments`

**SQL to retrieve**:
\`\`\`sql
SELECT e.*, d.department_name, r.role_name 
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN roles r ON e.role_id = r.role_id
WHERE e.employee_id = '550e8400-e29b-41d4-a716-446655440000';
\`\`\`

---

##### Update Employee (Admin Only)
**Endpoint**: `PUT /employees/{employee_id}`

**Authorization**: Bearer token (Admin role required)

**Request Body** (partial update):
\`\`\`json
{
  "first_name": "Samyak",
  "department_id": 2,
  "status": "inactive"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "employee_code": "EMP001",
  "first_name": "Samyak",
  "last_name": "Kumar",
  "department_id": 2,
  "status": "inactive"
}
\`\`\`

**Tables Used**: `employees` (UPDATE)

**SQL to verify update**:
\`\`\`sql
SELECT e.employee_id, e.first_name, e.department_id, 
       d.department_name, e.status
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE e.employee_id = '550e8400-e29b-41d4-a716-446655440000';
\`\`\`

---

##### Delete Employee (Admin Only)
**Endpoint**: `DELETE /employees/{employee_id}`

**Authorization**: Bearer token (Admin role required)

**Response** (204 No Content)

**Tables Used**: `employees` (DELETE)

**SQL to verify deletion**:
\`\`\`sql
SELECT COUNT(*) as employee_count FROM employees 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000';
\`\`\`

---

#### 2. Department Management

##### Create Department (Admin Only)
**Endpoint**: `POST /departments/`

**Request Body**:
\`\`\`json
{
  "department_name": "Engineering"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "department_id": 1,
  "department_name": "Engineering"
}
\`\`\`

**Tables Used**: `departments` (INSERT)

**SQL to verify**:
\`\`\`sql
SELECT * FROM departments ORDER BY department_id;
\`\`\`

---

#### 3. Role Management

##### Get All Roles
**Endpoint**: `GET /roles/`

**Authorization**: Bearer token (All authenticated users)

**Response** (200 OK):
\`\`\`json
[
  {
    "role_id": 1,
    "role_name": "admin"
  },
  {
    "role_id": 2,
    "role_name": "manager"
  },
  {
    "role_id": 3,
    "role_name": "employee"
  }
]
\`\`\`

**Tables Used**: `roles`

**SQL to retrieve**:
\`\`\`sql
SELECT * FROM roles;
\`\`\`

---

### LEAVE MANAGEMENT

#### 1. Leave Types Setup (Admin Only)

##### Get Leave Types
**Endpoint**: `GET /leave-types/`

**Response** (200 OK):
\`\`\`json
[
  {
    "leave_type_id": 1,
    "leave_name": "Sick Leave",
    "annual_limit": 12,
    "monthly_accrual": 1.0,
    "carry_forward_limit": 5,
    "is_carry_forward_allowed": true
  },
  {
    "leave_type_id": 2,
    "leave_name": "Casual Leave",
    "annual_limit": 10,
    "monthly_accrual": 0.83,
    "carry_forward_limit": 3,
    "is_carry_forward_allowed": true
  },
  {
    "leave_type_id": 3,
    "leave_name": "Earned Leave",
    "annual_limit": 20,
    "monthly_accrual": 1.67,
    "carry_forward_limit": 10,
    "is_carry_forward_allowed": true
  }
]
\`\`\`

**Tables Used**: `leave_types`

**SQL to retrieve**:
\`\`\`sql
SELECT * FROM leave_types;
\`\`\`

---

#### 2. Apply Leave (All Users)

##### Create Leave Request
**Endpoint**: `POST /leave-requests/`

**Authorization**: Bearer token (All authenticated users)

**Request Body**:
\`\`\`json
{
  "leave_type_id": 1,
  "start_date": "2025-02-10",
  "end_date": "2025-02-12",
  "reason": "Medical appointment"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "leave_id": "550e8400-e29b-41d4-a716-446655440100",
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "leave_type_id": 1,
  "start_date": "2025-02-10",
  "end_date": "2025-02-12",
  "total_days": 3,
  "reason": "Medical appointment",
  "status": "open",
  "created_at": "2025-02-01T10:00:00",
  "submitted_at": null,
  "approved_by": null,
  "approved_at": null
}
\`\`\`

**Tables Used**: 
- `leave_requests` (INSERT)
- `leave_types` (FK reference)
- `employees` (FK reference)

**SQL to verify creation**:
\`\`\`sql
SELECT lr.leave_id, lr.employee_id, e.first_name, e.last_name,
       lt.leave_name, lr.start_date, lr.end_date, lr.total_days,
       lr.status, lr.created_at
FROM leave_requests lr
JOIN employees e ON lr.employee_id = e.employee_id
JOIN leave_types lt ON lr.leave_type_id = lt.leave_type_id
WHERE lr.leave_id = '550e8400-e29b-41d4-a716-446655440100';
\`\`\`

---

##### Submit Leave Request
**Endpoint**: `PUT /leave-requests/{leave_id}/submit`

**Authorization**: Bearer token (Employee or Admin)

**Response** (200 OK):
\`\`\`json
{
  "leave_id": "550e8400-e29b-41d4-a716-446655440100",
  "status": "submitted",
  "submitted_at": "2025-02-01T10:05:00"
}
\`\`\`

**Tables Used**: `leave_requests` (UPDATE)

**Workflow**:
1. Employee creates leave request (status = "open")
2. Employee submits leave request (status = "submitted")
3. Manager/Admin reviews and approves (status = "approved")

**SQL to track status**:
\`\`\`sql
SELECT leave_id, status, created_at, submitted_at, 
       approved_at, approved_by
FROM leave_requests
WHERE leave_id = '550e8400-e29b-41d4-a716-446655440100';
\`\`\`

---

##### Approve/Reject Leave (Manager/Admin)
**Endpoint**: `PUT /leave-requests/{leave_id}/approve`

**Authorization**: Bearer token (Manager or Admin role required)

**Request Body**:
\`\`\`json
{
  "action": "approved"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "leave_id": "550e8400-e29b-41d4-a716-446655440100",
  "status": "approved",
  "approved_by": "550e8400-e29b-41d4-a716-446655440050",
  "approved_at": "2025-02-01T11:00:00"
}
\`\`\`

**Tables Used**: 
- `leave_requests` (UPDATE)
- `attendance` (INSERT/UPDATE for leave days)
- `approval_workflow` (INSERT)

**Automatic Actions**:
- When approved, system automatically marks attendance as "leave" for all dates in the leave period
- Updates `attendance` table with status = "leave"
- Creates workflow audit trail in `approval_workflow`

**SQL to verify approval and attendance auto-marking**:
\`\`\`sql
-- Check leave request approval
SELECT leave_id, status, approved_by, approved_at 
FROM leave_requests 
WHERE leave_id = '550e8400-e29b-41d4-a716-446655440100';

-- Check auto-marked attendance
SELECT employee_id, date, status 
FROM attendance 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000'
  AND date BETWEEN '2025-02-10' AND '2025-02-12'
ORDER BY date;
\`\`\`

---

##### Get Leave Balance (All Users)
**Endpoint**: `GET /leave-requests/balance/{employee_id}`

**Response** (200 OK):
\`\`\`json
[
  {
    "balance_id": "550e8400-e29b-41d4-a716-446655440200",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "leave_type_id": 1,
    "leave_name": "Sick Leave",
    "opening_balance": 10,
    "leaves_taken": 3,
    "accrued_this_month": 1,
    "closing_balance": 8,
    "year": 2025,
    "month": 2
  }
]
\`\`\`

**Tables Used**: `employee_leave_balance`, `leave_types`

**SQL to check balance**:
\`\`\`sql
SELECT elb.balance_id, elb.employee_id, e.first_name, e.last_name,
       lt.leave_name, elb.opening_balance, elb.leaves_taken, 
       elb.accrued_this_month, elb.closing_balance,
       elb.year, elb.month
FROM employee_leave_balance elb
JOIN employees e ON elb.employee_id = e.employee_id
JOIN leave_types lt ON elb.leave_type_id = lt.leave_type_id
WHERE elb.employee_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY elb.year DESC, elb.month DESC;
\`\`\`

---

### ATTENDANCE MANAGEMENT

#### 1. Daily Check-in / Check-out

##### Check-in (All Users)
**Endpoint**: `POST /attendance/checkin`

**Authorization**: Bearer token

**No Request Body Required** (system uses current user and date)

**Response** (201 Created):
\`\`\`json
{
  "attendance_id": "550e8400-e29b-41d4-a716-446655440300",
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2025-02-03",
  "check_in": "2025-02-03T09:00:00",
  "check_out": null,
  "total_hours": null,
  "status": "present"
}
\`\`\`

**Tables Used**: `attendance` (INSERT if not exists, UPDATE if exists)

**SQL to verify check-in**:
\`\`\`sql
SELECT attendance_id, employee_id, date, check_in, 
       check_out, total_hours, status
FROM attendance 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000' 
  AND date = DATE('2025-02-03');
\`\`\`

---

##### Check-out (All Users)
**Endpoint**: `POST /attendance/checkout`

**Authorization**: Bearer token

**No Request Body Required**

**Response** (200 OK):
\`\`\`json
{
  "attendance_id": "550e8400-e29b-41d4-a716-446655440300",
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2025-02-03",
  "check_in": "2025-02-03T09:00:00",
  "check_out": "2025-02-03T17:30:00",
  "total_hours": 8.5,
  "status": "present"
}
\`\`\`

**Tables Used**: `attendance` (UPDATE)

**Automatic Calculation**: 
- System calculates `total_hours = (check_out - check_in) / 3600`
- If hours > 8, it's capped at 8
- Status set to "present"

**SQL to verify complete attendance**:
\`\`\`sql
SELECT attendance_id, employee_id, date, 
       TIME(check_in) as checkin_time,
       TIME(check_out) as checkout_time,
       ROUND((julianday(check_out) - julianday(check_in)) * 24, 2) as calculated_hours,
       total_hours, status
FROM attendance 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000' 
  AND date = DATE('2025-02-03');
\`\`\`

---

##### Get Daily Attendance
**Endpoint**: `GET /attendance/daily/{emp_id}`

**Authorization**: Bearer token (Manager/Admin can view any; Employees see only own)

**Response** (200 OK):
\`\`\`json
[
  {
    "attendance_id": "550e8400-e29b-41d4-a716-446655440300",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "date": "2025-02-03",
    "check_in": "2025-02-03T09:00:00",
    "check_out": "2025-02-03T17:30:00",
    "total_hours": 8.5,
    "status": "present"
  },
  {
    "attendance_id": "550e8400-e29b-41d4-a716-446655440301",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "date": "2025-02-04",
    "check_in": "2025-02-04T09:15:00",
    "check_out": "2025-02-04T17:45:00",
    "total_hours": 8.5,
    "status": "present"
  }
]
\`\`\`

**Tables Used**: `attendance`

**SQL to retrieve attendance records**:
\`\`\`sql
SELECT attendance_id, employee_id, date, 
       check_in, check_out, total_hours, status
FROM attendance 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY date DESC;
\`\`\`

---

#### 2. Weekly Attendance Summary

##### Generate Weekly Summary (Admin Only)
**Endpoint**: `POST /attendance/weekly-summary`

**Authorization**: Bearer token (Admin role required)

**No Request Body Required** (system generates for current week)

**Response** (201 Created):
\`\`\`json
{
  "message": "Weekly summaries generated",
  "count": 15
}
\`\`\`

**Tables Used**: 
- `attendance` (READ)
- `weekly_attendance_summary` (INSERT)

**Business Logic**:
- Runs for all employees
- Calculates total hours for Mon-Sun of current week
- Calculates overtime if total_hours > 40
- Enforces 40-hour/week maximum

**SQL to generate weekly summary**:
\`\`\`sql
-- Find week start date (Monday)
WITH RECURSIVE week_data AS (
  SELECT DATE('2025-02-03', '-' || strftime('%w', '2025-02-03') || ' days') as week_start
),
employee_weekly as (
  SELECT 
    a.employee_id,
    week_start as week_start_date,
    DATE(week_start, '+6 days') as week_end_date,
    ROUND(SUM(COALESCE(a.total_hours, 0)), 2) as total_hours,
    ROUND(MAX(0, SUM(COALESCE(a.total_hours, 0)) - 40), 2) as over_time
  FROM attendance a
  CROSS JOIN week_data
  WHERE DATE(a.date) >= week_start
    AND DATE(a.date) <= DATE(week_start, '+6 days')
  GROUP BY a.employee_id
)
SELECT * FROM employee_weekly;
\`\`\`

**SQL to verify weekly summaries created**:
\`\`\`sql
SELECT summary_id, employee_id, e.first_name, e.last_name,
       week_start_date, week_end_date, total_hours, over_time
FROM weekly_attendance_summary was
JOIN employees e ON was.employee_id = e.employee_id
WHERE week_start_date = '2025-02-03'
ORDER BY e.first_name;
\`\`\`

---

##### Get Weekly Summary
**Endpoint**: `GET /attendance/weekly-summary/{emp_id}`

**Response** (200 OK):
\`\`\`json
[
  {
    "summary_id": "550e8400-e29b-41d4-a716-446655440400",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "week_start_date": "2025-02-03",
    "week_end_date": "2025-02-09",
    "total_hours": 40,
    "over_time": 0
  },
  {
    "summary_id": "550e8400-e29b-41d4-a716-446655440401",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "week_start_date": "2025-01-27",
    "week_end_date": "2025-02-02",
    "total_hours": 42,
    "over_time": 2
  }
]
\`\`\`

**Tables Used**: `weekly_attendance_summary`

**SQL to retrieve**:
\`\`\`sql
SELECT summary_id, employee_id, week_start_date, 
       week_end_date, total_hours, over_time
FROM weekly_attendance_summary 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY week_start_date DESC;
\`\`\`

---

### TIMESHEET MANAGEMENT

#### 1. Project & Task Setup (Admin)

##### Get Projects
**Endpoint**: `GET /projects/`

**Response** (200 OK):
\`\`\`json
[
  {
    "project_id": "550e8400-e29b-41d4-a716-446655440500",
    "project_name": "Mobile App Development",
    "description": "iOS and Android app for e-commerce",
    "client": "TechCorp Inc",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "status": "active"
  }
]
\`\`\`

**Tables Used**: `projects`

**SQL to retrieve**:
\`\`\`sql
SELECT project_id, project_name, description, client,
       start_date, end_date, status
FROM projects
WHERE status = 'active'
ORDER BY project_name;
\`\`\`

---

##### Get Tasks for Project
**Endpoint**: `GET /tasks/?project_id={project_id}`

**Response** (200 OK):
\`\`\`json
[
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440550",
    "project_id": "550e8400-e29b-41d4-a716-446655440500",
    "task_name": "UI Design",
    "description": "Design mobile app UI/UX"
  },
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440551",
    "project_id": "550e8400-e29b-41d4-a716-446655440500",
    "task_name": "Backend API",
    "description": "Develop REST APIs"
  }
]
\`\`\`

**Tables Used**: `tasks`, `projects`

**SQL to retrieve**:
\`\`\`sql
SELECT t.task_id, t.project_id, p.project_name,
       t.task_name, t.description
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
WHERE t.project_id = '550e8400-e29b-41d4-a716-446655440500';
\`\`\`

---

#### 2. Daily Timesheet Entry

##### Create Single Day Timesheet
**Endpoint**: `POST /timesheets/`

**Authorization**: Bearer token (All authenticated users)

**Request Body**:
\`\`\`json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440500",
  "task_id": "550e8400-e29b-41d4-a716-446655440550",
  "date": "2025-02-03",
  "hours": 6,
  "description": "Completed login screen design"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "timesheet_id": "550e8400-e29b-41d4-a716-446655440600",
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440500",
  "task_id": "550e8400-e29b-41d4-a716-446655440550",
  "date": "2025-02-03",
  "hours": 6,
  "description": "Completed login screen design",
  "status": "open"
}
\`\`\`

**Tables Used**:
- `timesheets` (INSERT)
- `projects` (FK reference, validation)
- `tasks` (FK reference, validation)

**Validation Rules**:
- Project must exist and be active
- Task must exist and belong to selected project
- Hours must be <= 8
- Hours must be >= 0

**SQL to verify creation**:
\`\`\`sql
SELECT t.timesheet_id, t.employee_id, e.first_name, e.last_name,
       p.project_name, tk.task_name, t.date, t.hours,
       t.status, t.created_at
FROM timesheets t
JOIN employees e ON t.employee_id = e.employee_id
JOIN projects p ON t.project_id = p.project_id
JOIN tasks tk ON t.task_id = tk.task_id
WHERE t.timesheet_id = '550e8400-e29b-41d4-a716-446655440600';
\`\`\`

---

#### 3. Weekly Timesheet Entry (NEW FEATURE)

##### Create Weekly Timesheet (Bulk Entry)
**Endpoint**: `POST /timesheets/weekly`

**Authorization**: Bearer token (All authenticated users)

**Request Body** (Enter entire week's timesheet at once):
\`\`\`json
{
  "week_start_date": "2025-02-03",
  "project_id": "550e8400-e29b-41d4-a716-446655440500",
  "task_id": "550e8400-e29b-41d4-a716-446655440550",
  "entries": [
    {
      "date": "2025-02-03",
      "hours": 8,
      "description": "UI design setup"
    },
    {
      "date": "2025-02-04",
      "hours": 8,
      "description": "Login screen design"
    },
    {
      "date": "2025-02-05",
      "hours": 8,
      "description": "Dashboard design"
    },
    {
      "date": "2025-02-06",
      "hours": 8,
      "description": "Settings screen design"
    },
    {
      "date": "2025-02-07",
      "hours": 8,
      "description": "Final review & tweaks"
    }
  ]
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "week_start_date": "2025-02-03",
  "week_end_date": "2025-02-09",
  "total_hours": 40,
  "entries_created": 5,
  "timesheets": [
    {
      "timesheet_id": "550e8400-e29b-41d4-a716-446655440600",
      "employee_id": "550e8400-e29b-41d4-a716-446655440000",
      "date": "2025-02-03",
      "hours": 8,
      "status": "open"
    },
    ... (4 more entries)
  ]
}
\`\`\`

**Tables Used**:
- `timesheets` (INSERT multiple records)
- `projects` (FK reference, validation)
- `tasks` (FK reference, validation)

**Validation Rules**:
- `week_start_date` must be a Monday
- Total hours for week must be <= 40
- Each day's hours must be <= 8
- No duplicate dates
- All dates must be within the same week

**Business Logic Benefits**:
- Employees can fill their entire week's timesheet in one request
- Validates weekly 40-hour limit
- Prevents accidental over-allocation
- Standard feature in modern HRMS systems

**SQL to verify weekly entries**:
\`\`\`sql
SELECT DATE(date) as date_logged, SUM(hours) as daily_total,
       COUNT(*) as task_count
FROM timesheets 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000'
  AND date BETWEEN '2025-02-03' AND '2025-02-09'
GROUP BY DATE(date)
ORDER BY date;

-- Total for week
SELECT SUM(hours) as weekly_total
FROM timesheets 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000'
  AND date BETWEEN '2025-02-03' AND '2025-02-09';
\`\`\`

---

##### Get Week Timesheets
**Endpoint**: `GET /timesheets/week/{week_start_date}`

**Parameters**: 
- `week_start_date` (format: YYYY-MM-DD, must be Monday)

**Response** (200 OK):
\`\`\`json
[
  {
    "timesheet_id": "550e8400-e29b-41d4-a716-446655440600",
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_id": "550e8400-e29b-41d4-a716-446655440500",
    "task_id": "550e8400-e29b-41d4-a716-446655440550",
    "date": "2025-02-03",
    "hours": 8,
    "status": "open"
  },
  ... (more entries for the week)
]
\`\`\`

**Tables Used**: `timesheets`

**Access Control**:
- Employees: See only their own timesheets
- Managers/Admins: See all employee timesheets

**SQL to retrieve week's timesheets**:
\`\`\`sql
SELECT t.timesheet_id, t.employee_id, e.first_name, e.last_name,
       p.project_name, tk.task_name, t.date, t.hours, t.status
FROM timesheets t
JOIN employees e ON t.employee_id = e.employee_id
JOIN projects p ON t.project_id = p.project_id
JOIN tasks tk ON t.task_id = tk.task_id
WHERE t.employee_id = '550e8400-e29b-41d4-a716-446655440000'
  AND date(t.date) BETWEEN '2025-02-03' AND '2025-02-09'
ORDER BY t.date, t.timesheet_id;
\`\`\`

---

##### Submit Week Timesheet
**Endpoint**: `PUT /timesheets/week/{week_start_date}/submit`

**Authorization**: Bearer token (Employee or Admin)

**Response** (200 OK):
\`\`\`json
{
  "message": "Submitted 5 timesheets for week starting 2025-02-03",
  "count": 5
}
\`\`\`

**Tables Used**: `timesheets` (UPDATE)

**Workflow**:
1. Employee creates individual or bulk entries (status = "open")
2. Employee submits all for the week (status = "submitted")
3. Manager reviews and approves each or all (status = "approved")

**SQL to verify submission**:
\`\`\`sql
SELECT DATE(date) as date_logged, COUNT(*) as entry_count,
       GROUP_CONCAT(DISTINCT status) as statuses
FROM timesheets 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000'
  AND date BETWEEN '2025-02-03' AND '2025-02-09'
GROUP BY DATE(date);
\`\`\`

---

##### Approve/Reject Timesheet (Manager/Admin)
**Endpoint**: `PUT /timesheets/{timesheet_id}/approve`

**Authorization**: Bearer token (Manager or Admin role required)

**Request Body**:
\`\`\`json
{
  "action": "approved",
  "remarks": "Good allocation"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "timesheet_id": "550e8400-e29b-41d4-a716-446655440600",
  "status": "approved",
  "approved_by": "550e8400-e29b-41d4-a716-446655440050",
  "approved_at": "2025-02-03T14:00:00"
}
\`\`\`

**Tables Used**:
- `timesheets` (UPDATE)
- `approval_workflow` (INSERT audit trail)

**SQL to verify approval**:
\`\`\`sql
SELECT t.timesheet_id, t.status, t.approved_by,
       e.first_name as approver_name,
       t.approved_at
FROM timesheets t
LEFT JOIN employees e ON t.approved_by = e.employee_id
WHERE t.timesheet_id = '550e8400-e29b-41d4-a716-446655440600';

-- Check approval workflow audit trail
SELECT workflow_id, request_type, request_id, approver_id,
       action, action_at, remarks
FROM approval_workflow
WHERE request_type = 'timesheet' 
  AND request_id = '550e8400-e29b-41d4-a716-446655440600';
\`\`\`

---

### ANALYTICS & REPORTING

#### 1. Personal Analytics (All Users)

##### Get Personal Leave Analytics
**Endpoint**: `GET /analytics/personal/leave`

**Authorization**: Bearer token

**Response** (200 OK):
\`\`\`json
[
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Samyak",
    "last_name": "Kumar",
    "email": "samyak@company.com",
    "department_name": "Engineering",
    "total_approved_leaves": 5,
    "total_days_taken": 8,
    "pending_requests": 1
  }
]
\`\`\`

**Tables Used**: `leave_requests`, `employees`, `departments`

**SQL to calculate**:
\`\`\`sql
SELECT e.employee_id, e.first_name, e.last_name, e.email,
       d.department_name,
       (SELECT COUNT(*) FROM leave_requests 
        WHERE employee_id = e.employee_id AND status = 'approved') as total_approved_leaves,
       (SELECT SUM(total_days) FROM leave_requests 
        WHERE employee_id = e.employee_id AND status = 'approved') as total_days_taken,
       (SELECT COUNT(*) FROM leave_requests 
        WHERE employee_id = e.employee_id AND status IN ('open', 'submitted')) as pending_requests
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE e.employee_id = '550e8400-e29b-41d4-a716-446655440000';
\`\`\`

---

##### Get Personal Attendance Analytics
**Endpoint**: `GET /analytics/personal/attendance?days=30`

**Parameters**: `days` (default: 30, range: 1-365)

**Response** (200 OK):
\`\`\`json
[
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Samyak",
    "last_name": "Kumar",
    "email": "samyak@company.com",
    "department_name": "Engineering",
    "present_days": 20,
    "absent_days": 2,
    "leave_days": 3,
    "avg_hours_per_day": 8.1,
    "total_hours_month": 162,
    "total_records": 25
  }
]
\`\`\`

**Tables Used**: `attendance`, `employees`, `departments`

**SQL to calculate (last 30 days)**:
\`\`\`sql
SELECT e.employee_id, e.first_name, e.last_name, e.email,
       d.department_name,
       (SELECT COUNT(*) FROM attendance 
        WHERE employee_id = e.employee_id AND status = 'present'
        AND date >= DATE('now', '-30 days')) as present_days,
       (SELECT COUNT(*) FROM attendance 
        WHERE employee_id = e.employee_id AND status = 'absent'
        AND date >= DATE('now', '-30 days')) as absent_days,
       (SELECT COUNT(*) FROM attendance 
        WHERE employee_id = e.employee_id AND status = 'leave'
        AND date >= DATE('now', '-30 days')) as leave_days,
       ROUND((SELECT AVG(total_hours) FROM attendance 
        WHERE employee_id = e.employee_id 
        AND date >= DATE('now', '-30 days')), 2) as avg_hours_per_day,
       ROUND((SELECT SUM(total_hours) FROM attendance 
        WHERE employee_id = e.employee_id 
        AND date >= DATE('now', '-30 days')), 2) as total_hours_month,
       (SELECT COUNT(*) FROM attendance 
        WHERE employee_id = e.employee_id 
        AND date >= DATE('now', '-30 days')) as total_records
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE e.employee_id = '550e8400-e29b-41d4-a716-446655440000';
\`\`\`

---

##### Get Personal Timesheet Analytics
**Endpoint**: `GET /analytics/personal/timesheet?days=30`

**Response** (200 OK):
\`\`\`json
[
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Samyak",
    "last_name": "Kumar",
    "department_name": "Engineering",
    "project_name": "Mobile App Development",
    "total_entries": 10,
    "approved_entries": 8,
    "total_hours": 75,
    "approved_hours": 60,
    "approval_rate": 80.0
  }
]
\`\`\`

**Tables Used**: `timesheets`, `employees`, `projects`, `departments`

**SQL to calculate**:
\`\`\`sql
SELECT e.employee_id, e.first_name, e.last_name,
       d.department_name, p.project_name,
       COUNT(*) as total_entries,
       (SELECT COUNT(*) FROM timesheets 
        WHERE employee_id = e.employee_id 
        AND project_id = p.project_id 
        AND status = 'approved'
        AND date >= DATE('now', '-30 days')) as approved_entries,
       ROUND(SUM(t.hours), 2) as total_hours,
       ROUND((SELECT SUM(hours) FROM timesheets 
        WHERE employee_id = e.employee_id 
        AND project_id = p.project_id 
        AND status = 'approved'
        AND date >= DATE('now', '-30 days')), 2) as approved_hours,
       ROUND((SELECT COUNT(*) FROM timesheets 
        WHERE employee_id = e.employee_id 
        AND project_id = p.project_id 
        AND status = 'approved'
        AND date >= DATE('now', '-30 days')) * 100 / 
        COUNT(*), 2) as approval_rate
FROM timesheets t
JOIN employees e ON t.employee_id = e.employee_id
JOIN projects p ON t.project_id = p.project_id
JOIN departments d ON e.department_id = d.department_id
WHERE t.employee_id = '550e8400-e29b-41d4-a716-446655440000'
  AND t.date >= DATE('now', '-30 days')
GROUP BY e.employee_id, p.project_id;
\`\`\`

---

#### 2. Manager Analytics (Managers/Admins Only)

##### Get Team Overview
**Endpoint**: `GET /analytics/team/overview`

**Authorization**: Bearer token (Manager or Admin role required)

**Response** (200 OK):
\`\`\`json
{
  "total_team_members": 10,
  "present_today": 9,
  "absent_today": 1,
  "on_leave_today": 0,
  "total_pending_leaves": 3,
  "total_pending_timesheets": 5,
  "average_team_hours_week": 38.5,
  "team_members": [
    {
      "employee_id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Prachi Singh",
      "department": "Engineering",
      "status": "present",
      "hours_today": 8,
      "leaves_balance": 5
    }
  ]
}
\`\`\`

**Tables Used**: `employees`, `attendance`, `leave_requests`, `timesheets`, `departments`

---

##### Get Team Attendance Analytics
**Endpoint**: `GET /analytics/team/attendance?days=30`

**Response** (200 OK):
\`\`\`json
[
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440001",
    "first_name": "Prachi",
    "last_name": "Singh",
    "email": "prachi@company.com",
    "department_name": "Engineering",
    "present_days": 22,
    "absent_days": 1,
    "leave_days": 2,
    "avg_hours_per_day": 8.0,
    "total_hours_month": 176,
    "total_records": 25
  },
  ... (more team members)
]
\`\`\`

---

#### 3. Admin Analytics (Admin Only)

##### Get Leave Summary (System-wide)
**Endpoint**: `GET /analytics/admin/leave-summary`

**Authorization**: Bearer token (Admin role required)

**Response** (200 OK):
\`\`\`json
[
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Samyak",
    "last_name": "Kumar",
    "email": "samyak@company.com",
    "department_name": "Engineering",
    "total_approved_leaves": 5,
    "total_days_taken": 8,
    "pending_requests": 1
  },
  ... (all employees)
]
\`\`\`

**SQL to calculate**:
\`\`\`sql
SELECT e.employee_id, e.first_name, e.last_name, e.email,
       d.department_name,
       COUNT(CASE WHEN lr.status = 'approved' THEN 1 END) as total_approved_leaves,
       COALESCE(SUM(CASE WHEN lr.status = 'approved' THEN lr.total_days ELSE 0 END), 0) as total_days_taken,
       COUNT(CASE WHEN lr.status IN ('open', 'submitted') THEN 1 END) as pending_requests
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN leave_requests lr ON e.employee_id = lr.employee_id
GROUP BY e.employee_id
ORDER BY e.first_name;
\`\`\`

---

##### Get Department Summary
**Endpoint**: `GET /analytics/admin/department-summary`

**Response** (200 OK):
\`\`\`json
[
  {
    "department_id": 1,
    "department_name": "Engineering",
    "total_employees": 5,
    "active_employees": 4,
    "avg_attendance_hours": 39.2,
    "total_present_days": 98
  },
  {
    "department_id": 2,
    "department_name": "Sales",
    "total_employees": 3,
    "active_employees": 3,
    "avg_attendance_hours": 38.5,
    "total_present_days": 72
  }
]
\`\`\`

**Tables Used**: `departments`, `employees`, `attendance`

**SQL to calculate**:
\`\`\`sql
SELECT d.department_id, d.department_name,
       COUNT(e.employee_id) as total_employees,
       SUM(CASE WHEN e.status = 'active' THEN 1 ELSE 0 END) as active_employees,
       ROUND(AVG(a.total_hours), 2) as avg_attendance_hours,
       COUNT(CASE WHEN a.status = 'present' THEN 1 END) as total_present_days
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
LEFT JOIN attendance a ON e.employee_id = a.employee_id
GROUP BY d.department_id
ORDER BY d.department_name;
\`\`\`

---

##### Get Project Productivity
**Endpoint**: `GET /analytics/admin/project-productivity`

**Response** (200 OK):
\`\`\`json
[
  {
    "project_id": "550e8400-e29b-41d4-a716-446655440500",
    "project_name": "Mobile App Development",
    "client": "TechCorp Inc",
    "team_size": 3,
    "total_hours_logged": 450,
    "approved_timesheets": 380,
    "avg_daily_hours": 8.1
  }
]
\`\`\`

**Tables Used**: `projects`, `timesheets`, `employees`

**SQL to calculate**:
\`\`\`sql
SELECT p.project_id, p.project_name, p.client,
       COUNT(DISTINCT t.employee_id) as team_size,
       ROUND(SUM(t.hours), 2) as total_hours_logged,
       ROUND(SUM(CASE WHEN t.status = 'approved' THEN t.hours ELSE 0 END), 2) as approved_timesheets,
       ROUND(AVG(t.hours), 2) as avg_daily_hours
FROM projects p
LEFT JOIN timesheets t ON p.project_id = t.project_id
GROUP BY p.project_id
ORDER BY p.project_name;
\`\`\`

---

##### Get Compliance Metrics
**Endpoint**: `GET /analytics/admin/compliance`

**Response** (200 OK):
\`\`\`json
[
  {
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Samyak",
    "last_name": "Kumar",
    "pending_leave_requests": 1
  }
]
\`\`\`

**Tables Used**: `leave_requests`, `timesheets`

**SQL to calculate**:
\`\`\`sql
SELECT e.employee_id, e.first_name, e.last_name,
       COUNT(CASE WHEN lr.status IN ('open', 'submitted') THEN 1 END) as pending_leave_requests
FROM employees e
LEFT JOIN leave_requests lr ON e.employee_id = lr.employee_id
GROUP BY e.employee_id
HAVING pending_leave_requests > 0;
\`\`\`

---

## Database Tables Reference

### 1. `employees`
| Column | Type | Purpose |
|--------|------|---------|
| employee_id (PK) | UUID | Primary key |
| employee_code | VARCHAR | HR code (unique) |
| first_name | VARCHAR | Employee first name |
| last_name | VARCHAR | Employee last name |
| email | VARCHAR | Email (unique) |
| password_hash | VARCHAR | Hashed password |
| department_id (FK) | INT | Reference to departments |
| role_id (FK) | INT | Reference to roles |
| manager_id (FK) | UUID | Self-reference for manager hierarchy |
| join_date | DATE | Joining date |
| status | ENUM | 'active' or 'inactive' |

---

### 2. `roles`
| Column | Type | Purpose |
|--------|------|---------|
| role_id (PK) | INT | Primary key |
| role_name | VARCHAR | 'admin', 'manager', 'employee' |

---

### 3. `departments`
| Column | Type | Purpose |
|--------|------|---------|
| department_id (PK) | INT | Primary key |
| department_name | VARCHAR | Department name (unique) |

---

### 4. `leave_types`
| Column | Type | Purpose |
|--------|------|---------|
| leave_type_id (PK) | INT | Primary key |
| leave_name | VARCHAR | 'Sick', 'Casual', 'Earned', etc. |
| annual_limit | INT | Max days per year |
| monthly_accrual | DECIMAL | Days accrued per month |
| carry_forward_limit | INT | Max days that can be carried forward |
| is_carry_forward_allowed | BOOLEAN | Whether carry forward is allowed |

---

### 5. `employee_leave_balance`
| Column | Type | Purpose |
|--------|------|---------|
| balance_id (PK) | UUID | Primary key |
| employee_id (FK) | UUID | Reference to employees |
| leave_type_id (FK) | INT | Reference to leave_types |
| opening_balance | DECIMAL | Opening balance for the month |
| leaves_taken | DECIMAL | Days taken this month |
| accrued_this_month | DECIMAL | Days accrued this month |
| closing_balance | DECIMAL | Closing balance (opening - taken + accrued) |
| year | INT | Financial year |
| month | INT | Month number (1-12) |

---

### 6. `leave_requests`
| Column | Type | Purpose |
|--------|------|---------|
| leave_id (PK) | UUID | Primary key |
| employee_id (FK) | UUID | Reference to employees |
| leave_type_id (FK) | INT | Reference to leave_types |
| start_date | DATE | Leave start date |
| end_date | DATE | Leave end date |
| total_days | DECIMAL | Calculated total days |
| reason | TEXT | Reason for leave |
| status | ENUM | 'open', 'submitted', 'approved', 'rejected', 'cancelled' |
| created_at | DATETIME | Creation timestamp |
| submitted_at | DATETIME | Submission timestamp |
| approved_by (FK) | UUID | Manager/Admin who approved |
| approved_at | DATETIME | Approval timestamp |

---

### 7. `attendance`
| Column | Type | Purpose |
|--------|------|---------|
| attendance_id (PK) | UUID | Primary key |
| employee_id (FK) | UUID | Reference to employees |
| date | DATE | Attendance date |
| check_in | DATETIME | Check-in timestamp |
| check_out | DATETIME | Check-out timestamp |
| total_hours | DECIMAL(5,2) | Calculated hours (capped at 8) |
| status | ENUM | 'present', 'leave', 'holiday', 'absent' |

---

### 8. `weekly_attendance_summary`
| Column | Type | Purpose |
|--------|------|---------|
| summary_id (PK) | UUID | Primary key |
| employee_id (FK) | UUID | Reference to employees |
| week_start_date | DATE | Monday of the week |
| week_end_date | DATE | Sunday of the week |
| total_hours | DECIMAL(5,2) | Total hours for the week |
| over_time | DECIMAL(5,2) | Hours over 40 |

---

### 9. `projects`
| Column | Type | Purpose |
|--------|------|---------|
| project_id (PK) | UUID | Primary key |
| project_name | VARCHAR | Project name |
| description | TEXT | Project description |
| client | VARCHAR | Client name |
| start_date | DATE | Project start date |
| end_date | DATE | Project end date |
| status | ENUM | 'active' or 'closed' |

---

### 10. `tasks`
| Column | Type | Purpose |
|--------|------|---------|
| task_id (PK) | UUID | Primary key |
| project_id (FK) | UUID | Reference to projects |
| task_name | VARCHAR | Task name |
| description | TEXT | Task description |

---

### 11. `timesheets`
| Column | Type | Purpose |
|--------|------|---------|
| timesheet_id (PK) | UUID | Primary key |
| employee_id (FK) | UUID | Reference to employees |
| project_id (FK) | UUID | Reference to projects |
| task_id (FK) | UUID | Reference to tasks |
| date | DATE | Date of work |
| hours | DECIMAL(5,2) | Hours worked (capped at 8) |
| description | TEXT | Work description |
| status | ENUM | 'open', 'submitted', 'approved', 'rejected' |
| approved_by (FK) | UUID | Manager/Admin who approved |
| approved_at | DATETIME | Approval timestamp |

---

### 12. `approval_workflow`
| Column | Type | Purpose |
|--------|------|---------|
| workflow_id (PK) | UUID | Primary key |
| request_type | ENUM | 'leave' or 'timesheet' |
| request_id | UUID | Reference to leave_id or timesheet_id |
| approver_id (FK) | UUID | Reference to employees (approver) |
| action | ENUM | 'submitted', 'approved', 'rejected' |
| action_at | DATETIME | Action timestamp |
| remarks | TEXT | Comments from approver |

---

## Complete Request/Response Examples

### Complete Leave Workflow Example

**Step 1: Employee Creates Leave Request**
\`\`\`bash
curl -X POST http://localhost:8000/leave-requests/ \
  -H "Authorization: Bearer {employee_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "leave_type_id": 1,
    "start_date": "2025-02-10",
    "end_date": "2025-02-12",
    "reason": "Medical appointment"
  }'
\`\`\`

Response:
\`\`\`json
{
  "leave_id": "550e8400-e29b-41d4-a716-446655440100",
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "open",
  "created_at": "2025-02-01T10:00:00"
}
\`\`\`

**Step 2: Employee Submits Leave Request**
\`\`\`bash
curl -X PUT http://localhost:8000/leave-requests/550e8400-e29b-41d4-a716-446655440100/submit \
  -H "Authorization: Bearer {employee_token}"
\`\`\`

Response:
\`\`\`json
{
  "leave_id": "550e8400-e29b-41d4-a716-446655440100",
  "status": "submitted",
  "submitted_at": "2025-02-01T10:05:00"
}
\`\`\`

**Step 3: Manager Approves Leave**
\`\`\`bash
curl -X PUT http://localhost:8000/leave-requests/550e8400-e29b-41d4-a716-446655440100/approve \
  -H "Authorization: Bearer {manager_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approved"
  }'
\`\`\`

Response:
\`\`\`json
{
  "leave_id": "550e8400-e29b-41d4-a716-446655440100",
  "status": "approved",
  "approved_by": "550e8400-e29b-41d4-a716-446655440050",
  "approved_at": "2025-02-01T11:00:00"
}
\`\`\`

**Step 4: Verify Attendance Auto-Marked**
\`\`\`sql
SELECT date, status, check_in, check_out 
FROM attendance 
WHERE employee_id = '550e8400-e29b-41d4-a716-446655440000'
  AND date BETWEEN '2025-02-10' AND '2025-02-12'
ORDER BY date;
\`\`\`

Result:
\`\`\`
date       | status | check_in | check_out
-----------|--------|----------|----------
2025-02-10 | leave  | NULL     | NULL
2025-02-11 | leave  | NULL     | NULL
2025-02-12 | leave  | NULL     | NULL
\`\`\`

---

### Complete Weekly Timesheet Workflow Example

**Step 1: Employee Fills Weekly Timesheet**
\`\`\`bash
curl -X POST http://localhost:8000/timesheets/weekly \
  -H "Authorization: Bearer {employee_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2025-02-03",
    "project_id": "550e8400-e29b-41d4-a716-446655440500",
    "task_id": "550e8400-e29b-41d4-a716-446655440550",
    "entries": [
      {"date": "2025-02-03", "hours": 8, "description": "UI design setup"},
      {"date": "2025-02-04", "hours": 8, "description": "Login screen design"},
      {"date": "2025-02-05", "hours": 8, "description": "Dashboard design"},
      {"date": "2025-02-06", "hours": 8, "description": "Settings screen"},
      {"date": "2025-02-07", "hours": 8, "description": "Final review"}
    ]
  }'
\`\`\`

Response:
\`\`\`json
{
  "week_start_date": "2025-02-03",
  "week_end_date": "2025-02-09",
  "total_hours": 40,
  "entries_created": 5,
  "timesheets": [
    {
      "timesheet_id": "550e8400-e29b-41d4-a716-446655440600",
      "employee_id": "550e8400-e29b-41d4-a716-446655440000",
      "date": "2025-02-03",
      "hours": 8,
      "status": "open"
    },
    ... (4 more)
  ]
}
\`\`\`

**Step 2: Employee Submits Week**
\`\`\`bash
curl -X PUT http://localhost:8000/timesheets/week/2025-02-03/submit \
  -H "Authorization: Bearer {employee_token}"
\`\`\`

Response:
\`\`\`json
{
  "message": "Submitted 5 timesheets for week starting 2025-02-03",
  "count": 5
}
\`\`\`

**Step 3: Manager Approves Timesheets**
\`\`\`bash
# Approve each timesheet
curl -X PUT http://localhost:8000/timesheets/550e8400-e29b-41d4-a716-446655440600/approve \
  -H "Authorization: Bearer {manager_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approved",
    "remarks": "Good allocation"
  }'
\`\`\`

---

## Summary

This comprehensive HRMS backend provides:

1. **Complete RBAC**: Three-tier access control (Employee, Manager, Admin)
2. **Leave Management**: Full lifecycle from creation to approval with auto-attendance marking
3. **Attendance Tracking**: Daily check-in/out with weekly summary generation
4. **Timesheet Management**: Single-day and weekly bulk entry with manager approval
5. **Analytics**: Personal, team, and system-wide insights
6. **Audit Trail**: Complete approval workflow tracking

All endpoints are documented with request/response examples, database table references, and SQL queries for testing and understanding.
