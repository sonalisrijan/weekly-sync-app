from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import User
from app.schemas.users import UserLogin
from app.utils.security import verify_password
from app.services.user_service import get_user_by_email


def authenticate_user(db: Session, login_data: UserLogin) -> User:
    """Authenticate user login credentials"""
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