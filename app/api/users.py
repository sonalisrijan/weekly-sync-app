from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models import get_db
from app.schemas.users import UserResponse
from app.services.user_service import get_user_by_id, get_mentees_for_mentor

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@router.get("/mentors/{mentor_id}/mentees", response_model=List[UserResponse])
async def get_mentees(mentor_id: int, db: Session = Depends(get_db)):
    """Get all mentees for a specific mentor"""
    return get_mentees_for_mentor(db, mentor_id) 