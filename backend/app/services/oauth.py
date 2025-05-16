import requests
from typing import Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from app.schemas.user import OAuthUserInfo, AuthProvider
from app.services.user import get_user_by_email, create_user
from app.services.auth import create_access_token, get_random_string
from datetime import timedelta
from app.core.oauth import google_config, github_config
import json


async def get_google_user_info(access_token: str) -> OAuthUserInfo:
    """Get user info from Google OAuth"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(google_config["userinfo_url"], headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get user info from Google. Status: {response.status_code}, Response: {response.text}")
    
    data = response.json()
    return OAuthUserInfo(
        provider=AuthProvider.GOOGLE,
        provider_user_id=data["sub"],
        email=data["email"],
        username=data.get("email", "").split("@")[0],  # Use part before @ as username
        full_name=data.get("name"),
        avatar_url=data.get("picture")
    )


async def get_github_user_info(access_token: str) -> OAuthUserInfo:
    """Get user info from GitHub OAuth"""
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/json"
    }
    
    # First get the user profile
    user_response = requests.get(github_config["userinfo_url"], headers=headers)
    if user_response.status_code != 200:
        raise Exception(f"Failed to get user info from GitHub. Status: {user_response.status_code}, Response: {user_response.text}")
    
    user_data = user_response.json()
    
    # GitHub may not provide email, we need to make a separate request for emails
    email = user_data.get("email")
    if not email:
        email_response = requests.get("https://api.github.com/user/emails", headers=headers)
        if email_response.status_code == 200:
            emails_data = email_response.json()
            # Get the primary email
            primary_email = next((email["email"] for email in emails_data if email["primary"]), None)
            email = primary_email or (emails_data[0]["email"] if emails_data else None)
    
    if not email:
        raise Exception("Could not retrieve email from GitHub account")
    
    return OAuthUserInfo(
        provider=AuthProvider.GITHUB,
        provider_user_id=str(user_data["id"]),
        email=email,
        username=user_data.get("login"),
        full_name=user_data.get("name"),
        avatar_url=user_data.get("avatar_url")
    )


async def authenticate_oauth_user(db: Session, user_info: Dict[str, Any] | OAuthUserInfo) -> Tuple[Dict[str, str], bool]:
    """
    Authenticate or create a user based on OAuth data
    Returns a tuple of (token_data, is_new_user)
    
    Args:
        db: Database session
        user_info: User information, either as an OAuthUserInfo object or a dictionary
    """
    # Convert dictionary to proper format if needed
    if isinstance(user_info, dict):
        print(f"Converting dictionary to OAuthUserInfo: {user_info}")
        # Handle the dictionary format
        email = user_info.get("email")
        if not email:
            raise ValueError("Email is required for OAuth authentication")
            
        # Get or create username from email
        username = user_info.get("username", email.split("@")[0])
        
        # Determine provider
        provider_str = user_info.get("auth_provider", "google").lower()
        if provider_str == "google":
            provider = AuthProvider.GOOGLE
        elif provider_str == "github":
            provider = AuthProvider.GITHUB
        else:
            provider = AuthProvider.LOCAL
            
        # Create proper OAuthUserInfo object
        user_info = OAuthUserInfo(
            provider=provider,
            provider_user_id=user_info.get("sub", str(hash(email))),  # Use a hash of email if no ID
            email=email,
            username=username,
            full_name=user_info.get("name"),
            avatar_url=user_info.get("picture")
        )
        
    # Check if user already exists with this email
    existing_user = get_user_by_email(db, user_info.email)
    is_new_user = False
    
    if existing_user:
        # If user exists with a different provider, update to new provider
        if existing_user.auth_provider != user_info.provider:
            existing_user.auth_provider = user_info.provider
            existing_user.provider_user_id = user_info.provider_user_id
            existing_user.avatar_url = user_info.avatar_url or existing_user.avatar_url
            db.commit()
    else:
        # Create new user
        hashed_password = None  # OAuth users don't need a password
        user_data = {
            "email": user_info.email,
            "username": user_info.username or f"user_{get_random_string(8)}",  # Generate a username if not provided
            "full_name": user_info.full_name,
            "auth_provider": user_info.provider,
            "provider_user_id": user_info.provider_user_id,
            "avatar_url": user_info.avatar_url
        }
        existing_user = create_user(db, user_data, hashed_password)
        is_new_user = True
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24)  # 24 hours
    access_token = create_access_token(
        data={"sub": existing_user.username, "id": existing_user.id, "provider": existing_user.auth_provider},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}, is_new_user
