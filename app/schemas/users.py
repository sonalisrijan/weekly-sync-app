from pydantic import BaseModel, EmailStr
from typing import Optional


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