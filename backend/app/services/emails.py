import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.email_campaign import EmailTemplate, EmailCampaign
from app.models.lead import Lead
from app.schemas.email import (
    EmailTemplateCreate,
    EmailCampaignCreate,
    EmailCampaignUpdate
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Email Template Services
def get_email_templates(
    db: Session,
    creator_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[EmailTemplate]:
    """Get all email templates created by a user"""
    return db.query(EmailTemplate).offset(skip).limit(limit).all()


def get_email_template(db: Session, template_id: int) -> Optional[EmailTemplate]:
    """Get a specific email template by ID"""
    return db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()


def create_email_template(
    db: Session,
    template: EmailTemplateCreate,
    creator_id: int
) -> EmailTemplate:
    """Create a new email template"""
    db_template = EmailTemplate(
        **template.dict()
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


# Email Campaign Services
def get_email_campaigns(
    db: Session,
    creator_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[EmailCampaign]:
    """Get all email campaigns created by a user"""
    return db.query(EmailCampaign).filter(
        EmailCampaign.creator_id == creator_id
    ).offset(skip).limit(limit).all()


def get_email_campaign(db: Session, campaign_id: int) -> Optional[EmailCampaign]:
    """Get a specific email campaign by ID"""
    return db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()


def create_email_campaign(
    db: Session,
    campaign: EmailCampaignCreate,
    creator_id: int
) -> EmailCampaign:
    """Create a new email campaign"""
    campaign_data = campaign.dict()
    lead_ids = campaign_data.pop("lead_ids", [])
    
    # Create campaign
    db_campaign = EmailCampaign(
        **campaign_data,
        creator_id=creator_id
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    # Associate leads with campaign
    if lead_ids:
        leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        db_campaign.leads = leads
        db.commit()
        db.refresh(db_campaign)
    
    return db_campaign


def update_email_campaign(
    db: Session,
    campaign: EmailCampaign,
    campaign_data: EmailCampaignUpdate
) -> EmailCampaign:
    """Update an email campaign"""
    update_data = campaign_data.dict(exclude_unset=True)
    lead_ids = update_data.pop("lead_ids", None)
    
    # Update campaign fields
    for key, value in update_data.items():
        setattr(campaign, key, value)
    
    # Update associated leads if provided
    if lead_ids is not None:
        leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        campaign.leads = leads
    
    db.commit()
    db.refresh(campaign)
    return campaign


def delete_email_campaign(db: Session, campaign_id: int) -> bool:
    """Delete an email campaign"""
    campaign = get_email_campaign(db, campaign_id)
    if not campaign:
        return False
    
    # Remove lead associations
    campaign.leads = []
    
    # Delete campaign
    db.delete(campaign)
    db.commit()
    return True


async def start_email_campaign(db: Session, campaign_id: int) -> bool:
    """
    Start an email campaign - this would trigger actual email sending in production.
    
    For demo purposes, we'll simulate the start by changing status and incrementing counters.
    """
    try:
        logger.info(f"Starting email campaign {campaign_id}")
        
        # Get campaign
        campaign = get_email_campaign(db, campaign_id)
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return False
        
        # Check campaign has leads
        if not campaign.leads:
            logger.error(f"Campaign {campaign_id} has no leads")
            return False
        
        # Update campaign status
        campaign.status = "active"
        
        # Get template
        template = get_email_template(db, campaign.template_id)
        if not template:
            logger.error(f"Template {campaign.template_id} not found")
            return False
        
        # In a real implementation, you would:
        # 1. Queue email sending tasks
        # 2. Log email events
        # 3. Update statistics in real-time
        
        # For demo, just set some example stats
        lead_count = len(campaign.leads)
        
        # Simulate sending emails
        campaign.sent_count = lead_count
        
        # Update project email count
        from app.models.project import Project
        project = db.query(Project).filter(Project.id == campaign.project_id).first()
        if project:
            project.email_sent_count += lead_count
        
        db.commit()
        db.refresh(campaign)
        
        logger.info(f"Campaign {campaign_id} started successfully, sent to {lead_count} leads")
        return True
        
    except Exception as e:
        logger.error(f"Error starting campaign {campaign_id}: {str(e)}")
        return False
