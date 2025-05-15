import re
import logging
from typing import List, Dict, Any, Tuple
import pandas as pd
import requests
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailPredictor:
    """Predict email addresses for leads based on patterns and validation"""
    
    def __init__(self):
        """Initialize email predictor"""
        self.email_formats = {
            "first.last": lambda f, l: f"{f}.{l}",
            "firstlast": lambda f, l: f"{f}{l}",
            "first_last": lambda f, l: f"{f}_{l}",
            "flast": lambda f, l: f"{f[0]}{l}",
            "first": lambda f, l: f"{f}",
            "first.l": lambda f, l: f"{f}.{l[0]}",
            "f.last": lambda f, l: f"{f[0]}.{l}",
            "lastfirst": lambda f, l: f"{l}{f}",
        }
    
    def analyze_company_emails(self, emails: List[str]) -> Dict[str, Any]:
        """
        Analyze existing emails to identify common patterns within a company.
        
        Args:
            emails: List of known email addresses
            
        Returns:
            Dictionary with email pattern analysis
        """
        if not emails:
            return {
                "primary_format": "first.last",
                "formats": ["first.last", "firstlast"],
                "confidence": 0.3,
                "sample_size": 0
            }
        
        # Extract domain from first email
        domain_match = re.search(r'@([\w.-]+)', emails[0])
        if not domain_match:
            return {
                "primary_format": "first.last",
                "formats": ["first.last", "firstlast"],
                "confidence": 0.3,
                "sample_size": 0
            }
        
        domain = domain_match.group(1)
        
        # Filter emails with the same domain
        domain_emails = [email for email in emails if email.endswith(f"@{domain}")]
        
        # Count formats
        format_counts = {}
        
        for email in domain_emails:
            # Extract local part (before @)
            local_part = email.split('@')[0].lower()
            
            # Try to identify format
            if '.' in local_part:
                parts = local_part.split('.')
                if len(parts) == 2:
                    if len(parts[0]) == 1 and len(parts[1]) > 1:
                        format_counts["f.last"] = format_counts.get("f.last", 0) + 1
                    elif len(parts[0]) > 1 and len(parts[1]) == 1:
                        format_counts["first.l"] = format_counts.get("first.l", 0) + 1
                    else:
                        format_counts["first.last"] = format_counts.get("first.last", 0) + 1
                else:
                    format_counts["first.last"] = format_counts.get("first.last", 0) + 1
            elif '_' in local_part:
                format_counts["first_last"] = format_counts.get("first_last", 0) + 1
            elif len(local_part) > 3:
                if local_part[0].isalpha() and local_part[1:].isalpha():
                    if len(local_part) <= 10:  # Heuristic for firstlast
                        format_counts["firstlast"] = format_counts.get("firstlast", 0) + 1
                    else:
                        # Might be lastfirst
                        format_counts["lastfirst"] = format_counts.get("lastfirst", 0) + 1
                elif len(local_part) <= 6:  # Heuristic for first
                    format_counts["first"] = format_counts.get("first", 0) + 1
                else:
                    # Could be flast
                    format_counts["flast"] = format_counts.get("flast", 0) + 1
        
        if not format_counts:
            return {
                "primary_format": "first.last",
                "formats": ["first.last", "firstlast"],
                "confidence": 0.3,
                "sample_size": len(domain_emails)
            }
        
        # Find most common format
        primary_format = max(format_counts.items(), key=lambda x: x[1])[0]
        
        # Sort formats by frequency
        sorted_formats = sorted(format_counts.items(), key=lambda x: x[1], reverse=True)
        format_list = [f[0] for f in sorted_formats]
        
        # Calculate confidence
        total = sum(format_counts.values())
        confidence = format_counts[primary_format] / total if total > 0 else 0.3
        
        return {
            "primary_format": primary_format,
            "formats": format_list,
            "confidence": confidence,
            "sample_size": len(domain_emails)
        }
    
    def generate_email_variants(
        self,
        first_name: str,
        last_name: str,
        domain: str,
        formats: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate email variants based on name and formats.
        
        Args:
            first_name: First name
            last_name: Last name
            domain: Email domain
            formats: List of formats to use (default: use all formats)
            
        Returns:
            List of email variants with confidence scores
        """
        if not formats:
            formats = list(self.email_formats.keys())
        
        # Clean names
        first = first_name.lower().strip()
        last = last_name.lower().strip()
        
        # Remove special characters
        first = re.sub(r'[^a-z0-9]', '', first)
        last = re.sub(r'[^a-z0-9]', '', last)
        
        variants = []
        base_confidence = 1.0
        confidence_decay = 0.8  # Confidence decreases for less likely formats
        
        for i, format_name in enumerate(formats):
            if format_name in self.email_formats:
                try:
                    local_part = self.email_formats[format_name](first, last)
                    email = f"{local_part}@{domain}"
                    confidence = base_confidence * (confidence_decay ** i)
                    
                    variants.append({
                        "email": email,
                        "format": format_name,
                        "confidence": round(confidence, 2)
                    })
                except Exception as e:
                    logger.error(f"Error generating email for format {format_name}: {str(e)}")
        
        return variants
    
    async def predict_email(
        self,
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
        
        # Analyze company emails to determine format
        format_analysis = self.analyze_company_emails(known_emails)
        
        # Generate email variants
        variants = self.generate_email_variants(
            first_name=first_name,
            last_name=last_name,
            domain=company_domain,
            formats=format_analysis["formats"]
        )
        
        return {
            "predictions": variants,
            "first_name": first_name,
            "last_name": last_name,
            "company_domain": company_domain,
            "format_analysis": format_analysis
        }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Perform simple email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            Dictionary with validation results
        """
        # Basic format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        format_valid = bool(re.match(email_pattern, email))
        
        if not format_valid:
            return {
                "email": email,
                "valid": False,
                "reason": "Invalid email format"
            }
        
        # In a production environment, you would implement more sophisticated validation:
        # 1. DNS MX record check
        # 2. SMTP verification
        # 3. API verification with services like Hunter.io or Clearbit
        
        # This is a simplified implementation
        domain = email.split('@')[1]
        
        return {
            "email": email,
            "valid": True,
            "disposable": self._is_disposable_domain(domain),
            "free_provider": self._is_free_provider(domain),
            "corporate": not self._is_free_provider(domain) and not self._is_disposable_domain(domain)
        }
    
    def _is_disposable_domain(self, domain: str) -> bool:
        """Check if domain is a disposable email provider"""
        disposable_domains = [
            'mailinator.com', 'tempmail.com', 'temp-mail.org', 'guerrillamail.com',
            'throwawaymail.com', 'yopmail.com', '10minutemail.com'
        ]
        return domain.lower() in disposable_domains
    
    def _is_free_provider(self, domain: str) -> bool:
        """Check if domain is a free email provider"""
        free_providers = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
            'protonmail.com', 'mail.com', 'zoho.com', 'icloud.com', 'gmx.com'
        ]
        return domain.lower() in free_providers


def batch_predict_emails(
    leads: List[Dict[str, Any]],
    company_emails: Dict[str, List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Predict emails for multiple leads.
    
    Args:
        leads: List of lead data
        company_emails: Dictionary mapping company domains to known emails
        
    Returns:
        List of leads with predicted emails
    """
    if not company_emails:
        company_emails = {}
    
    predictor = EmailPredictor()
    
    results = []
    for lead in tqdm(leads, desc="Predicting emails"):
        try:
            first_name = lead.get('first_name', '')
            last_name = lead.get('last_name', '')
            company = lead.get('company', '')
            
            # Get company domain
            company_domain = lead.get('company_domain', '')
            if not company_domain and company:
                # In production, you would use a service to lookup the domain
                # For demo, we'll use a simplified approach
                company_domain = company.lower().replace(' ', '') + '.com'
            
            # Get known emails for this company
            known_emails = company_emails.get(company_domain, [])
            
            # Predict email
            prediction = predictor.predict_email(
                first_name=first_name,
                last_name=last_name,
                company_domain=company_domain,
                known_emails=known_emails
            )
            
            # Get top prediction
            if prediction['predictions']:
                top_prediction = prediction['predictions'][0]
                lead['predicted_email'] = top_prediction['email']
                lead['email_confidence'] = top_prediction['confidence']
                lead['email_format'] = top_prediction['format']
            
            results.append(lead)
            
        except Exception as e:
            logger.error(f"Error predicting email for lead {lead.get('id')}: {str(e)}")
            results.append(lead)
    
    return results


if __name__ == "__main__":
    # Test email prediction
    predictor = EmailPredictor()
    
    # Test case 1: No known emails
    prediction1 = predictor.predict_email(
        first_name="John",
        last_name="Smith",
        company_domain="example.com"
    )
    
    print("Prediction with no known emails:")
    for pred in prediction1['predictions'][:3]:
        print(f"- {pred['email']} (confidence: {pred['confidence']})")
    
    # Test case 2: With known emails
    known_emails = [
        "jane.doe@acme.com",
        "john.williams@acme.com",
        "sarah.johnson@acme.com"
    ]
    
    prediction2 = predictor.predict_email(
        first_name="Michael",
        last_name="Brown",
        company_domain="acme.com",
        known_emails=known_emails
    )
    
    print("\nPrediction with known emails (first.last format):")
    for pred in prediction2['predictions'][:3]:
        print(f"- {pred['email']} (confidence: {pred['confidence']})")
    
    # Test validation
    print("\nEmail validation:")
    print(predictor.validate_email("test@example.com"))
    print(predictor.validate_email("invalid-email"))
    print(predictor.validate_email("test@gmail.com"))
