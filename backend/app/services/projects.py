from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from sqlalchemy import func

from app.models.project import Project
from app.models.lead import Lead
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStats


def get_projects(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
    """Get all projects for a user"""
    return db.query(Project).filter(Project.owner_id == owner_id).offset(skip).limit(limit).all()


def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get a project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()


def create_project(db: Session, project: ProjectCreate, owner_id: int) -> Project:
    """Create a new project"""
    db_project = Project(
        **project.dict(),
        owner_id=owner_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project: Project, project_data: ProjectUpdate) -> Project:
    """Update a project"""
    update_data = project_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(project, key, value)
        
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    """Delete a project"""
    project = get_project(db, project_id)
    if not project:
        return False
        
    db.delete(project)
    db.commit()
    return True


def get_project_stats(db: Session, project_id: int) -> ProjectStats:
    """Get statistics for a project"""
    # Get total leads count
    total_leads = db.query(func.count(Lead.id)).filter(
        Lead.project_id == project_id
    ).scalar()
    
    # Get high quality leads count
    high_quality_leads = db.query(func.count(Lead.id)).filter(
        Lead.project_id == project_id,
        Lead.score >= 80
    ).scalar()
    
    # Get contacted leads count
    leads_contacted = db.query(func.count(Lead.id)).filter(
        Lead.project_id == project_id,
        Lead.status.in_(["contacted", "responded", "qualified", "customer"])
    ).scalar()
    
    # Get email metrics
    from app.models.email_campaign import EmailCampaign
    
    email_campaigns = db.query(EmailCampaign).filter(
        EmailCampaign.project_id == project_id
    ).all()
    
    total_emails_sent = sum(campaign.sent_count for campaign in email_campaigns)
    total_replies = sum(campaign.reply_count for campaign in email_campaigns)
    
    response_rate = 0
    if total_emails_sent > 0:
        response_rate = (total_replies / total_emails_sent) * 100
    
    # Get latest leads
    latest_leads = db.query(Lead).filter(
        Lead.project_id == project_id
    ).order_by(Lead.created_at.desc()).limit(5).all()
    
    return ProjectStats(
        total_leads=total_leads,
        high_quality_leads=high_quality_leads,
        leads_contacted=leads_contacted,
        total_emails_sent=total_emails_sent,
        response_rate=response_rate,
        latest_leads=latest_leads
    )
