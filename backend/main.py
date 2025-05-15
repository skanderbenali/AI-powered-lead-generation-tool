from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db, engine
from app.models import Base
from app.schemas import (
    LeadCreate, Lead, LeadSearch,
    UserCreate, User, Token, 
    Project, ProjectCreate,
    EmailTemplate, EmailTemplateCreate,
    EmailCampaign, EmailCampaignCreate
)
from app.routers import leads, auth, projects, emails, ai, analytics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lead Generation API",
    description="API for AI-Powered Lead Generation Tool",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leads.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(emails.router)
app.include_router(ai.router)
app.include_router(analytics.router)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}


@app.get("/api/v1/config", tags=["Config"])
async def get_config():
    """Return client-side configuration"""
    return {
        "scraperEnabled": True,
        "aiEmailFeatureEnabled": True,
        "leadEnrichmentEnabled": True,
        "maxProjectsPerUser": 5,
        "maxLeadsPerProject": 1000,
        "version": "0.1.0"
    }
