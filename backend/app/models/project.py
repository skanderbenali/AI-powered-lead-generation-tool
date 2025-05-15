from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    
    # Project configuration
    target_industry = Column(String)
    target_company_size = Column(String)
    target_locations = Column(String)
    target_titles = Column(String)
    search_keywords = Column(String)
    
    # Additional configuration stored as JSON
    config = Column(JSON, default={})
    
    # Metrics
    lead_count = Column(Integer, default=0)
    email_sent_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    leads = relationship("Lead", back_populates="project")
    email_campaigns = relationship("EmailCampaign", back_populates="project")
