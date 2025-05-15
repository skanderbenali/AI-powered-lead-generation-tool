from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.schemas import EmailTemplate, EmailGenerationRequest
from app.services.ai import generate_email_template, predict_email
from app.deps.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Services"])


@router.post("/generate-email", response_model=EmailTemplate)
async def generate_email_content(
    request: EmailGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate an email template using AI based on lead and project data"""
    # This would be an async task, but for demo we'll make it synchronous
    template = await generate_email_template(
        db=db,
        lead_ids=request.lead_ids,
        project_id=request.project_id,
        tone=request.tone,
        length=request.length,
        focus=request.focus,
        custom_instructions=request.custom_instructions,
        user_id=current_user.id
    )
    return template


@router.post("/predict-email", response_model=Dict[str, Any])
async def predict_lead_email(
    first_name: str,
    last_name: str,
    company_domain: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Predict an email address based on name and company domain"""
    result = await predict_email(
        first_name=first_name,
        last_name=last_name,
        company_domain=company_domain
    )
    return result


@router.post("/score-leads", response_model=Dict[str, Any])
async def score_leads_for_project(
    project_id: int,
    lead_ids: List[int] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Score leads for a project using ML models"""
    # This would be implemented with a real ML model
    # For now, return a dummy response
    return {
        "status": "processing",
        "message": "Lead scoring initiated",
        "task_id": "dummy-task-id-12345"
    }
