from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.database import get_db
from app.deps.auth import get_current_user
from app.services.analytics import (
    get_user_stats,
    get_lead_source_distribution,
    get_email_campaign_metrics,
    get_lead_quality_metrics
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get aggregated metrics for the dashboard"""
    # User stats
    user_stats = get_user_stats(db, user_id=current_user.id)
    
    # Lead source distribution
    sources = get_lead_source_distribution(db, user_id=current_user.id)
    
    # Email campaign metrics
    campaigns = get_email_campaign_metrics(db, user_id=current_user.id)
    
    # Lead quality
    quality = get_lead_quality_metrics(db, user_id=current_user.id)
    
    return {
        "user_stats": user_stats,
        "lead_sources": sources,
        "campaigns": campaigns,
        "lead_quality": quality
    }


@router.get("/leads/quality", response_model=Dict[str, Any])
async def get_lead_quality_analysis(
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed lead quality analysis"""
    return get_lead_quality_metrics(db, user_id=current_user.id, project_id=project_id)


@router.get("/campaigns/performance", response_model=Dict[str, Any])
async def get_campaign_performance(
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed campaign performance metrics"""
    return get_email_campaign_metrics(db, user_id=current_user.id, project_id=project_id)
