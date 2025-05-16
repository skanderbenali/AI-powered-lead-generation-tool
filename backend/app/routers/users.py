from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User as UserModel
from app.schemas import User, UserProfileUpdate
from app.deps.auth import get_current_user

# Create router
router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/profile", response_model=User)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile information
    
    This endpoint allows users to update their profile data such as:
    - username
    - full_name
    - avatar_url (profile picture)
    - Additional profile fields like bio, company, job_title, location
    
    The email address cannot be changed after registration.
    """
    # Get the user from the database
    user_db = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow changing the email address
    # Also check if username is changed and make sure it's not already taken
    if profile_data.username and profile_data.username != user_db.username:
        existing_user = db.query(UserModel).filter(UserModel.username == profile_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user_db.username = profile_data.username
    
    # Update allowed fields
    if profile_data.full_name is not None:
        user_db.full_name = profile_data.full_name
        
    if profile_data.avatar_url is not None:
        user_db.avatar_url = profile_data.avatar_url
    
    # Update additional profile fields if they exist in the model
    # These could be stored in a separate profile table or JSON field
    # For now we're assuming these fields might be added to the User model
    for field in ["bio", "company", "job_title", "location"]:
        if hasattr(profile_data, field) and getattr(profile_data, field) is not None:
            # Only update if the attribute exists on the User model
            if hasattr(user_db, field):
                setattr(user_db, field, getattr(profile_data, field))
    
    # Save changes to the database
    db.commit()
    db.refresh(user_db)
    
    return user_db
