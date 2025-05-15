from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    EmailTemplate, EmailTemplateCreate,
    EmailCampaign, EmailCampaignCreate, EmailCampaignUpdate
)
from app.services.emails import (
    create_email_template,
    get_email_templates,
    get_email_template,
    create_email_campaign,
    get_email_campaigns,
    get_email_campaign,
    update_email_campaign,
    delete_email_campaign,
    start_email_campaign
)
from app.deps.auth import get_current_user

router = APIRouter(prefix="/emails", tags=["Email Campaigns"])


# Email Templates
@router.get("/templates", response_model=List[EmailTemplate])
def read_email_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all email templates created by the current user"""
    return get_email_templates(db, creator_id=current_user.id, skip=skip, limit=limit)


@router.post("/templates", response_model=EmailTemplate)
def create_new_email_template(
    template: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new email template"""
    return create_email_template(db=db, template=template, creator_id=current_user.id)


@router.get("/templates/{template_id}", response_model=EmailTemplate)
def read_email_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific email template by ID"""
    template = get_email_template(db, template_id=template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Email template not found")
    return template


# Email Campaigns
@router.get("/campaigns", response_model=List[EmailCampaign])
def read_email_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all email campaigns created by the current user"""
    return get_email_campaigns(db, creator_id=current_user.id, skip=skip, limit=limit)


@router.post("/campaigns", response_model=EmailCampaign)
def create_new_email_campaign(
    campaign: EmailCampaignCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new email campaign"""
    return create_email_campaign(db=db, campaign=campaign, creator_id=current_user.id)


@router.get("/campaigns/{campaign_id}", response_model=EmailCampaign)
def read_email_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific email campaign by ID"""
    campaign = get_email_campaign(db, campaign_id=campaign_id)
    if campaign is None or campaign.creator_id != current_user.id:
        raise HTTPException(status_code=404, detail="Email campaign not found")
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=EmailCampaign)
def update_existing_campaign(
    campaign_id: int,
    campaign_data: EmailCampaignUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an email campaign"""
    campaign = get_email_campaign(db, campaign_id=campaign_id)
    if campaign is None or campaign.creator_id != current_user.id:
        raise HTTPException(status_code=404, detail="Email campaign not found")
    return update_email_campaign(db=db, campaign=campaign, campaign_data=campaign_data)


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an email campaign"""
    campaign = get_email_campaign(db, campaign_id=campaign_id)
    if campaign is None or campaign.creator_id != current_user.id:
        raise HTTPException(status_code=404, detail="Email campaign not found")
    delete_email_campaign(db=db, campaign_id=campaign_id)
    return None


@router.post("/campaigns/{campaign_id}/start", response_model=EmailCampaign)
def start_existing_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start an email campaign"""
    campaign = get_email_campaign(db, campaign_id=campaign_id)
    if campaign is None or campaign.creator_id != current_user.id:
        raise HTTPException(status_code=404, detail="Email campaign not found")
    
    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Campaign already started or completed")
    
    # Start the campaign asynchronously
    background_tasks.add_task(
        start_email_campaign,
        db=db,
        campaign_id=campaign_id
    )
    
    # Update status to "queued"
    campaign_data = EmailCampaignUpdate(status="queued")
    return update_email_campaign(db=db, campaign=campaign, campaign_data=campaign_data)
