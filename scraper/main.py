from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
import os
import httpx
from dotenv import load_dotenv

from app.linkedin import scrape_linkedin_profiles
from app.website import scrape_website_contact_data
from app.tasks import scrape_leads_task
from app.celery_worker import create_celery

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Lead Generation Scraper Service",
    description="Microservice for scraping lead data from LinkedIn and company websites",
    version="0.1.0"
)

# Initialize Celery
celery = create_celery()
app.celery = celery

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_KEY = os.getenv("API_KEY", "dummy-api-key")


# Models
class ScrapeLinkedInRequest(BaseModel):
    search_url: HttpUrl
    max_results: int = 100
    project_id: int
    callback_url: Optional[HttpUrl] = None


class ScrapeWebsiteRequest(BaseModel):
    domain: str
    project_id: int
    company_name: Optional[str] = None
    callback_url: Optional[HttpUrl] = None


class ScrapeProjectRequest(BaseModel):
    project_id: int
    industry: Optional[str] = None
    title_keywords: List[str] = []
    location: Optional[str] = None
    company_size: Optional[str] = None
    max_results: int = 100
    callback_url: Optional[HttpUrl] = None


# API Routes
@app.get("/")
async def root():
    return {"status": "ok", "message": "Scraper service is running"}


@app.post("/linkedin/scrape")
async def scrape_linkedin(
    request: ScrapeLinkedInRequest, 
    background_tasks: BackgroundTasks
):
    """Scrape LinkedIn profiles based on a search URL"""
    task_id = f"linkedin_scrape_{request.project_id}_{id(request)}"
    
    # Add scraping task to background
    background_tasks.add_task(
        scrape_leads_task,
        task_id=task_id,
        source="linkedin",
        params=request.dict(),
        callback_url=request.callback_url
    )
    
    return {
        "status": "processing",
        "task_id": task_id,
        "message": f"Started scraping LinkedIn profiles for project {request.project_id}"
    }


@app.post("/website/scrape")
async def scrape_website(
    request: ScrapeWebsiteRequest,
    background_tasks: BackgroundTasks
):
    """Scrape contact information from a company website"""
    task_id = f"website_scrape_{request.project_id}_{id(request)}"
    
    # Add scraping task to background
    background_tasks.add_task(
        scrape_leads_task,
        task_id=task_id,
        source="website",
        params=request.dict(),
        callback_url=request.callback_url
    )
    
    return {
        "status": "processing",
        "task_id": task_id,
        "message": f"Started scraping website {request.domain} for project {request.project_id}"
    }


@app.post("/project/scrape")
async def scrape_project(
    request: ScrapeProjectRequest,
    background_tasks: BackgroundTasks
):
    """Start a comprehensive scrape for a project based on its criteria"""
    task_id = f"project_scrape_{request.project_id}"
    
    # Add project scraping task to Celery queue
    celery.send_task(
        "app.tasks.scrape_project_task",
        kwargs={
            "project_id": request.project_id,
            "params": request.dict(),
            "callback_url": request.callback_url
        },
        task_id=task_id
    )
    
    return {
        "status": "processing",
        "task_id": task_id,
        "message": f"Started comprehensive scraping for project {request.project_id}"
    }


@app.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get the status of a scraping task"""
    # Get task result from Celery
    task_result = celery.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }


# Add routes for other scraping services as needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
