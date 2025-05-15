import re
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional, Set
import logging
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from user_agent import generate_user_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scrape_website_contact_data(
    domain: str,
    company_name: Optional[str] = None,
    max_pages: int = 20,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Scrape a company website for contact information and potential leads.
    
    Args:
        domain: Website domain to scrape
        company_name: Name of the company (optional)
        max_pages: Maximum number of pages to crawl
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with scraped contact information and potential leads
    """
    logger.info(f"Starting website scrape for domain: {domain}")
    
    # Ensure domain has proper URL format
    if not domain.startswith('http'):
        domain = f'https://{domain}'
        
    # Parse domain
    parsed_domain = urlparse(domain)
    base_domain = parsed_domain.netloc
    
    # Use company name from domain if not provided
    if not company_name:
        company_name = base_domain.split('.')[0].title()
        
    # Initialize results
    results = {
        'company': company_name,
        'domain': base_domain,
        'contacts': [],
        'team_page_url': None,
        'contact_page_url': None,
        'about_page_url': None,
        'social_links': {},
        'emails': set(),
        'phone_numbers': set()
    }
    
    # Queue of URLs to visit
    to_visit = [domain]
    visited = set()
    
    # Identify key pages (about, team, contact)
    key_page_patterns = {
        'team_page_url': [r'/team', r'/about-us/team', r'/people', r'/our-team', r'/staff'],
        'contact_page_url': [r'/contact', r'/contact-us', r'/get-in-touch'],
        'about_page_url': [r'/about', r'/about-us', r'/company']
    }
    
    # Set up async HTTP session
    async with aiohttp.ClientSession() as session:
        # Process URLs until queue is empty or we reach max_pages
        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
                
            visited.add(current_url)
            
            try:
                # Generate random user agent
                headers = {'User-Agent': generate_user_agent()}
                
                # Make request
                async with session.get(current_url, headers=headers, timeout=timeout) as response:
                    if response.status != 200:
                        continue
                        
                    # Parse HTML
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Check if this is a key page
                    for page_type, patterns in key_page_patterns.items():
                        if not results[page_type]:
                            for pattern in patterns:
                                if re.search(pattern, current_url, re.IGNORECASE):
                                    results[page_type] = current_url
                                    break
                    
                    # Extract contact information
                    extract_contact_info(soup, results)
                    
                    # Extract social links
                    extract_social_links(soup, results)
                    
                    # Extract team members if this is a team page
                    if results['team_page_url'] == current_url:
                        extract_team_members(soup, results)
                    
                    # Find links to other pages on the same domain
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        
                        # Make absolute URL
                        if not href.startswith('http'):
                            href = urljoin(current_url, href)
                            
                        # Check if URL is on the same domain
                        if urlparse(href).netloc == base_domain and href not in visited and href not in to_visit:
                            to_visit.append(href)
                            
            except Exception as e:
                logger.error(f"Error scraping {current_url}: {str(e)}")
    
    # Convert sets to lists for JSON serialization
    results['emails'] = list(results['emails'])
    results['phone_numbers'] = list(results['phone_numbers'])
    
    logger.info(f"Website scrape complete for {domain}, found {len(results['emails'])} emails and {len(results['contacts'])} potential contacts")
    
    return results


def extract_contact_info(soup: BeautifulSoup, results: Dict[str, Any]) -> None:
    """Extract contact information from a webpage"""
    # Extract emails
    content = soup.get_text()
    
    # Find emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, content)
    for email in emails:
        results['emails'].add(email.lower())
    
    # Find phone numbers
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, content)
    for phone in phones:
        results['phone_numbers'].add(phone)


def extract_social_links(soup: BeautifulSoup, results: Dict[str, Any]) -> None:
    """Extract social media links"""
    social_patterns = {
        'linkedin': r'linkedin\.com',
        'twitter': r'twitter\.com',
        'facebook': r'facebook\.com',
        'instagram': r'instagram\.com'
    }
    
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        for platform, pattern in social_patterns.items():
            if re.search(pattern, href, re.IGNORECASE):
                results['social_links'][platform] = href
                break


def extract_team_members(soup: BeautifulSoup, results: Dict[str, Any]) -> None:
    """Extract team members information from a team page"""
    # This is a simplified approach that would be enhanced in production
    
    # Look for common team member containers
    member_containers = soup.select('.team-member, .employee, .staff, .person, .profile')
    
    if not member_containers:
        # Try looking for other common patterns
        member_containers = soup.find_all(['div', 'li'], class_=lambda c: c and any(
            x in str(c).lower() for x in ['team', 'member', 'employee', 'staff', 'profile']
        ))
    
    for container in member_containers:
        try:
            # Try to extract name
            name_elem = container.find(['h2', 'h3', 'h4', 'strong', 'b'])
            name = name_elem.text.strip() if name_elem else None
            
            if not name:
                continue
                
            # Try to extract title
            title = None
            p_tags = container.find_all('p')
            for p in p_tags:
                text = p.text.strip()
                if text and text != name and len(text) < 100:
                    title = text
                    break
            
            # Try to extract email
            email = None
            email_elem = container.find('a', href=lambda h: h and 'mailto:' in h)
            if email_elem:
                email = email_elem['href'].replace('mailto:', '').strip()
                results['emails'].add(email.lower())
            
            # Split name into first and last name
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Add to contacts
            results['contacts'].append({
                'first_name': first_name,
                'last_name': last_name,
                'title': title,
                'company': results['company'],
                'email': email,
                'source': 'website'
            })
            
        except Exception as e:
            logger.error(f"Error extracting team member: {str(e)}")


async def predict_email_format(
    domain: str,
    known_emails: List[str]
) -> Dict[str, Any]:
    """
    Predict the email format used by a company based on known emails.
    
    Args:
        domain: Company domain
        known_emails: List of known email addresses from the company
        
    Returns:
        Predicted email format
    """
    if not known_emails:
        # Default formats to try
        return {
            'primary_format': 'first.last',
            'formats': [
                'first.last',
                'firstlast',
                'first_last',
                'flast',
                'first',
                'first.last.initial'
            ],
            'confidence': 0.3
        }
    
    formats = {}
    
    for email in known_emails:
        # Only process emails from the target domain
        if not email.endswith(f'@{domain}'):
            continue
            
        local_part = email.split('@')[0].lower()
        
        # Try to identify format
        format_type = None
        
        if '.' in local_part:
            parts = local_part.split('.')
            if len(parts) == 2:
                format_type = 'first.last'
            elif len(parts) > 2 and len(parts[-1]) == 1:
                format_type = 'first.last.initial'
        elif '_' in local_part:
            format_type = 'first_last'
        elif local_part[0].isalpha() and len(local_part) > 2:
            if local_part[1:].isalpha():
                format_type = 'firstlast'
            else:
                format_type = 'flast'
        
        if format_type:
            formats[format_type] = formats.get(format_type, 0) + 1
    
    if not formats:
        return {
            'primary_format': 'first.last',
            'formats': ['first.last', 'firstlast'],
            'confidence': 0.3
        }
    
    # Find most common format
    primary_format = max(formats.items(), key=lambda x: x[1])[0]
    
    # Sort formats by frequency
    sorted_formats = sorted(formats.items(), key=lambda x: x[1], reverse=True)
    format_list = [f[0] for f in sorted_formats]
    
    # Calculate confidence
    total = sum(formats.values())
    confidence = formats[primary_format] / total if total > 0 else 0.3
    
    return {
        'primary_format': primary_format,
        'formats': format_list,
        'confidence': confidence
    }
