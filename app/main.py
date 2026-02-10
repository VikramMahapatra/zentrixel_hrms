from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base, init_db
from app.routers import auth, employees, departments, roles, leave_types, leave_requests, attendance, projects, tasks, timesheets, approval_workflow, analytics,role_policies

# Initialize database on startup
def setup_db():
    Base.metadata.create_all(bind=engine)
    init_db(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_db()
    yield

app = FastAPI(
    title="HRMS Backend API",
    description="Human Resource Management System with Leave, Attendance, and Timesheet Management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(departments.router, prefix="/api/departments", tags=["Departments"])
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])
app.include_router(leave_types.router, prefix="/api/leave-types", tags=["Leave Types"])
app.include_router(leave_requests.router, prefix="/api/leave-requests", tags=["Leave Requests"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(timesheets.router, prefix="/api/timesheets", tags=["Timesheets"])
app.include_router(approval_workflow.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(role_policies.router, prefix="/api/role-policies", tags=["Role Policies"])

@app.get("/")
def read_root():
    return {"message": "HRMS Backend API is running"}
