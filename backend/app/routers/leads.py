from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import Lead, LeadCreate, LeadUpdate, LeadSearch
from app.services.leads import (
    get_leads, 
    get_lead, 
    create_lead, 
    update_lead, 
    delete_lead,
    search_leads
)
from app.deps.auth import get_current_user

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.get("/", response_model=List[Lead])
def read_leads(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all leads owned by the current user"""
    leads = get_leads(db, owner_id=current_user.id, skip=skip, limit=limit)
    return leads


@router.post("/", response_model=Lead)
def create_new_lead(
    lead: LeadCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new lead"""
    return create_lead(db=db, lead=lead, owner_id=current_user.id)


@router.get("/{lead_id}", response_model=Lead)
def read_lead(
    lead_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific lead by ID"""
    lead = get_lead(db, lead_id=lead_id)
    if lead is None or lead.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=Lead)
def update_existing_lead(
    lead_id: int, 
    lead_data: LeadUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a lead"""
    lead = get_lead(db, lead_id=lead_id)
    if lead is None or lead.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Lead not found")
    return update_lead(db=db, lead=lead, lead_data=lead_data)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_lead(
    lead_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a lead"""
    lead = get_lead(db, lead_id=lead_id)
    if lead is None or lead.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Lead not found")
    delete_lead(db=db, lead_id=lead_id)
    return None


@router.post("/search", response_model=List[Lead])
def search_for_leads(
    search_criteria: LeadSearch,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search for leads based on criteria"""
    leads = search_leads(db=db, search_criteria=search_criteria, owner_id=current_user.id)
    return leads


@router.post("/{lead_id}/enrich", response_model=Lead)
def enrich_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Enrich a lead with additional data from external sources"""
    lead = get_lead(db, lead_id=lead_id)
    if lead is None or lead.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # TODO: Implement lead enrichment service
    # This would be a call to an async task that fetches additional data
    # For now, just return the lead as is
    return lead
