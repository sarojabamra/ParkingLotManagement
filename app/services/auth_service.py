import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.constants import UserRole
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.auth import (
    create_access_token,
    hash_password,
    verify_password,
)

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def register_user(request: UserCreate, db: Session):
    existing_user = db.query(User).filter(User.name == request.name).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    hashed_password = hash_password(request.password)

    user = User(
        name=request.name,
        password=hashed_password,
        role=UserRole.PUBLIC,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(
    db: Session,
    username: str,
    password: str,
):
    user = db.query(User).filter(User.name == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    verify_password(password, user.password)

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role.value,
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
