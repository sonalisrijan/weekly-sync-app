from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import get_db
from app.schemas.users import UserCreate, UserLogin, UserResponse
from app.services.user_service import create_user
from app.services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (mentor or mentee)"""
    return create_user(db, user_data)


@router.post("/login", response_model=UserResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user login"""
    return authenticate_user(db, login_data) 