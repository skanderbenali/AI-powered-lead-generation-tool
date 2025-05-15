from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas import User, UserCreate, Token
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.services.user import create_user, get_user_by_email, get_user_by_username

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user_by_email = get_user_by_email(db, email=user_data.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    db_user_by_username = get_user_by_username(db, username=user_data.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_data_dict = user_data.dict()
    user_data_dict.pop("password")
    new_user = create_user(db, user_data_dict, hashed_password)
    
    return new_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
