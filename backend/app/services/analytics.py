import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.models.lead import Lead
from app.models.project import Project
from app.models.email_campaign import EmailCampaign, EmailTemplate
from app.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Get aggregated stats for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with user stats
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {}
    
    # Get lead counts
    total_leads = db.query(func.count(Lead.id)).filter(
        Lead.owner_id == user_id
    ).scalar()
    
    # Get project count
    project_count = db.query(func.count(Project.id)).filter(
        Project.owner_id == user_id
    ).scalar()
    
    # Get high quality leads (score >= 80)
    high_quality_leads = db.query(func.count(Lead.id)).filter(
        Lead.owner_id == user_id,
        Lead.score >= 80
    ).scalar()
    
    # Get contacted leads
    contacted_leads = db.query(func.count(Lead.id)).filter(
        Lead.owner_id == user_id,
        Lead.status.in_(["contacted", "responded", "qualified", "customer"])
    ).scalar()
    
    # Get email campaign metrics
    email_campaigns = db.query(EmailCampaign).filter(
        EmailCampaign.creator_id == user_id
    ).all()
    
    total_campaigns = len(email_campaigns)
    total_emails_sent = sum(campaign.sent_count for campaign in email_campaigns)
    total_opens = sum(campaign.open_count for campaign in email_campaigns)
    total_clicks = sum(campaign.click_count for campaign in email_campaigns)
    total_replies = sum(campaign.reply_count for campaign in email_campaigns)
    
    # Calculate rates
    open_rate = (total_opens / total_emails_sent * 100) if total_emails_sent > 0 else 0
    click_rate = (total_clicks / total_opens * 100) if total_opens > 0 else 0
    reply_rate = (total_replies / total_emails_sent * 100) if total_emails_sent > 0 else 0
    
    # Get recent activity - last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    new_leads_week = db.query(func.count(Lead.id)).filter(
        Lead.owner_id == user_id,
        Lead.created_at >= seven_days_ago
    ).scalar()
    
    emails_sent_week = db.query(func.sum(EmailCampaign.sent_count)).filter(
        EmailCampaign.creator_id == user_id,
        EmailCampaign.updated_at >= seven_days_ago,
        EmailCampaign.status.in_(["active", "completed"])
    ).scalar() or 0
    
    return {
        "total_leads": total_leads,
        "project_count": project_count,
        "high_quality_leads": high_quality_leads,
        "contacted_leads": contacted_leads,
        "lead_quality_ratio": (high_quality_leads / total_leads * 100) if total_leads > 0 else 0,
        "contact_ratio": (contacted_leads / total_leads * 100) if total_leads > 0 else 0,
        "email_campaigns": {
            "total": total_campaigns,
            "emails_sent": total_emails_sent,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "reply_rate": reply_rate
        },
        "recent_activity": {
            "new_leads_week": new_leads_week,
            "emails_sent_week": emails_sent_week
        }
    }


def get_lead_source_distribution(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Get lead distribution by source.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of lead sources with counts and percentages
    """
    # Get total leads
    total_leads = db.query(func.count(Lead.id)).filter(
        Lead.owner_id == user_id
    ).scalar()
    
    if total_leads == 0:
        return []
    
    # Get lead counts by source
    source_counts = db.query(
        Lead.source,
        func.count(Lead.id).label("count")
    ).filter(
        Lead.owner_id == user_id
    ).group_by(
        Lead.source
    ).all()
    
    # Format results
    results = []
    for source, count in source_counts:
        source_name = source if source else "unknown"
        percentage = (count / total_leads) * 100
        
        results.append({
            "source": source_name,
            "count": count,
            "percentage": round(percentage, 1)
        })
    
    # Sort by count
    results.sort(key=lambda x: x["count"], reverse=True)
    
    return results


def get_email_campaign_metrics(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get email campaign metrics.
    
    Args:
        db: Database session
        user_id: User ID
        project_id: Optional project ID to filter by
        
    Returns:
        Dictionary with email campaign metrics
    """
    # Base query
    query = db.query(EmailCampaign).filter(EmailCampaign.creator_id == user_id)
    
    # Filter by project if specified
    if project_id:
        query = query.filter(EmailCampaign.project_id == project_id)
    
    campaigns = query.all()
    
    if not campaigns:
        return {
            "total_campaigns": 0,
            "total_sent": 0,
            "metrics": {},
            "campaigns": []
        }
    
    # Calculate metrics
    total_sent = sum(c.sent_count for c in campaigns)
    total_opened = sum(c.open_count for c in campaigns)
    total_clicked = sum(c.click_count for c in campaigns)
    total_replied = sum(c.reply_count for c in campaigns)
    
    # Calculate rates
    open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
    click_rate = (total_clicked / total_sent * 100) if total_sent > 0 else 0
    reply_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0
    
    # Get campaign details
    campaign_details = []
    for campaign in campaigns:
        # Get template
        template = db.query(EmailTemplate).filter(
            EmailTemplate.id == campaign.template_id
        ).first()
        
        # Calculate campaign-specific rates
        campaign_open_rate = (campaign.open_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0
        campaign_click_rate = (campaign.click_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0
        campaign_reply_rate = (campaign.reply_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0
        
        campaign_details.append({
            "id": campaign.id,
            "name": campaign.name,
            "status": campaign.status,
            "sent": campaign.sent_count,
            "opened": campaign.open_count,
            "clicked": campaign.click_count,
            "replied": campaign.reply_count,
            "open_rate": campaign_open_rate,
            "click_rate": campaign_click_rate,
            "reply_rate": campaign_reply_rate,
            "template_name": template.name if template else None,
            "is_ai_generated": template.is_ai_generated if template else False,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None
        })
    
    return {
        "total_campaigns": len(campaigns),
        "total_sent": total_sent,
        "metrics": {
            "open_rate": round(open_rate, 1),
            "click_rate": round(click_rate, 1),
            "reply_rate": round(reply_rate, 1),
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "total_replied": total_replied
        },
        "campaigns": campaign_details
    }


def get_lead_quality_metrics(
    db: Session,
    user_id: int,
    project_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get lead quality metrics.
    
    Args:
        db: Database session
        user_id: User ID
        project_id: Optional project ID to filter by
        
    Returns:
        Dictionary with lead quality metrics
    """
    # Base query
    query = db.query(Lead).filter(Lead.owner_id == user_id)
    
    # Filter by project if specified
    if project_id:
        query = query.filter(Lead.project_id == project_id)
    
    # Get total leads
    total_leads = query.count()
    
    if total_leads == 0:
        return {
            "total_leads": 0,
            "score_distribution": [],
            "status_distribution": []
        }
    
    # Get score distribution
    score_ranges = [
        {"min": 0, "max": 50, "label": "Low Quality"},
        {"min": 50, "max": 70, "label": "Average Quality"},
        {"min": 70, "max": 85, "label": "Good Quality"},
        {"min": 85, "max": 100, "label": "High Quality"}
    ]
    
    score_distribution = []
    for score_range in score_ranges:
        count = query.filter(
            Lead.score >= score_range["min"],
            Lead.score < score_range["max"]
        ).count()
        
        percentage = (count / total_leads) * 100
        
        score_distribution.append({
            "label": score_range["label"],
            "min": score_range["min"],
            "max": score_range["max"],
            "count": count,
            "percentage": round(percentage, 1)
        })
    
    # Get status distribution
    status_counts = db.query(
        Lead.status,
        func.count(Lead.id).label("count")
    ).filter(
        Lead.owner_id == user_id
    )
    
    if project_id:
        status_counts = status_counts.filter(Lead.project_id == project_id)
    
    status_counts = status_counts.group_by(Lead.status).all()
    
    status_distribution = []
    for status, count in status_counts:
        status_name = status if status else "unknown"
        percentage = (count / total_leads) * 100
        
        status_distribution.append({
            "status": status_name,
            "count": count,
            "percentage": round(percentage, 1)
        })
    
    # Sort by count
    status_distribution.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "total_leads": total_leads,
        "score_distribution": score_distribution,
        "status_distribution": status_distribution
    }
