from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.schemas.user import AuthProvider


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # Can be null for OAuth users
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # OAuth fields
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.LOCAL)
    provider_user_id = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Relationships
    leads = relationship("Lead", back_populates="owner")
    projects = relationship("Project", back_populates="owner")
    email_campaigns = relationship("EmailCampaign", back_populates="creator")
