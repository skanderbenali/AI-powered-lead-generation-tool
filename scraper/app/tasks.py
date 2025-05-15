import asyncio
import logging
import httpx
from typing import Dict, Any, Optional, List
import json
import time

from app.linkedin import scrape_linkedin_profiles
from app.website import scrape_website_contact_data, predict_email_format

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scrape_leads_task(
    task_id: str,
    source: str,
    params: Dict[str, Any],
    callback_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a scraping task and send results back to main application.
    
    Args:
        task_id: Unique identifier for this task
        source: Source to scrape ("linkedin" or "website")
        params: Parameters for the scraping task
        callback_url: URL to send results back to
        
    Returns:
        Task results
    """
    logger.info(f"Starting scrape task {task_id} from source {source}")
    
    results = {
        "task_id": task_id,
        "source": source,
        "timestamp": time.time(),
        "status": "completed",
        "data": None,
        "error": None
    }
    
    try:
        if source == "linkedin":
            profiles = await scrape_linkedin_profiles(
                search_url=params.get("search_url"),
                max_results=params.get("max_results", 100)
            )
            results["data"] = {"profiles": profiles}
            
        elif source == "website":
            website_data = await scrape_website_contact_data(
                domain=params.get("domain"),
                company_name=params.get("company_name")
            )
            results["data"] = website_data
            
        else:
            results["status"] = "failed"
            results["error"] = f"Unknown source: {source}"
            
    except Exception as e:
        logger.error(f"Error in scrape task {task_id}: {str(e)}")
        results["status"] = "failed"
        results["error"] = str(e)
        
    # Send results to callback URL if provided
    if callback_url and results["status"] == "completed":
        await send_results_to_callback(callback_url, results)
        
    return results


async def scrape_project_task(
    project_id: int,
    params: Dict[str, Any],
    callback_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a comprehensive scraping task for a project.
    
    Args:
        project_id: Project ID to scrape for
        params: Parameters for the scraping task
        callback_url: URL to send results back to
        
    Returns:
        Task results
    """
    logger.info(f"Starting comprehensive scrape for project {project_id}")
    
    # This would be implemented with more sophisticated logic in production
    # For demo, we'll create a basic implementation
    
    # Get project configuration
    industry = params.get("industry", "")
    title_keywords = params.get("title_keywords", [])
    location = params.get("location", "")
    company_size = params.get("company_size", "")
    max_results = params.get("max_results", 100)
    
    # Build LinkedIn search URL (this is a simplified version)
    search_url = "https://www.linkedin.com/search/results/people/?"
    search_params = []
    
    if industry:
        search_params.append(f"industry={industry}")
    if title_keywords:
        search_params.append(f"title={','.join(title_keywords)}")
    if location:
        search_params.append(f"location={location}")
    
    if search_params:
        search_url += "&".join(search_params)
    
    # Start LinkedIn scraping
    linkedin_results = await scrape_linkedin_profiles(
        search_url=search_url,
        max_results=max_results
    )
    
    # Process company domains from LinkedIn results
    company_domains = {}
    for profile in linkedin_results:
        company = profile.get("company", "")
        if company and company not in company_domains:
            # In a real implementation, you would have logic to convert company names to domains
            # For demo, we'll create dummy domains
            domain = company.lower().replace(" ", "") + ".com"
            company_domains[company] = domain
    
    # Scrape websites for each company
    website_results = []
    for company, domain in company_domains.items():
        try:
            website_data = await scrape_website_contact_data(
                domain=domain,
                company_name=company
            )
            website_results.append(website_data)
        except Exception as e:
            logger.error(f"Error scraping website for {company}: {str(e)}")
    
    # Combine results
    combined_results = {
        "linkedin_profiles": linkedin_results,
        "website_data": website_results,
        "project_id": project_id,
        "timestamp": time.time(),
        "status": "completed"
    }
    
    # Send results to callback URL if provided
    if callback_url:
        await send_results_to_callback(callback_url, combined_results)
    
    return combined_results


async def send_results_to_callback(
    callback_url: str,
    results: Dict[str, Any]
) -> None:
    """Send results to a callback URL"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                callback_url,
                json=results,
                timeout=30
            )
            if response.status_code != 200:
                logger.error(f"Error sending results to callback URL: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"Error sending results to callback URL: {str(e)}")


async def predict_email(
    first_name: str,
    last_name: str,
    company_domain: str,
    known_emails: List[str] = None
) -> Dict[str, Any]:
    """
    Predict most likely email address for a person.
    
    Args:
        first_name: First name
        last_name: Last name
        company_domain: Company domain
        known_emails: List of known email addresses from the company
        
    Returns:
        Predicted email addresses with confidence scores
    """
    if not known_emails:
        known_emails = []
    
    # Predict format based on known emails
    format_prediction = await predict_email_format(company_domain, known_emails)
    
    primary_format = format_prediction["primary_format"]
    formats = format_prediction["formats"]
    confidence = format_prediction["confidence"]
    
    # Clean names
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    first_initial = first[0] if first else ""
    last_initial = last[0] if last else ""
    
    # Generate predictions
    predictions = []
    
    # Email format templates
    email_templates = {
        "first.last": f"{first}.{last}@{company_domain}",
        "firstlast": f"{first}{last}@{company_domain}",
        "first_last": f"{first}_{last}@{company_domain}",
        "flast": f"{first_initial}{last}@{company_domain}",
        "first": f"{first}@{company_domain}",
        "first.last.initial": f"{first}.{last}.{first_initial}@{company_domain}"
    }
    
    # Add predictions based on formats
    base_confidence = confidence
    for i, format_name in enumerate(formats):
        if format_name in email_templates:
            email = email_templates[format_name]
            format_confidence = base_confidence * (1 - (i * 0.1))  # Decrease confidence for less likely formats
            
            predictions.append({
                "email": email,
                "format": format_name,
                "confidence": round(format_confidence, 2)
            })
    
    # If no predictions were made, use default formats
    if not predictions:
        predictions = [
            {"email": email_templates["first.last"], "format": "first.last", "confidence": 0.5},
            {"email": email_templates["firstlast"], "format": "firstlast", "confidence": 0.3}
        ]
    
    return {
        "predictions": predictions,
        "first_name": first_name,
        "last_name": last_name,
        "company_domain": company_domain
    }
