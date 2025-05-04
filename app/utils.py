import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_text_from_url(url: str, timeout: int = 10) -> Optional[str]:
    """
    Extract main text content from a URL (e.g., job description)
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text or None if failed
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Fetch content
        headers = {
            'User-Agent': 'SHL-Assessment-Recommender/1.0'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe']):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text if text else None
        
    except Exception as e:
        logger.warning(f"Failed to extract text from URL {url}: {str(e)}")
        return None