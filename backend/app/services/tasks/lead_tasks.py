import logging
import time
import os
import httpx
from typing import List, Dict, Any, Optional
import json
from sqlalchemy.orm import Session

from worker import celery_app
from app.database import SessionLocal
from app.models.lead import Lead
from app.models.project import Project

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ML Service URL
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml-service:8000")


@celery_app.task(name="score_leads")
def score_leads(lead_ids: List[int], project_id: Optional[int] = None):
    """
    Task to score leads using the ML service.
    
    Args:
        lead_ids: List of lead IDs to score
        project_id: Optional project ID for context
    """
    logger.info(f"Starting task to score {len(lead_ids)} leads")
    
    db = SessionLocal()
    try:
        # Get leads
        leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        if not leads:
            logger.error("No leads found with the provided IDs")
            return {"status": "error", "message": "No leads found"}
        
        lead_count = len(leads)
        logger.info(f"Found {lead_count} leads to score")
        
        # In a real implementation, you would call the ML service
        # For demo purposes, we'll simulate the ML scoring
        
        for lead in leads:
            try:
                # Simulate ML scoring
                score, explanation = _simulate_lead_scoring(lead, project_id)
                
                # Update lead with score
                lead.score = score
                
                # Store explanation in enrichment_data
                if not lead.enrichment_data:
                    lead.enrichment_data = {}
                
                lead.enrichment_data['score_explanation'] = explanation
                
                # Commit changes
                db.commit()
                
                logger.info(f"Updated lead {lead.id} with score {score}")
                
            except Exception as e:
                logger.error(f"Error scoring lead {lead.id}: {str(e)}")
        
        logger.info(f"Completed scoring {lead_count} leads")
        return {
            "status": "success",
            "message": f"Scored {lead_count} leads",
            "leads_updated": lead_count
        }
        
    except Exception as e:
        logger.error(f"Error in score_leads task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


@celery_app.task(name="enrich_leads")
def enrich_leads(lead_ids: List[int]):
    """
    Task to enrich leads with additional data.
    
    Args:
        lead_ids: List of lead IDs to enrich
    """
    logger.info(f"Starting task to enrich {len(lead_ids)} leads")
    
    db = SessionLocal()
    try:
        # Get leads
        leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        if not leads:
            logger.error("No leads found with the provided IDs")
            return {"status": "error", "message": "No leads found"}
        
        lead_count = len(leads)
        logger.info(f"Found {lead_count} leads to enrich")
        
        # In a real implementation, you would:
        # 1. Call external APIs for enrichment (Clearbit, LinkedIn, etc.)
        # 2. Update leads with the enriched data
        
        for lead in leads:
            try:
                # Simulate enrichment
                enrichment_data = _simulate_lead_enrichment(lead)
                
                # Update lead with enriched data
                if not lead.enrichment_data:
                    lead.enrichment_data = {}
                
                # Merge new data with existing data
                lead.enrichment_data.update(enrichment_data)
                
                # Update specific fields if available
                if 'email' in enrichment_data and not lead.email:
                    lead.email = enrichment_data['email']
                
                if 'company_size' in enrichment_data and not lead.company_size:
                    lead.company_size = enrichment_data['company_size']
                
                if 'industry' in enrichment_data and not lead.industry:
                    lead.industry = enrichment_data['industry']
                
                # Commit changes
                db.commit()
                
                logger.info(f"Enriched lead {lead.id}")
                
            except Exception as e:
                logger.error(f"Error enriching lead {lead.id}: {str(e)}")
        
        logger.info(f"Completed enriching {lead_count} leads")
        return {
            "status": "success",
            "message": f"Enriched {lead_count} leads",
            "leads_updated": lead_count
        }
        
    except Exception as e:
        logger.error(f"Error in enrich_leads task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


@celery_app.task(name="predict_lead_emails")
def predict_lead_emails(lead_ids: List[int]):
    """
    Task to predict email addresses for leads.
    
    Args:
        lead_ids: List of lead IDs
    """
    logger.info(f"Starting task to predict emails for {len(lead_ids)} leads")
    
    db = SessionLocal()
    try:
        # Get leads
        leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        if not leads:
            logger.error("No leads found with the provided IDs")
            return {"status": "error", "message": "No leads found"}
        
        lead_count = len(leads)
        logger.info(f"Found {lead_count} leads to predict emails for")
        
        # Group leads by company domain to improve prediction
        company_leads = {}
        for lead in leads:
            domain = lead.company_domain
            if not domain and lead.company:
                # Generate domain from company name
                domain = lead.company.lower().replace(' ', '') + '.com'
                lead.company_domain = domain
            
            if domain not in company_leads:
                company_leads[domain] = []
            
            company_leads[domain].append(lead)
        
        # In a real implementation, you would call the ML service
        # For each company, collect known emails to improve predictions
        
        for domain, domain_leads in company_leads.items():
            try:
                # Get known emails for this domain
                known_emails = [l.email for l in domain_leads if l.email]
                
                # For each lead without an email, predict one
                for lead in domain_leads:
                    if lead.email:
                        continue
                    
                    # Predict email
                    prediction = _simulate_email_prediction(
                        lead.first_name,
                        lead.last_name,
                        domain,
                        known_emails
                    )
                    
                    # Update lead with predicted email
                    if prediction:
                        lead.predicted_email = prediction['email']
                        lead.email_confidence = prediction['confidence']
                        
                        # Store prediction details
                        if not lead.enrichment_data:
                            lead.enrichment_data = {}
                        
                        lead.enrichment_data['email_prediction'] = prediction
                        
                        # Commit changes
                        db.commit()
                        
                        logger.info(f"Predicted email for lead {lead.id}: {prediction['email']}")
                
            except Exception as e:
                logger.error(f"Error predicting emails for domain {domain}: {str(e)}")
        
        logger.info(f"Completed predicting emails for {lead_count} leads")
        return {
            "status": "success",
            "message": f"Predicted emails for applicable leads",
            "leads_processed": lead_count
        }
        
    except Exception as e:
        logger.error(f"Error in predict_lead_emails task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


def _simulate_lead_scoring(lead: Lead, project_id: Optional[int] = None) -> tuple:
    """
    Simulate ML-based lead scoring.
    
    In a real implementation, this would call the ML service.
    For demo purposes, we'll use a simple heuristic.
    
    Args:
        lead: Lead to score
        project_id: Optional project ID
        
    Returns:
        Tuple of (score, explanation)
    """
    # Base score
    score = 60
    factors = {}
    
    # Title-based scoring
    title_scores = {
        'ceo': 20,
        'cto': 18,
        'coo': 18,
        'cfo': 16,
        'vp': 15,
        'head': 14,
        'director': 13,
        'manager': 10,
        'lead': 8,
        'senior': 6,
        'engineer': 5,
        'developer': 5,
        'specialist': 4,
        'coordinator': 3,
        'assistant': 2,
    }
    
    if lead.title:
        title_lower = lead.title.lower()
        for title, points in title_scores.items():
            if title in title_lower:
                score += points
                factors['title'] = {
                    'value': lead.title,
                    'importance': 0.3
                }
                break
    
    # Company size scoring
    size_scores = {
        '1-10': 2,
        '11-50': 5,
        '51-200': 10,
        '201-500': 15,
        '501-1000': 18,
        '1001+': 20
    }
    
    if lead.company_size and lead.company_size in size_scores:
        score += size_scores[lead.company_size]
        factors['company_size'] = {
            'value': lead.company_size,
            'importance': 0.25
        }
    
    # Industry scoring - would be more sophisticated in a real implementation
    if lead.industry:
        industry_lower = lead.industry.lower()
        if 'tech' in industry_lower or 'software' in industry_lower:
            score += 10
        elif 'finance' in industry_lower or 'banking' in industry_lower:
            score += 8
        elif 'health' in industry_lower or 'medical' in industry_lower:
            score += 7
        elif 'education' in industry_lower:
            score += 5
        
        factors['industry'] = {
            'value': lead.industry,
            'importance': 0.2
        }
    
    # Contact info scoring
    if lead.email:
        score += 5
        factors['has_email'] = {
            'value': True,
            'importance': 0.15
        }
    
    if lead.linkedin_url:
        score += 5
        factors['has_linkedin'] = {
            'value': True,
            'importance': 0.1
        }
    
    # Clamp score to 0-100
    score = max(0, min(100, score))
    
    # Generate explanation
    reasons = []
    if score >= 80:
        reasons.append("High-value lead based on role and company profile")
    elif score >= 60:
        reasons.append("Good potential lead with moderate fit")
    else:
        reasons.append("Average fit with target criteria")
    
    if 'title' in factors:
        reasons.append(f"Decision-making role: {lead.title}")
    
    if 'company_size' in factors:
        reasons.append(f"Company size ({lead.company_size}) matches target profile")
    
    explanation = {
        'score': score,
        'reasons': reasons,
        'factors': factors
    }
    
    return score, explanation


def _simulate_lead_enrichment(lead: Lead) -> Dict[str, Any]:
    """
    Simulate lead enrichment from external sources.
    
    In a real implementation, this would call external APIs.
    For demo purposes, we'll return mock data.
    
    Args:
        lead: Lead to enrich
        
    Returns:
        Dictionary of enriched data
    """
    # Mock enrichment data
    company_size_map = {
        'small': '11-50',
        'medium': '51-200',
        'large': '201-500',
        'enterprise': '1001+'
    }
    
    industry_options = [
        'Technology', 'Software', 'Financial Services', 'Healthcare',
        'Education', 'Manufacturing', 'Retail', 'Real Estate', 'Media'
    ]
    
    # Generate some mock enrichment data
    enrichment = {}
    
    # Company info
    if lead.company:
        enrichment['company_info'] = {
            'name': lead.company,
            'domain': lead.company_domain or f"{lead.company.lower().replace(' ', '')}.com",
            'founded': 2010 + (hash(lead.company) % 10),
            'location': lead.location or 'San Francisco, CA'
        }
        
        if not lead.company_size:
            sizes = list(company_size_map.values())
            enrichment['company_size'] = sizes[hash(lead.company) % len(sizes)]
        
        if not lead.industry:
            enrichment['industry'] = industry_options[hash(lead.company) % len(industry_options)]
    
    # Contact info
    if not lead.email and lead.first_name and lead.last_name:
        domain = lead.company_domain or f"{lead.company.lower().replace(' ', '')}.com"
        enrichment['email'] = f"{lead.first_name.lower()}.{lead.last_name.lower()}@{domain}"
    
    # Social profiles
    if not lead.linkedin_url and lead.first_name and lead.last_name:
        name_slug = f"{lead.first_name.lower()}-{lead.last_name.lower()}"
        enrichment['linkedin_url'] = f"https://linkedin.com/in/{name_slug}"
    
    if not lead.twitter_url and lead.first_name and lead.last_name:
        name_slug = f"{lead.first_name.lower()}{lead.last_name.lower()}"
        enrichment['twitter_url'] = f"https://twitter.com/{name_slug}"
    
    # Additional profile data
    enrichment['profile_data'] = {
        'education': [
            {
                'school': 'University of California',
                'degree': 'Bachelor of Science',
                'field': 'Computer Science',
                'year': 2010 + (hash(lead.id if lead.id else 0) % 10)
            }
        ],
        'languages': ['English', 'Spanish'],
        'skills': ['Leadership', 'Strategy', 'Management']
    }
    
    return enrichment


def _simulate_email_prediction(
    first_name: str,
    last_name: str,
    domain: str,
    known_emails: List[str]
) -> Dict[str, Any]:
    """
    Simulate email prediction based on name and domain.
    
    In a real implementation, this would call the ML service.
    For demo purposes, we'll use a simple heuristic.
    
    Args:
        first_name: First name
        last_name: Last name
        domain: Company domain
        known_emails: List of known email addresses from the company
        
    Returns:
        Dictionary with predicted email and confidence
    """
    # Clean names
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    first_initial = first[0] if first else ""
    
    # Determine format based on known emails
    if known_emails:
        # Check for patterns in known emails
        dot_count = 0
        first_last_count = 0
        
        for email in known_emails:
            local_part = email.split('@')[0].lower()
            if '.' in local_part:
                dot_count += 1
            
            if first in local_part and last in local_part:
                first_last_count += 1
        
        # Use most common pattern
        if dot_count > len(known_emails) / 2:
            # first.last format seems common
            return {
                'email': f"{first}.{last}@{domain}",
                'format': 'first.last',
                'confidence': 0.8,
                'based_on': f"{len(known_emails)} known company emails"
            }
        elif first_last_count > 0:
            # firstlast format
            return {
                'email': f"{first}{last}@{domain}",
                'format': 'firstlast',
                'confidence': 0.75,
                'based_on': f"{len(known_emails)} known company emails"
            }
    
    # Default to common formats with decreasing confidence
    formats = [
        {'format': 'first.last', 'email': f"{first}.{last}@{domain}", 'confidence': 0.7},
        {'format': 'firstlast', 'email': f"{first}{last}@{domain}", 'confidence': 0.6},
        {'format': 'first_last', 'email': f"{first}_{last}@{domain}", 'confidence': 0.5},
        {'format': 'flast', 'email': f"{first_initial}{last}@{domain}", 'confidence': 0.4},
    ]
    
    return formats[0]
