from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


# Junction table for many-to-many relationship between campaigns and leads
campaign_leads = Table(
    "campaign_leads",
    Base.metadata,
    Column("campaign_id", Integer, ForeignKey("email_campaigns.id"), primary_key=True),
    Column("lead_id", Integer, ForeignKey("leads.id"), primary_key=True),
)


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaigns = relationship("EmailCampaign", back_populates="template")


class EmailCampaign(Base):
    __tablename__ = "email_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="draft")  # draft, active, paused, completed, etc.
    
    # Email configuration
    template_id = Column(Integer, ForeignKey("email_templates.id"))
    from_email = Column(String)
    reply_to = Column(String)
    
    # Campaign metrics
    sent_count = Column(Integer, default=0)
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    # Timestamps
    scheduled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    template = relationship("EmailTemplate", back_populates="campaigns")
    project = relationship("Project", back_populates="email_campaigns")
    creator = relationship("User", back_populates="email_campaigns")
    leads = relationship("Lead", secondary=campaign_leads, back_populates="campaigns")
