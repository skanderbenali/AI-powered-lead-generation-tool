import logging
import time
import os
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from worker import celery_app
from app.database import SessionLocal
from app.models.lead import Lead
from app.models.project import Project
from app.models.user import User
from app.schemas.lead import LeadCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scraper service URL
SCRAPER_SERVICE_URL = os.getenv("SCRAPER_SERVICE_URL", "http://scraper:8080")


@celery_app.task(name="scrape_project_data")
def scrape_project_data(project_id: int, user_id: int, max_results: int = 100):
    """
    Task to scrape data for a project using the scraper microservice.
    
    Args:
        project_id: Project ID to scrape for
        user_id: User ID who owns the project
        max_results: Maximum results to scrape
    """
    logger.info(f"Starting task to scrape data for project {project_id}")
    
    db = SessionLocal()
    try:
        # Get project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found")
            return {"status": "error", "message": "Project not found"}
        
        # Verify project belongs to user
        if project.owner_id != user_id:
            logger.error(f"Project {project_id} does not belong to user {user_id}")
            return {"status": "error", "message": "Project does not belong to user"}
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "message": "User not found"}
        
        # Prepare request to scraper service
        params = {
            "project_id": project_id,
            "industry": project.target_industry,
            "title_keywords": project.target_titles.split(",") if project.target_titles else [],
            "location": project.target_locations,
            "company_size": project.target_company_size,
            "max_results": max_results,
            "callback_url": f"{os.getenv('BACKEND_URL', 'http://backend:8000')}/api/scraper/callback"
        }
        
        # Call scraper service
        # In a real implementation, you would:
        # 1. Make an async request to the scraper service
        # 2. The scraper would process the request and call back with results
        # 3. We'd then process those results in the callback endpoint
        
        # For demo, we'll simulate calling the scraper and getting results
        try:
            logger.info(f"Calling scraper service for project {project_id}")
            results = _simulate_scraper_call(params)
            
            # Process results - in production this would happen in the callback
            _process_scraper_results(db, results, project_id, user_id)
            
        except Exception as e:
            logger.error(f"Error calling scraper service: {str(e)}")
            return {"status": "error", "message": f"Scraper service error: {str(e)}"}
        
        # Update project
        project.lead_count = db.query(Lead).filter(Lead.project_id == project_id).count()
        db.commit()
        
        logger.info(f"Completed scraping data for project {project_id}")
        return {
            "status": "success",
            "message": f"Scraped {project.lead_count} leads for project"
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_project_data task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


@celery_app.task(name="import_leads_from_csv")
def import_leads_from_csv(csv_data: str, project_id: int, user_id: int):
    """
    Task to import leads from CSV data.
    
    Args:
        csv_data: CSV data as string
        project_id: Project ID
        user_id: User ID
    """
    logger.info(f"Starting task to import leads from CSV for project {project_id}")
    
    db = SessionLocal()
    try:
        # Get project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found")
            return {"status": "error", "message": "Project not found"}
        
        # Verify project belongs to user
        if project.owner_id != user_id:
            logger.error(f"Project {project_id} does not belong to user {user_id}")
            return {"status": "error", "message": "Project does not belong to user"}
        
        # Parse CSV data
        leads = _parse_csv_data(csv_data)
        
        # Add leads to database
        added_count = 0
        for lead_data in leads:
            try:
                # Create lead
                lead_create = LeadCreate(
                    first_name=lead_data.get("first_name"),
                    last_name=lead_data.get("last_name"),
                    email=lead_data.get("email"),
                    title=lead_data.get("title"),
                    company=lead_data.get("company"),
                    company_domain=lead_data.get("company_domain"),
                    company_size=lead_data.get("company_size"),
                    industry=lead_data.get("industry"),
                    location=lead_data.get("location"),
                    linkedin_url=lead_data.get("linkedin_url"),
                    source="csv_import",
                    project_id=project_id
                )
                
                # Add to database
                from app.services.leads import create_lead
                create_lead(db=db, lead=lead_create, owner_id=user_id)
                
                added_count += 1
                
            except Exception as e:
                logger.error(f"Error adding lead from CSV: {str(e)}")
        
        # Update project lead count
        project.lead_count = db.query(Lead).filter(Lead.project_id == project_id).count()
        db.commit()
        
        logger.info(f"Completed importing {added_count} leads for project {project_id}")
        return {
            "status": "success",
            "message": f"Imported {added_count} leads for project"
        }
        
    except Exception as e:
        logger.error(f"Error in import_leads_from_csv task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


def _simulate_scraper_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate calling the scraper service.
    
    In a real implementation, this would make an HTTP request to the scraper microservice.
    For demo purposes, we return mock data.
    """
    logger.info(f"Simulating scraper call with params: {params}")
    
    # Wait to simulate processing time
    time.sleep(2)
    
    # Generate mock LinkedIn profiles
    profiles = []
    for i in range(5):
        profiles.append({
            "first_name": f"FirstName{i}",
            "last_name": f"LastName{i}",
            "title": "VP of Marketing" if i % 2 == 0 else "Director of Sales",
            "company": f"Company {i+1}",
            "location": "San Francisco, CA" if i % 2 == 0 else "New York, NY",
            "linkedin_url": f"https://linkedin.com/in/firstname{i}lastname{i}",
            "source": "linkedin"
        })
    
    # Generate mock website data
    website_data = []
    for i in range(3):
        website_data.append({
            "company": f"Company {i+1}",
            "domain": f"company{i+1}.com",
            "contacts": [
                {
                    "first_name": f"Contact{j}",
                    "last_name": f"Person{j}",
                    "title": "CEO" if j == 0 else "CTO",
                    "email": f"contact{j}@company{i+1}.com",
                    "source": "website"
                }
                for j in range(2)
            ],
            "emails": [f"contact{j}@company{i+1}.com" for j in range(2)],
            "phone_numbers": [f"555-123-456{j}" for j in range(2)]
        })
    
    return {
        "project_id": params["project_id"],
        "timestamp": time.time(),
        "status": "completed",
        "linkedin_profiles": profiles,
        "website_data": website_data
    }


def _parse_csv_data(csv_data: str) -> List[Dict[str, Any]]:
    """
    Parse CSV data into a list of lead dictionaries.
    
    In a real implementation, this would use the csv module to properly parse the data.
    For demo purposes, we'll return mock data.
    """
    # Mock parsed leads
    leads = []
    for i in range(5):
        leads.append({
            "first_name": f"CSV{i}",
            "last_name": f"User{i}",
            "email": f"csv{i}.user{i}@example.com",
            "title": "Marketing Manager" if i % 2 == 0 else "Sales Executive",
            "company": f"CSV Company {i+1}",
            "company_domain": f"csvcompany{i+1}.com",
            "company_size": "51-200",
            "industry": "Technology",
            "location": "Austin, TX" if i % 2 == 0 else "Chicago, IL",
            "linkedin_url": f"https://linkedin.com/in/csv{i}user{i}"
        })
    
    return leads


def _process_scraper_results(
    db: Session,
    results: Dict[str, Any],
    project_id: int,
    user_id: int
) -> None:
    """
    Process results from the scraper service.
    
    Args:
        db: Database session
        results: Scraper results
        project_id: Project ID
        user_id: User ID
    """
    logger.info(f"Processing scraper results for project {project_id}")
    
    # Process LinkedIn profiles
    linkedin_profiles = results.get("linkedin_profiles", [])
    for profile in linkedin_profiles:
        try:
            # Create lead
            lead_create = LeadCreate(
                first_name=profile.get("first_name"),
                last_name=profile.get("last_name"),
                title=profile.get("title"),
                company=profile.get("company"),
                location=profile.get("location"),
                linkedin_url=profile.get("linkedin_url"),
                source=profile.get("source", "linkedin"),
                project_id=project_id
            )
            
            # Add to database
            from app.services.leads import create_lead
            create_lead(db=db, lead=lead_create, owner_id=user_id)
            
        except Exception as e:
            logger.error(f"Error adding LinkedIn lead: {str(e)}")
    
    # Process website data
    website_data = results.get("website_data", [])
    for website in website_data:
        company = website.get("company")
        domain = website.get("domain")
        
        # Process contacts
        contacts = website.get("contacts", [])
        for contact in contacts:
            try:
                # Create lead
                lead_create = LeadCreate(
                    first_name=contact.get("first_name"),
                    last_name=contact.get("last_name"),
                    email=contact.get("email"),
                    title=contact.get("title"),
                    company=company,
                    company_domain=domain,
                    source=contact.get("source", "website"),
                    project_id=project_id
                )
                
                # Add to database
                from app.services.leads import create_lead
                create_lead(db=db, lead=lead_create, owner_id=user_id)
                
            except Exception as e:
                logger.error(f"Error adding website lead: {str(e)}")
    
    logger.info(f"Completed processing scraper results for project {project_id}")
