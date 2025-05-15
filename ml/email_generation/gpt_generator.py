import os
import openai
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")
openai.api_key = OPENAI_API_KEY


class EmailGenerator:
    """Generate personalized emails using OpenAI GPT"""
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the email generator.
        
        Args:
            model: OpenAI model to use
        """
        self.model = model
    
    async def generate_email(
        self,
        lead_data: Dict[str, Any],
        project_data: Dict[str, Any],
        tone: str = "professional",
        length: str = "medium",
        focus: str = "benefits",
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized email for a lead.
        
        Args:
            lead_data: Lead information
            project_data: Project information
            tone: Email tone (professional, friendly, casual)
            length: Email length (short, medium, long)
            focus: Email focus (benefits, problems, curiosity)
            custom_instructions: Custom instructions for the model
            
        Returns:
            Generated email content
        """
        try:
            # Extract lead information
            lead_name = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}"
            lead_title = lead_data.get('title', '')
            lead_company = lead_data.get('company', '')
            lead_industry = lead_data.get('industry', '')
            
            # Extract project information
            project_name = project_data.get('name', '')
            project_description = project_data.get('description', '')
            
            # Prepare the prompt
            system_prompt = self._create_system_prompt(tone, length, focus, project_description)
            
            # Prepare lead context
            lead_context = (
                f"Lead Name: {lead_name}\n"
                f"Lead Title: {lead_title}\n"
                f"Lead Company: {lead_company}\n"
                f"Lead Industry: {lead_industry}\n"
            )
            
            if lead_data.get('linkedin_url'):
                lead_context += f"LinkedIn Profile: {lead_data.get('linkedin_url')}\n"
                
            if custom_instructions:
                lead_context += f"\nCustom Instructions: {custom_instructions}\n"
            
            # Create user prompt
            user_prompt = (
                f"Generate a personalized outreach email to {lead_name} at {lead_company}.\n\n"
                f"Context about the lead:\n{lead_context}\n\n"
                f"Project we're promoting: {project_name}\n"
                f"The email should introduce our product/service and request a brief meeting."
            )
            
            # Make OpenAI API call
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract the email content
            email_content = response.choices[0].message.content.strip()
            
            # Parse subject and body
            subject, body = self._parse_email_content(email_content)
            
            return {
                "subject": subject,
                "body": body,
                "lead_id": lead_data.get('id'),
                "project_id": project_data.get('id'),
                "tone": tone,
                "length": length,
                "focus": focus,
                "is_ai_generated": True
            }
            
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            
            # Fallback to a template email
            return self._generate_fallback_email(lead_data, project_data)
    
    def _create_system_prompt(
        self,
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
            "2. Start with a personalized introduction\n"
            "3. Briefly explain who you are\n"
            "4. Present the value proposition clearly\n"
            "5. Include a specific call to action for a meeting\n"
            "6. End with a professional sign-off\n\n"
            f"About our project/product: {project_description}\n\n"
            "Format your response like this:\n"
            "Subject: [Email Subject]\n\n"
            "[Email Body]"
        )
        
        return system_prompt
    
    def _parse_email_content(self, content: str) -> tuple:
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
    
    def _generate_fallback_email(
        self,
        lead_data: Dict[str, Any],
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a fallback template email"""
        
        lead_name = f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}"
        lead_company = lead_data.get('company', '')
        project_name = project_data.get('name', 'our solution')
        
        subject = f"Quick question about {lead_company}'s lead generation"
        
        body = (
            f"Hi {lead_data.get('first_name', '')},\n\n"
            f"I noticed {lead_company} and wanted to reach out about {project_name}. "
            f"We've been helping companies in the {lead_data.get('industry', 'your industry')} space "
            f"improve their lead generation process.\n\n"
            f"Would you be open to a 15-minute call next week to explore if this might be valuable for your team?\n\n"
            f"Best regards,\n"
            f"[Your Name]\n"
        )
        
        return {
            "subject": subject,
            "body": body,
            "lead_id": lead_data.get('id'),
            "project_id": project_data.get('id'),
            "tone": "professional",
            "length": "medium",
            "focus": "benefits",
            "is_ai_generated": True
        }


async def batch_generate_emails(
    leads: List[Dict[str, Any]],
    project_data: Dict[str, Any],
    tone: str = "professional",
    length: str = "medium",
    focus: str = "benefits",
    custom_instructions: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Generate emails for multiple leads.
    
    Args:
        leads: List of lead data
        project_data: Project information
        tone: Email tone
        length: Email length
        focus: Email focus
        custom_instructions: Custom instructions
        
    Returns:
        List of generated emails
    """
    generator = EmailGenerator()
    
    results = []
    for lead in leads:
        try:
            email = await generator.generate_email(
                lead_data=lead,
                project_data=project_data,
                tone=tone,
                length=length,
                focus=focus,
                custom_instructions=custom_instructions
            )
            results.append(email)
        except Exception as e:
            logger.error(f"Error generating email for lead {lead.get('id')}: {str(e)}")
    
    return results


if __name__ == "__main__":
    import asyncio
    
    async def test_email_generation():
        # Test lead data
        lead = {
            "id": 1,
            "first_name": "John",
            "last_name": "Smith",
            "title": "VP of Marketing",
            "company": "Acme Inc",
            "industry": "Software",
            "linkedin_url": "https://linkedin.com/in/johnsmith"
        }
        
        # Test project data
        project = {
            "id": 1,
            "name": "AI Lead Generation Tool",
            "description": "An AI-powered tool that helps companies find and engage high-quality leads, automate outreach, and close more deals."
        }
        
        # Create email generator
        generator = EmailGenerator()
        
        # Generate email
        email = await generator.generate_email(
            lead_data=lead,
            project_data=project,
            tone="friendly",
            length="medium",
            focus="benefits"
        )
        
        print(f"Subject: {email['subject']}")
        print(f"\nBody:\n{email['body']}")
    
    # Run test
    asyncio.run(test_email_generation())
