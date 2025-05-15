from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.models.user import User


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: Dict[str, Any], hashed_password: str) -> User:
    """Create a new user"""
    db_user = User(
        email=user_data["email"],
        username=user_data["username"],
        full_name=user_data.get("full_name"),
        hashed_password=hashed_password,
        is_active=user_data.get("is_active", True),
        is_superuser=user_data.get("is_superuser", False)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
    """Update a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
        
    for key, value in user_data.items():
        if value is not None and hasattr(db_user, key):
            setattr(db_user, key, value)
            
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
        
    db.delete(db_user)
    db.commit()
    return True
