from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from models import get_db
from app.schemas.reports import WeeklyReportCreate, WeeklyReportResponse
from app.services.report_service import (
    create_weekly_report,
    get_latest_reports_for_mentee,
    get_reports_for_mentor,
    update_weekly_report,
    delete_weekly_report
)

router = APIRouter(prefix="/reports", tags=["Weekly Reports"])


@router.post("/", response_model=WeeklyReportResponse)
async def create_report(
    report_data: WeeklyReportCreate, 
    mentee_id: int, 
    db: Session = Depends(get_db)
):
    """Create a new weekly report (mentees only)"""
    return create_weekly_report(db, mentee_id, report_data)


@router.get("/mentees/{mentee_id}/latest", response_model=List[WeeklyReportResponse])
async def get_latest_mentee_reports(mentee_id: int, db: Session = Depends(get_db)):
    """Get the latest 2 reports for a mentee"""
    return get_latest_reports_for_mentee(db, mentee_id)


@router.get("/mentors/{mentor_id}", response_model=List[WeeklyReportResponse])
async def get_mentor_reports(mentor_id: int, db: Session = Depends(get_db)):
    """Get all reports for a mentor's mentees"""
    return get_reports_for_mentor(db, mentor_id)


@router.put("/{report_id}", response_model=WeeklyReportResponse)
async def update_report(
    report_id: int,
    report_data: WeeklyReportCreate,
    db: Session = Depends(get_db)
):
    """Update an existing weekly report"""
    return update_weekly_report(db, report_id, report_data)


@router.delete("/{report_id}")
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a weekly report"""
    return delete_weekly_report(db, report_id) 