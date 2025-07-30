#!/usr/bin/env python3
"""
Test script for models.py - Creates example tables and demonstrates model functionality
"""

from models import User, WeeklyReport, create_tables, SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os

def reset_database():
    """Remove existing database and recreate tables"""
    db_file = "weekly_reports.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed existing database: {db_file}")
    
    create_tables()
    print("Created fresh database tables")

def create_sample_users(db: Session):
    """Create sample mentor and mentee users"""
    print("\n=== Creating Sample Users ===")
    
    # Create mentors
    mentor1 = User(
        name="Alice Johnson",
        email="alice.johnson@company.com",
        password_hash="hashed_password_1",
        user_type="mentor",
        mentor_id=None,  # Mentors don't have mentors
        team_name="Engineering",
        current_position="Senior Software Engineer",
        office_location="New York"
    )
    
    mentor2 = User(
        name="Bob Smith",
        email="bob.smith@company.com",
        password_hash="hashed_password_2",
        user_type="mentor",
        mentor_id=None,
        team_name="Product",
        current_position="Product Manager",
        office_location="San Francisco"
    )
    
    db.add_all([mentor1, mentor2])
    db.commit()
    db.refresh(mentor1)
    db.refresh(mentor2)
    
    print(f"Created mentor: {mentor1.name} (ID: {mentor1.id})")
    print(f"Created mentor: {mentor2.name} (ID: {mentor2.id})")
    
    # Create mentees
    mentee1 = User(
        name="Charlie Brown",
        email="charlie.brown@company.com",
        password_hash="hashed_password_3",
        user_type="mentee",
        mentor_id=mentor1.id,  # Assigned to Alice
        team_name="Engineering",
        current_position="Junior Software Engineer",
        office_location="New York"
    )
    
    mentee2 = User(
        name="Diana Prince",
        email="diana.prince@company.com",
        password_hash="hashed_password_4",
        user_type="mentee",
        mentor_id=mentor1.id,  # Also assigned to Alice
        team_name="Engineering",
        current_position="Software Engineer Intern",
        office_location="Remote"
    )
    
    mentee3 = User(
        name="Edward Wilson",
        email="edward.wilson@company.com",
        password_hash="hashed_password_5",
        user_type="mentee",
        mentor_id=mentor2.id,  # Assigned to Bob
        team_name="Product",
        current_position="Associate Product Manager",
        office_location="San Francisco"
    )
    
    db.add_all([mentee1, mentee2, mentee3])
    db.commit()
    
    print(f"Created mentee: {mentee1.name} (ID: {mentee1.id}) -> Mentor: {mentor1.name}")
    print(f"Created mentee: {mentee2.name} (ID: {mentee2.id}) -> Mentor: {mentor1.name}")
    print(f"Created mentee: {mentee3.name} (ID: {mentee3.id}) -> Mentor: {mentor2.name}")
    
    return mentor1, mentor2, mentee1, mentee2, mentee3

def create_sample_reports(db: Session, mentees):
    """Create sample weekly reports"""
    print("\n=== Creating Sample Weekly Reports ===")
    
    mentee1, mentee2, mentee3 = mentees
    
    # Week 1 reports
    report1 = WeeklyReport(
        mentee_id=mentee1.id,
        mentor_id=mentee1.mentor_id,
        week_number=1,
        year=2024,
        accomplishments="Completed onboarding training and set up development environment. Fixed 2 minor bugs in the user authentication system.",
        blockers_concerns_comments="Having trouble understanding the legacy codebase architecture. Need guidance on testing best practices.",
        aspirations="Want to learn more about system design and contribute to a major feature this quarter."
    )
    
    report2 = WeeklyReport(
        mentee_id=mentee2.id,
        mentor_id=mentee2.mentor_id,
        week_number=1,
        year=2024,
        accomplishments="Finished React tutorial and created first component for the dashboard. Attended all team standups.",
        blockers_concerns_comments="Need help with state management in React. Code reviews are taking longer than expected.",
        aspirations="Goal is to become proficient in frontend development and eventually work on full-stack features."
    )
    
    report3 = WeeklyReport(
        mentee_id=mentee3.id,
        mentor_id=mentee3.mentor_id,
        week_number=1,
        year=2024,
        accomplishments="Conducted user interviews for the new feature. Created wireframes and initial product requirements document.",
        blockers_concerns_comments="Stakeholders have conflicting priorities. Need help prioritizing features for the roadmap.",
        aspirations="Want to improve my skills in data analysis and learn more about A/B testing methodologies."
    )
    
    # Week 2 reports
    report4 = WeeklyReport(
        mentee_id=mentee1.id,
        mentor_id=mentee1.mentor_id,
        week_number=2,
        year=2024,
        accomplishments="Implemented a new API endpoint for user preferences. Wrote comprehensive unit tests.",
        blockers_concerns_comments="Performance issues with database queries. Need to optimize some slow endpoints.",
        aspirations="Looking forward to presenting my work at the next team demo and getting feedback."
    )
    
    db.add_all([report1, report2, report3, report4])
    db.commit()
    
    print(f"Created report for {mentee1.name} - Week 1, 2024")
    print(f"Created report for {mentee2.name} - Week 1, 2024")
    print(f"Created report for {mentee3.name} - Week 1, 2024")
    print(f"Created report for {mentee1.name} - Week 2, 2024")

def test_relationships(db: Session):
    """Test model relationships and demonstrate queries"""
    print("\n=== Testing Model Relationships ===")
    
    # Test mentor-mentee relationships
    mentors = db.query(User).filter(User.user_type == "mentor").all()
    
    for mentor in mentors:
        print(f"\nMentor: {mentor.name}")
        print(f"  Mentees: {[mentee.name for mentee in mentor.mentees]}")
        print(f"  Reports to review: {len(mentor.weekly_reports_as_mentor)}")
    
    # Test mentee reports
    mentees = db.query(User).filter(User.user_type == "mentee").all()
    
    for mentee in mentees:
        print(f"\nMentee: {mentee.name}")
        print(f"  Mentor: {mentee.mentor.name if mentee.mentor else 'No mentor assigned'}")
        print(f"  Reports submitted: {len(mentee.weekly_reports_as_mentee)}")
        
        for report in mentee.weekly_reports_as_mentee:
            print(f"    Week {report.week_number}, {report.year}: {report.accomplishments[:50]}...")

def test_queries(db: Session):
    """Demonstrate various database queries"""
    print("\n=== Testing Database Queries ===")
    
    # Query 1: Get all reports for a specific week
    week1_reports = db.query(WeeklyReport).filter(
        WeeklyReport.week_number == 1,
        WeeklyReport.year == 2024
    ).all()
    
    print(f"\nWeek 1, 2024 reports: {len(week1_reports)}")
    for report in week1_reports:
        print(f"  {report.mentee.name}: {report.accomplishments[:30]}...")
    
    # Query 2: Get all mentees for a specific mentor
    mentor = db.query(User).filter(User.name == "Alice Johnson").first()
    if mentor:
        mentee_count = len(mentor.mentees)
        print(f"\n{mentor.name} has {mentee_count} mentees:")
        for mentee in mentor.mentees:
            print(f"  - {mentee.name} ({mentee.current_position})")
    
    # Query 3: Get reports that need attention (with blockers/concerns)
    reports_with_blockers = db.query(WeeklyReport).filter(
        WeeklyReport.blockers_concerns_comments.isnot(None)
    ).all()
    
    print(f"\nReports with blockers/concerns: {len(reports_with_blockers)}")
    for report in reports_with_blockers:
        print(f"  {report.mentee.name}: {report.blockers_concerns_comments[:40]}...")

def main():
    """Main test function"""
    print("Testing Models.py - Weekly Sync App")
    print("=" * 50)
    
    # Reset and create fresh database
    reset_database()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create sample data
        mentor1, mentor2, mentee1, mentee2, mentee3 = create_sample_users(db)
        create_sample_reports(db, (mentee1, mentee2, mentee3))
        
        # Test relationships and queries
        test_relationships(db)
        test_queries(db)
        
        print("\n✅ All tests completed successfully!")
        print("\nDatabase file created: weekly_reports.db")
        print("You can now inspect the database using SQLite tools or continue testing the API.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
