from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime


class LeadBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    company: Optional[str] = None
    company_domain: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    website_url: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None


class LeadCreate(LeadBase):
    project_id: int


class LeadUpdate(LeadBase):
    status: Optional[str] = None
    score: Optional[float] = None
    enrichment_data: Optional[Dict[str, Any]] = None


class LeadSearch(BaseModel):
    industry: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    keywords: Optional[str] = None
    project_id: Optional[int] = None
    min_score: Optional[float] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0


class Lead(LeadBase):
    id: int
    status: str
    score: float
    project_id: int
    owner_id: int
    enrichment_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class LeadWithScore(Lead):
    score_explanation: Optional[Dict[str, Any]] = None
