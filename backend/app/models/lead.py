from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    company_domain = Column(String)
    company_size = Column(String)
    industry = Column(String)
    location = Column(String)
    
    # Contact information
    phone = Column(String)
    linkedin_url = Column(String)
    twitter_url = Column(String)
    website_url = Column(String)
    
    # Enrichment data - stored as JSON for flexibility
    enrichment_data = Column(JSON)
    
    # Lead quality and tracking
    score = Column(Float, default=0.0)  # ML-generated lead score
    status = Column(String, default="new")  # new, contacted, qualified, customer, etc.
    source = Column(String)  # where this lead came from
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Relationships
    owner = relationship("User", back_populates="leads")
    project = relationship("Project", back_populates="leads")
    campaigns = relationship("EmailCampaign", secondary="campaign_leads", back_populates="leads")
