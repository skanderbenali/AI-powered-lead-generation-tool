from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Dict, Any, Optional

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate, LeadSearch


def get_leads(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Lead]:
    """Get all leads for a user"""
    return db.query(Lead).filter(Lead.owner_id == owner_id).offset(skip).limit(limit).all()


def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    """Get a lead by ID"""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def create_lead(db: Session, lead: LeadCreate, owner_id: int) -> Lead:
    """Create a new lead"""
    db_lead = Lead(
        **lead.dict(),
        owner_id=owner_id
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    
    # Update lead count in project
    if db_lead.project_id:
        update_project_lead_count(db, db_lead.project_id)
        
    return db_lead


def update_lead(db: Session, lead: Lead, lead_data: LeadUpdate) -> Lead:
    """Update a lead"""
    update_data = lead_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(lead, key, value)
        
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int) -> bool:
    """Delete a lead"""
    lead = get_lead(db, lead_id)
    if not lead:
        return False
        
    project_id = lead.project_id
    
    db.delete(lead)
    db.commit()
    
    # Update lead count in project
    if project_id:
        update_project_lead_count(db, project_id)
        
    return True


def update_project_lead_count(db: Session, project_id: int) -> None:
    """Update the lead count for a project"""
    from app.models.project import Project
    
    lead_count = db.query(func.count(Lead.id)).filter(
        Lead.project_id == project_id
    ).scalar()
    
    db.query(Project).filter(Project.id == project_id).update(
        {"lead_count": lead_count}
    )
    db.commit()


def search_leads(db: Session, search_criteria: LeadSearch, owner_id: int) -> List[Lead]:
    """Search for leads based on criteria"""
    query = db.query(Lead).filter(Lead.owner_id == owner_id)
    
    # Apply filters
    if search_criteria.project_id:
        query = query.filter(Lead.project_id == search_criteria.project_id)
        
    if search_criteria.industry:
        query = query.filter(Lead.industry.ilike(f"%{search_criteria.industry}%"))
        
    if search_criteria.title:
        query = query.filter(Lead.title.ilike(f"%{search_criteria.title}%"))
        
    if search_criteria.location:
        query = query.filter(Lead.location.ilike(f"%{search_criteria.location}%"))
        
    if search_criteria.company_size:
        query = query.filter(Lead.company_size == search_criteria.company_size)
        
    if search_criteria.min_score is not None:
        query = query.filter(Lead.score >= search_criteria.min_score)
        
    if search_criteria.status:
        query = query.filter(Lead.status == search_criteria.status)
        
    if search_criteria.keywords:
        keywords = search_criteria.keywords.split()
        keyword_filters = []
        
        for keyword in keywords:
            keyword_filter = or_(
                Lead.first_name.ilike(f"%{keyword}%"),
                Lead.last_name.ilike(f"%{keyword}%"),
                Lead.company.ilike(f"%{keyword}%"),
                Lead.title.ilike(f"%{keyword}%"),
                Lead.notes.ilike(f"%{keyword}%") if Lead.notes else False
            )
            keyword_filters.append(keyword_filter)
            
        if keyword_filters:
            query = query.filter(and_(*keyword_filters))
    
    # Apply pagination
    return query.offset(search_criteria.offset).limit(search_criteria.limit).all()
