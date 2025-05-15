import os
import logging
import openai
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import asyncio
import httpx
from datetime import datetime

from app.models.lead import Lead
from app.models.project import Project
from app.models.email_campaign import EmailTemplate
from app.schemas.email import EmailTemplateCreate
from app.services.emails import create_email_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")
openai.api_key = OPENAI_API_KEY

# ML Service URL
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml-service:8000")


async def generate_email_template(
    db: Session,
    lead_ids: List[int],
    project_id: int,
    tone: str = "professional",
    length: str = "medium",
    focus: str = "benefits",
    custom_instructions: Optional[str] = None,
    user_id: int = None
) -> EmailTemplate:
    """
    Generate an email template using GPT for specific leads and project.
    
    Args:
        db: Database session
        lead_ids: List of lead IDs to use for email generation
        project_id: Project ID for context
        tone: Email tone (professional, friendly, casual)
        length: Email length (short, medium, long)
        focus: Email focus (benefits, problems, curiosity)
        custom_instructions: Custom instructions for the model
        user_id: ID of the user generating the email
        
    Returns:
        Generated email template
    """
    try:
        logger.info(f"Generating email template for project {project_id} with {len(lead_ids)} leads")
        
        # Get leads data
        leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        if not leads:
            raise ValueError("No leads found with the provided IDs")
            
        # Get project data
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")
            
        # Prepare lead data
        lead_data_list = []
        for lead in leads:
            lead_data = {
                "id": lead.id,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "title": lead.title,
                "company": lead.company,
                "industry": lead.industry
            }
            if lead.linkedin_url:
                lead_data["linkedin_url"] = lead.linkedin_url
                
            lead_data_list.append(lead_data)
            
        # Prepare project data
        project_data = {
            "id": project.id,
            "name": project.name,
            "description": project.description
        }
        
        # Define system prompt
        system_prompt = _create_email_system_prompt(tone, length, focus, project.description)
        
        # Prepare lead context
        lead_context = ""
        for i, lead in enumerate(lead_data_list):
            lead_name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}"
            lead_context += (
                f"Lead {i+1}:\n"
                f"Name: {lead_name}\n"
                f"Title: {lead.get('title', '')}\n"
                f"Company: {lead.get('company', '')}\n"
                f"Industry: {lead.get('industry', '')}\n\n"
            )
        
        # Create user prompt
        user_prompt = (
            f"Generate a personalized outreach email template for the following leads:\n\n"
            f"{lead_context}\n"
            f"Project we're promoting: {project.name}\n\n"
            f"The email should introduce our product/service and request a brief meeting."
        )
        
        if custom_instructions:
            user_prompt += f"\n\nAdditional instructions: {custom_instructions}"
        
        # Make OpenAI API call
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the email content
        email_content = response.choices[0].message.content.strip()
        
        # Parse subject and body
        subject, body = _parse_email_content(email_content)
        
        # Create template name
        template_name = f"AI Generated Template - {project.name} - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Create template in database
        template_data = EmailTemplateCreate(
            name=template_name,
            subject=subject,
            body=body,
            is_ai_generated=True
        )
        
        email_template = create_email_template(db, template_data, user_id)
        
        return email_template
        
    except Exception as e:
        logger.error(f"Error generating email template: {str(e)}")
        raise


def _create_email_system_prompt(
    tone: str,
    length: str,
    focus: str,
    project_description: str
) -> str:
    """Create system prompt based on parameters"""
    
    # Define tone guidelines
    tone_guidelines = {
        "professional": "Use a formal and professional tone. Be respectful and concise.",
        "friendly": "Use a warm and approachable tone. Be personable while maintaining professionalism.",
        "casual": "Use a conversational and relaxed tone. Be casual but still respectful."
    }
    
    # Define length guidelines
    length_guidelines = {
        "short": "Keep the email brief and to the point, around 3-4 sentences.",
        "medium": "Write a moderately sized email with 1-2 short paragraphs.",
        "long": "Create a comprehensive email with 2-3 paragraphs of detail."
    }
    
    # Define focus guidelines
    focus_guidelines = {
        "benefits": "Focus on the specific benefits our solution can provide to the recipient's business.",
        "problems": "Focus on the problems the recipient might be facing and how our solution solves them.",
        "curiosity": "Focus on creating curiosity about our solution without revealing too much detail."
    }
    
    # Create the system prompt
    system_prompt = (
        "You are an expert email copywriter specializing in B2B outreach emails. "
        f"{tone_guidelines.get(tone, tone_guidelines['professional'])} "
        f"{length_guidelines.get(length, length_guidelines['medium'])} "
        f"{focus_guidelines.get(focus, focus_guidelines['benefits'])}\n\n"
        "The email should:\n"
        "1. Have a compelling subject line\n"
        "2. Start with a personalized introduction using {{first_name}}\n"
        "3. Briefly explain who you are\n"
        "4. Present the value proposition clearly\n"
        "5. Include a specific call to action for a meeting\n"
        "6. End with a professional sign-off\n\n"
        f"About our project/product: {project_description}\n\n"
        "Format your response like this:\n"
        "Subject: [Email Subject]\n\n"
        "[Email Body with {{first_name}} placeholder for personalization]"
    )
    
    return system_prompt


def _parse_email_content(content: str) -> tuple:
    """Parse the subject and body from the email content"""
    
    # Check if the content starts with "Subject: "
    if content.startswith("Subject:"):
        # Split by first blank line
        parts = content.split("\n\n", 1)
        
        if len(parts) >= 2:
            subject = parts[0].replace("Subject:", "").strip()
            body = parts[1].strip()
            return subject, body
    
    # Fallback: Try to find "Subject:" anywhere in the content
    subject_index = content.find("Subject:")
    if subject_index >= 0:
        subject_line = content[subject_index:].split("\n", 1)[0]
        subject = subject_line.replace("Subject:", "").strip()
        
        # Body is everything after the subject line
        body_start = content.find(subject) + len(subject)
        body = content[body_start:].strip()
        
        return subject, body
    
    # Fallback: Use first line as subject
    lines = content.split("\n")
    return lines[0], "\n".join(lines[1:]).strip()


async def predict_email(
    first_name: str,
    last_name: str,
    company_domain: str
) -> Dict[str, Any]:
    """
    Predict email address based on name and company domain.
    
    Args:
        first_name: First name
        last_name: Last name
        company_domain: Company domain
        
    Returns:
        Predicted email addresses with confidence scores
    """
    try:
        # In a production environment, this would call the ML service
        # For now, we'll implement a simple prediction logic here
        
        # Define common email formats
        formats = [
            {"format": "first.last", "email": f"{first_name.lower()}.{last_name.lower()}@{company_domain}", "confidence": 0.8},
            {"format": "firstlast", "email": f"{first_name.lower()}{last_name.lower()}@{company_domain}", "confidence": 0.7},
            {"format": "first_last", "email": f"{first_name.lower()}_{last_name.lower()}@{company_domain}", "confidence": 0.6},
            {"format": "flast", "email": f"{first_name[0].lower()}{last_name.lower()}@{company_domain}", "confidence": 0.5},
            {"format": "first", "email": f"{first_name.lower()}@{company_domain}", "confidence": 0.3},
        ]
        
        return {
            "predictions": formats,
            "first_name": first_name,
            "last_name": last_name,
            "company_domain": company_domain
        }
        
    except Exception as e:
        logger.error(f"Error predicting email: {str(e)}")
        return {
            "predictions": [
                {"format": "first.last", "email": f"{first_name.lower()}.{last_name.lower()}@{company_domain}", "confidence": 0.5}
            ],
            "first_name": first_name,
            "last_name": last_name,
            "company_domain": company_domain,
            "error": str(e)
        }
