from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime, timezone

from models import User, WeeklyReport
from app.schemas.reports import WeeklyReportCreate, WeeklyReportResponse


def create_weekly_report(db: Session, mentee_id: int, report_data: WeeklyReportCreate) -> WeeklyReportResponse:
    """Create a new weekly report for a mentee"""
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
    return WeeklyReportResponse(
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


def get_latest_reports_for_mentee(db: Session, mentee_id: int) -> list[WeeklyReportResponse]:
    """Get the latest 2 reports for a mentee"""
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
    return [
        WeeklyReportResponse(
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
        for report in reports
    ]


def get_reports_for_mentor(db: Session, mentor_id: int) -> list[WeeklyReportResponse]:
    """Get all reports for a mentor's mentees"""
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
    return [
        WeeklyReportResponse(
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
        )
        for report, mentee_name in reports
    ]


def update_weekly_report(db: Session, report_id: int, report_data: WeeklyReportCreate) -> WeeklyReportResponse:
    """Update an existing weekly report"""
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
    
    return WeeklyReportResponse(
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


def delete_weekly_report(db: Session, report_id: int) -> dict:
    """Delete a weekly report"""
    report = db.query(WeeklyReport).filter(WeeklyReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"} 