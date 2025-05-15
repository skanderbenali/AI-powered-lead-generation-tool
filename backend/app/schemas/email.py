from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    body: str
    is_ai_generated: bool = False


class EmailTemplateCreate(EmailTemplateBase):
    pass


class EmailTemplate(EmailTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class EmailCampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "draft"
    from_email: EmailStr
    reply_to: Optional[EmailStr] = None
    scheduled_at: Optional[datetime] = None


class EmailCampaignCreate(EmailCampaignBase):
    template_id: int
    project_id: int
    lead_ids: List[int] = []


class EmailCampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    from_email: Optional[EmailStr] = None
    reply_to: Optional[EmailStr] = None
    scheduled_at: Optional[datetime] = None
    template_id: Optional[int] = None
    lead_ids: Optional[List[int]] = None


class EmailCampaign(EmailCampaignBase):
    id: int
    template_id: int
    project_id: int
    creator_id: int
    sent_count: int
    open_count: int
    click_count: int
    reply_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class EmailGenerationRequest(BaseModel):
    lead_ids: List[int]
    project_id: int
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"
    focus: Optional[str] = "benefits"
    custom_instructions: Optional[str] = None
