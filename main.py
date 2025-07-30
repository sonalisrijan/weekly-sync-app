from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
import hashlib

from models import User, WeeklyReport, create_tables, get_db

app = FastAPI(title="1:1 Weekly Report System", version="1.0.0")

# Create database tables on startup
create_tables()

# Pydantic models for API
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    team_name: str
    current_position: str
    office_location: str
    mentor_email: Optional[EmailStr] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    user_type: str
    team_name: str
    current_position: str
    office_location: str
    mentor_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class WeeklyReportCreate(BaseModel):
    week_number: int
    year: int
    accomplishments: str
    blockers_concerns_comments: str
    aspirations: str

class WeeklyReportResponse(BaseModel):
    id: int
    mentee_id: int
    mentor_id: int
    week_number: int
    year: int
    accomplishments: str
    blockers_concerns_comments: str
    aspirations: str
    submission_date: datetime
    mentee_name: str
    
    class Config:
        from_attributes = True

# Utility functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "1:1 Weekly Report System API"}

# User Registration
@app.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Determine user type and mentor
    mentor_id = None
    user_type = "mentor"
    
    if user_data.mentor_email:
        mentor = get_user_by_email(db, user_data.mentor_email)
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentor email not found"
            )
        if mentor.user_type != "mentor":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Specified user is not a mentor"
            )
        mentor_id = mentor.id
        user_type = "mentee"
    
    # Create new user
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        user_type=user_type,
        mentor_id=mentor_id,
        team_name=user_data.team_name,
        current_position=user_data.current_position,
        office_location=user_data.office_location
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# User Login
@app.post("/login", response_model=UserResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_data.email)
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    return user

# Get user profile
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Get mentees for a mentor
@app.get("/mentors/{mentor_id}/mentees", response_model=List[UserResponse])
async def get_mentees(mentor_id: int, db: Session = Depends(get_db)):
    # Verify mentor exists
    mentor = db.query(User).filter(and_(User.id == mentor_id, User.user_type == "mentor")).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    
    # Get all mentees for this mentor
    mentees = db.query(User).filter(
        and_(User.mentor_id == mentor_id, User.is_active == True)
    ).all()
    
    return mentees

# Create weekly report (mentees only)
@app.post("/weekly-reports", response_model=WeeklyReportResponse)
async def create_weekly_report(
    report_data: WeeklyReportCreate, 
    mentee_id: int, 
    db: Session = Depends(get_db)
):
    # Verify mentee exists and is actually a mentee
    mentee = db.query(User).filter(
        and_(User.id == mentee_id, User.user_type == "mentee")
    ).first()
    if not mentee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentee not found"
        )
    
    # Check if report already exists for this week
    existing_report = db.query(WeeklyReport).filter(
        and_(
            WeeklyReport.mentee_id == mentee_id,
            WeeklyReport.week_number == report_data.week_number,
            WeeklyReport.year == report_data.year
        )
    ).first()
    
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report already exists for week {report_data.week_number}, {report_data.year}"
        )
    
    # Create new report
    db_report = WeeklyReport(
        mentee_id=mentee_id,
        mentor_id=mentee.mentor_id,
        week_number=report_data.week_number,
        year=report_data.year,
        accomplishments=report_data.accomplishments,
        blockers_concerns_comments=report_data.blockers_concerns_comments,
        aspirations=report_data.aspirations
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Return report with mentee name
    response = WeeklyReportResponse(
        id=db_report.id,
        mentee_id=db_report.mentee_id,
        mentor_id=db_report.mentor_id,
        week_number=db_report.week_number,
        year=db_report.year,
        accomplishments=db_report.accomplishments,
        blockers_concerns_comments=db_report.blockers_concerns_comments,
        aspirations=db_report.aspirations,
        submission_date=db_report.submission_date,
        mentee_name=mentee.name
    )
    
    return response

# Get latest 2 reports for a mentee
@app.get("/mentees/{mentee_id}/reports/latest", response_model=List[WeeklyReportResponse])
async def get_latest_reports(mentee_id: int, db: Session = Depends(get_db)):
    # Verify mentee exists
    mentee = db.query(User).filter(User.id == mentee_id).first()
    if not mentee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentee not found"
        )
    
    # Get latest 2 reports
    reports = db.query(WeeklyReport).filter(
        WeeklyReport.mentee_id == mentee_id
    ).order_by(
        WeeklyReport.year.desc(),
        WeeklyReport.week_number.desc()
    ).limit(2).all()
    
    # Format response with mentee name
    response_reports = []
    for report in reports:
        response_reports.append(WeeklyReportResponse(
            id=report.id,
            mentee_id=report.mentee_id,
            mentor_id=report.mentor_id,
            week_number=report.week_number,
            year=report.year,
            accomplishments=report.accomplishments,
            blockers_concerns_comments=report.blockers_concerns_comments,
            aspirations=report.aspirations,
            submission_date=report.submission_date,
            mentee_name=mentee.name
        ))
    
    return response_reports

# Get all reports for a mentor's mentees
@app.get("/mentors/{mentor_id}/reports", response_model=List[WeeklyReportResponse])
async def get_mentor_reports(mentor_id: int, db: Session = Depends(get_db)):
    # Verify mentor exists
    mentor = db.query(User).filter(
        and_(User.id == mentor_id, User.user_type == "mentor")
    ).first()
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found"
        )
    
    # Get all reports for this mentor's mentees
    reports = db.query(WeeklyReport, User.name).join(
        User, WeeklyReport.mentee_id == User.id
    ).filter(
        WeeklyReport.mentor_id == mentor_id
    ).order_by(
        WeeklyReport.submission_date.desc()
    ).all()
    
    # Format response
    response_reports = []
    for report, mentee_name in reports:
        response_reports.append(WeeklyReportResponse(
            id=report.id,
            mentee_id=report.mentee_id,
            mentor_id=report.mentor_id,
            week_number=report.week_number,
            year=report.year,
            accomplishments=report.accomplishments,
            blockers_concerns_comments=report.blockers_concerns_comments,
            aspirations=report.aspirations,
            submission_date=report.submission_date,
            mentee_name=mentee_name
        ))
    
    return response_reports

# Update weekly report
@app.put("/weekly-reports/{report_id}", response_model=WeeklyReportResponse)
async def update_weekly_report(
    report_id: int,
    report_data: WeeklyReportCreate,
    db: Session = Depends(get_db)
):
    # Get existing report
    report = db.query(WeeklyReport).filter(WeeklyReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Update report fields
    report.week_number = report_data.week_number
    report.year = report_data.year
    report.accomplishments = report_data.accomplishments
    report.blockers_concerns_comments = report_data.blockers_concerns_comments
    report.aspirations = report_data.aspirations
    report.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(report)
    
    # Get mentee name for response
    mentee = db.query(User).filter(User.id == report.mentee_id).first()
    
    response = WeeklyReportResponse(
        id=report.id,
        mentee_id=report.mentee_id,
        mentor_id=report.mentor_id,
        week_number=report.week_number,
        year=report.year,
        accomplishments=report.accomplishments,
        blockers_concerns_comments=report.blockers_concerns_comments,
        aspirations=report.aspirations,
        submission_date=report.submission_date,
        mentee_name=mentee.name
    )
    
    return response

# Delete weekly report
@app.delete("/weekly-reports/{report_id}")
async def delete_weekly_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(WeeklyReport).filter(WeeklyReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"}