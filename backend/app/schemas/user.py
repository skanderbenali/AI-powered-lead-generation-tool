from pydantic import BaseModel, Field
from app.compat import EmailStr
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    auth_provider: AuthProvider = AuthProvider.LOCAL
    provider_user_id: Optional[str] = None
    avatar_url: Optional[str] = None
    # Profile fields
    bio: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None  # Password is optional for OAuth users


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    auth_provider: Optional[AuthProvider] = None


class OAuthUserInfo(BaseModel):
    provider: AuthProvider
    provider_user_id: str
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile information"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    
    class Config:
        orm_mode = True
