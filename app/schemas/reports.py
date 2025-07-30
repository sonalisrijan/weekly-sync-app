from pydantic import BaseModel
from datetime import datetime


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