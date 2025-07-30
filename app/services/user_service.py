from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from models import User
from app.schemas.users import UserCreate
from app.utils.security import hash_password


def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email address"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user (mentee or mentor)"""
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


def get_mentees_for_mentor(db: Session, mentor_id: int) -> list[User]:
    """Get all mentees for a specific mentor"""
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