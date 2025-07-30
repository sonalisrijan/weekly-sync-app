from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(10), nullable=False)  # 'mentor' or 'mentee'
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    team_name = Column(String(100), nullable=False)
    current_position = Column(String(100), nullable=False)
    office_location = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    mentor = relationship("User", remote_side=[id], backref="mentees")
    weekly_reports_as_mentee = relationship("WeeklyReport", foreign_keys="WeeklyReport.mentee_id", back_populates="mentee")
    weekly_reports_as_mentor = relationship("WeeklyReport", foreign_keys="WeeklyReport.mentor_id", back_populates="mentor")

class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    accomplishments = Column(Text, nullable=False)
    blockers_concerns_comments = Column(Text, nullable=False)
    aspirations = Column(Text, nullable=False)
    submission_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    mentee = relationship("User", foreign_keys=[mentee_id], back_populates="weekly_reports_as_mentee")
    mentor = relationship("User", foreign_keys=[mentor_id], back_populates="weekly_reports_as_mentor")
    
    # Ensure one report per mentee per week per year
    __table_args__ = (UniqueConstraint('mentee_id', 'week_number', 'year', name='unique_mentee_week_year'),)

# Database setup
DATABASE_URL = "sqlite:///./weekly_reports.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

