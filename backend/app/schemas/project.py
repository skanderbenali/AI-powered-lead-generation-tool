from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_industry: Optional[str] = None
    target_company_size: Optional[str] = None
    target_locations: Optional[str] = None
    target_titles: Optional[str] = None
    search_keywords: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_industry: Optional[str] = None
    target_company_size: Optional[str] = None
    target_locations: Optional[str] = None
    target_titles: Optional[str] = None
    search_keywords: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class Project(ProjectBase):
    id: int
    owner_id: int
    lead_count: int
    email_sent_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ProjectStats(BaseModel):
    total_leads: int
    high_quality_leads: int
    leads_contacted: int
    total_emails_sent: int
    response_rate: float
    latest_leads: List[Any] = []
