import logging
import time
from typing import List, Dict, Any, Optional
import os
import httpx
from sqlalchemy.orm import Session

from worker import celery_app
from app.database import SessionLocal
from app.models.email_campaign import EmailCampaign, EmailTemplate
from app.models.lead import Lead
from app.models.project import Project

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(name="send_email_campaign")
def send_email_campaign(campaign_id: int):
    """
    Task to send emails for a campaign.
    
    Args:
        campaign_id: Campaign ID
    """
    logger.info(f"Starting task to send email campaign {campaign_id}")
    
    db = SessionLocal()
    try:
        # Get campaign
        campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return {"status": "error", "message": "Campaign not found"}
        
        # Get template
        template = db.query(EmailTemplate).filter(EmailTemplate.id == campaign.template_id).first()
        if not template:
            logger.error(f"Template {campaign.template_id} not found")
            return {"status": "error", "message": "Template not found"}
        
        # Get leads
        leads = campaign.leads
        if not leads:
            logger.error(f"Campaign {campaign_id} has no leads")
            return {"status": "error", "message": "No leads to send to"}
        
        logger.info(f"Sending campaign {campaign_id} to {len(leads)} leads")
        
        # Update campaign status
        campaign.status = "active"
        db.commit()
        
        # Process each lead
        for lead in leads:
            try:
                # In a production environment, this would:
                # 1. Render the email with personalization
                # 2. Send via SMTP or email service API
                # 3. Track the send in a database
                
                # For demo, we'll simulate sending
                _simulate_email_send(campaign, template, lead)
                
                # Update campaign metrics
                campaign.sent_count += 1
                
                # Update project metrics
                project = db.query(Project).filter(Project.id == campaign.project_id).first()
                if project:
                    project.email_sent_count += 1
                
                # Commit changes
                db.commit()
                
                # Small delay to prevent overwhelming any real email service
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error sending email to lead {lead.id}: {str(e)}")
        
        # Mark campaign as completed
        campaign.status = "completed"
        db.commit()
        
        logger.info(f"Completed sending campaign {campaign_id}")
        return {
            "status": "success",
            "message": f"Campaign sent to {campaign.sent_count} leads"
        }
        
    except Exception as e:
        logger.error(f"Error in send_email_campaign task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


@celery_app.task(name="generate_email_template")
def generate_email_template(
    lead_ids: List[int],
    project_id: int,
    user_id: int,
    tone: str = "professional",
    length: str = "medium",
    focus: str = "benefits",
    custom_instructions: Optional[str] = None
):
    """
    Task to generate an email template using AI.
    
    Args:
        lead_ids: List of lead IDs
        project_id: Project ID
        user_id: User ID
        tone: Email tone
        length: Email length
        focus: Email focus
        custom_instructions: Custom instructions
    """
    logger.info(f"Starting task to generate email template for project {project_id}")
    
    db = SessionLocal()
    try:
        # Call the AI service to generate the template
        from app.services.ai import generate_email_template
        
        template = generate_email_template(
            db=db,
            lead_ids=lead_ids,
            project_id=project_id,
            tone=tone,
            length=length,
            focus=focus,
            custom_instructions=custom_instructions,
            user_id=user_id
        )
        
        logger.info(f"Generated email template {template.id}")
        return {
            "status": "success",
            "template_id": template.id,
            "name": template.name,
            "subject": template.subject
        }
        
    except Exception as e:
        logger.error(f"Error in generate_email_template task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


def _simulate_email_send(campaign: EmailCampaign, template: EmailTemplate, lead: Lead) -> None:
    """
    Simulate sending an email to a lead.
    
    This is a placeholder for actual email sending logic.
    In production, this would connect to an email service API.
    """
    # Get lead's email
    email = lead.email
    if not email:
        raise ValueError(f"Lead {lead.id} has no email address")
    
    # Personalize subject and body
    subject = template.subject
    body = template.body
    
    # Replace placeholders
    if lead.first_name:
        body = body.replace("{{first_name}}", lead.first_name)
    
    if lead.last_name:
        body = body.replace("{{last_name}}", lead.last_name)
    
    if lead.company:
        body = body.replace("{{company}}", lead.company)
    
    # Log the simulated send
    logger.info(f"Simulated email send to {email} for campaign {campaign.id}")
    
    # In a real implementation, you would:
    # 1. Connect to SMTP or API-based email service
    # 2. Format the email with HTML templates
    # 3. Include tracking pixels and links
    # 4. Add unsubscribe options
    # 5. Handle bounces and errors
