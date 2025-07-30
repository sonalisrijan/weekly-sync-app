from fastapi import FastAPI

from models import create_tables
from app.api import auth, users, reports

# Create database tables on startup
create_tables()

# Initialize FastAPI app
app = FastAPI(
    title="1:1 Weekly Report System",
    description="A system for managing mentor-mentee weekly sync reports",
    version="2.0.0"
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "1:1 Weekly Report System API",
        "version": "2.0.0",
        "docs": "/docs"
    }

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reports.router) 