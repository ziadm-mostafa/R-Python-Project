from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token


logger = logging.getLogger("library.auth")

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    existing_user = db.query(User).filter(
        (User.username == user_data.username) |
        (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username or email already exists"
        )

    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role="member"
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"user registered: {new_user.username}")

        return new_user

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="registration failed"
        )


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.username == user_data.username).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        logger.warning(f"failed login attempt: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials"
        )

    token = create_access_token({
        "sub": user.username,
        "role": user.role,
        "user_id": user.id
    })

    logger.info(f"user logged in: {user.username}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }