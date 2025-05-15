import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
import logging
import json

# For demo purposes, using pyppeteer, in production might use Playwright
from pyppeteer import launch
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scrape_linkedin_profiles(
    search_url: str,
    max_results: int = 100,
    headless: bool = True
) -> List[Dict[str, Any]]:
    """
    Scrape LinkedIn profiles from search results.
    
    Args:
        search_url: LinkedIn search URL
        max_results: Maximum number of profiles to scrape
        headless: Run browser in headless mode
        
    Returns:
        List of scraped profiles
    """
    logger.info(f"Starting LinkedIn scrape for URL: {search_url}")
    
    # Launch browser
    browser = await launch(
        headless=headless,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    )
    
    try:
        page = await browser.newPage()
        
        # Set random user agent
        user_agent = generate_user_agent()
        await page.setUserAgent(user_agent)
        
        # Set viewport size
        await page.setViewport({'width': 1280, 'height': 800})
        
        # Navigate to search URL
        await page.goto(search_url)
        
        # Handle LinkedIn login if needed (would require credentials in production)
        if await page.querySelector('input#username') is not None:
            logger.warning("LinkedIn login required but not implemented in demo")
            return []
            
        # Wait for search results to load
        await page.waitForSelector('.search-result__info', {'timeout': 10000})
        
        profiles = []
        page_num = 1
        
        # Iterate through search result pages
        while len(profiles) < max_results:
            # Extract profile data from current page
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find profile cards
            profile_cards = soup.select('.search-result__info')
            
            if not profile_cards:
                logger.info("No more profiles found")
                break
                
            # Process profile cards
            for card in profile_cards:
                if len(profiles) >= max_results:
                    break
                
                profile_data = extract_profile_from_card(card)
                if profile_data:
                    profiles.append(profile_data)
                    
            # Check if there's a next page
            next_button = await page.querySelector('.artdeco-pagination__button--next:not(.artdeco-pagination__button--disabled)')
            if next_button:
                logger.info(f"Navigating to page {page_num + 1}")
                await next_button.click()
                await page.waitForNavigation()
                page_num += 1
                
                # Add random delay to avoid detection
                await asyncio.sleep(random.uniform(3, 7))
            else:
                logger.info("No more pages available")
                break
                
        logger.info(f"Scraped {len(profiles)} LinkedIn profiles")
        return profiles
        
    except Exception as e:
        logger.error(f"Error scraping LinkedIn: {str(e)}")
        return []
        
    finally:
        await browser.close()


def extract_profile_from_card(card) -> Optional[Dict[str, Any]]:
    """Extract profile information from a LinkedIn search result card"""
    try:
        # Get name
        name_elem = card.select_one('.actor-name')
        name = name_elem.text.strip() if name_elem else None
        
        # Get profile URL
        profile_link = card.select_one('a.search-result__result-link')
        profile_url = profile_link['href'] if profile_link else None
        
        # Get title
        title_elem = card.select_one('.subline-level-1')
        title = title_elem.text.strip() if title_elem else None
        
        # Get company
        company_elem = card.select_one('.subline-level-2')
        company = company_elem.text.strip() if company_elem else None
        
        # Get location
        location_elem = card.select_one('.subline-level-3')
        location = location_elem.text.strip() if location_elem else None
        
        if not name or not profile_url:
            return None
            
        # Split name into first and last name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'title': title,
            'company': company,
            'location': location,
            'linkedin_url': profile_url,
            'source': 'linkedin'
        }
        
    except Exception as e:
        logger.error(f"Error extracting profile data: {str(e)}")
        return None


async def enrich_linkedin_profile(profile_url: str) -> Dict[str, Any]:
    """
    Enrich a LinkedIn profile with additional information.
    
    Args:
        profile_url: URL to LinkedIn profile
        
    Returns:
        Enriched profile data
    """
    # This would be implemented with a more sophisticated approach in production
    # For demo purposes, we'll return some mock data
    
    return {
        'education': [
            {'school': 'Example University', 'degree': 'Bachelor of Science', 'field': 'Computer Science', 'dates': '2010-2014'}
        ],
        'experience': [
            {'company': 'Example Corp', 'title': 'Senior Developer', 'dates': '2018-Present'},
            {'company': 'Previous Inc', 'title': 'Developer', 'dates': '2014-2018'}
        ],
        'skills': ['Python', 'JavaScript', 'Machine Learning', 'Data Analysis'],
        'languages': ['English', 'Spanish'],
        'connections': '500+'
    }
